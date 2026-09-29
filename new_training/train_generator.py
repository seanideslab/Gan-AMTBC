"""Train a NEW, limited AMBTC bitmap-preserving quantization-compensation candidate.
Does NOT reproduce paper's PPO-DQN-GAN/SRNet results or replace published figures.
"""
from __future__ import annotations
import argparse,hashlib,json,random,time,shutil,datetime
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader
from torch.nn import functional as F
from ambtc import encode,reconstruct,embed,extract,plan_loads,corrected_reconstruct,psnr
from data import ImageDataset,make_manifest,sha
from models import CandidateAttentionResUNet,count_parameters


def make_pair(x,hashes,target,seed,key='new-reconstruction-v1'):
    bm,hi,lo=encode(x)
    stego=[];loads_all=[];secrets=[]
    for j in range(x.shape[0]):
        _,bh,bw,_,_=bm.shape
        score=(hi[j]-lo[j]).detach().flatten().tolist()
        loads=plan_loads(bh*bw,target,scores=score)
        message_seed=int.from_bytes(hashlib.sha256(f'{hashes[j]}:{seed}:{target}'.encode()).digest()[:8],'big')%(2**63-1)
        g=torch.Generator().manual_seed(message_seed)
        msg=torch.randint(0,2,(sum(loads),),generator=g,dtype=torch.uint8)
        sbm=embed(bm[j:j+1],msg.to(x.device),loads,sample_id=hashes[j],key=key)
        if not torch.equal(extract(sbm,loads,sample_id=hashes[j],key=key),msg):
            raise RuntimeError('Payload extraction failure')
        stego.append(sbm);loads_all.append(loads);secrets.append(msg)
    sbm=torch.cat(stego,0)
    return sbm,hi,lo,loads_all,secrets


def run_epoch(model,loader,optimizer,epoch,device,targets,max_delta,limit_batches=None,accumulate=1):
    is_train=optimizer is not None;model.train(is_train)
    sums={'loss':0.,'baseline_mse':0.,'corrected_mse':0.,'achieved_bpp':0.,'bit_errors':0,'samples':0}
    context=torch.enable_grad() if is_train else torch.no_grad()
    n_batches=min(len(loader),limit_batches) if limit_batches is not None else len(loader)
    if is_train: optimizer.zero_grad(set_to_none=True)
    with context:
        for batch,(x,ids) in enumerate(loader):
            if limit_batches is not None and batch>=limit_batches:break
            x=x.to(device)
            target=targets[(epoch+batch)%len(targets)]
            bm,hi,lo=encode(x)
            target_cover=reconstruct(bm,hi,lo).detach()
            sbm,hi,lo,loads,secrets=make_pair(x,ids,target,epoch*1_000_000+batch)
            baseline=reconstruct(sbm,hi,lo)
            correction=model(baseline)
            restored,hh,ll=corrected_reconstruct(sbm,hi,lo,correction,max_delta=max_delta)
            distortion=F.mse_loss(restored,target_cover)
            penalty=correction.square().mean()*.001
            loss=distortion+penalty
            if is_train:
                group_count=min(accumulate,n_batches-(batch//accumulate)*accumulate)
                (loss/group_count).backward()
                if (batch+1)%accumulate==0 or batch+1==n_batches:
                    torch.nn.utils.clip_grad_norm_(model.parameters(),1.)
                    optimizer.step();optimizer.zero_grad(set_to_none=True)
            n=x.shape[0]
            sums['loss']+=loss.detach().item()*n
            sums['baseline_mse']+=F.mse_loss(baseline,target_cover).detach().item()*n
            sums['corrected_mse']+=distortion.detach().item()*n
            sums['achieved_bpp']+=sum(map(sum,loads))/(x.shape[-1]*x.shape[-2])
            sums['samples']+=n
    if sums['samples']==0:raise ValueError('No batches ran')
    out={k:(v/sums['samples'] if k not in ('samples','bit_errors') else v) for k,v in sums.items()}
    return out


def fixed_validation_config(loader,device,targets,limit_batches=None):
    """Fingerprint actual per-image loads/messages, independent of model weights."""
    records=[]
    with torch.no_grad():
        for target in targets:
            for batch,(x,ids) in enumerate(loader):
                if limit_batches is not None and batch>=limit_batches:break
                sbm,_,_,loads,secrets=make_pair(x.to(device),ids,target,batch)
                for j,sample_id in enumerate(ids):
                    records.append({'image_sha256':sample_id,'target_bpp':target,'batch':batch,
                                    'pair_seed':batch,'embedding_key':'new-reconstruction-v1',
                                    'loads':loads[j],
                                    'secret_sha256':hashlib.sha256(secrets[j].numpy().tobytes()).hexdigest(),
                                    'stego_bitmap_sha256':hashlib.sha256(sbm[j].cpu().numpy().tobytes()).hexdigest()})
    digest=hashlib.sha256(json.dumps(records,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return {'sha256':digest,'epoch_argument':0,'targets':list(targets),'items':records}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data-root',required=True)
    ap.add_argument('--output-dir',required=True)
    ap.add_argument('--manifest',default=None)
    ap.add_argument('--resume',default=None,help='Resume a matching NEW checkpoint; never use original/unverified weights')
    ap.add_argument('--epochs',type=int,default=200)
    ap.add_argument('--batch-size',type=int,default=16)
    ap.add_argument('--accumulate',type=int,default=1,help='Gradient accumulation; effective batch=batch-size*accumulate')
    ap.add_argument('--size',type=int,default=256,choices=[32,64,128,256,512])
    ap.add_argument('--base',type=int,default=50)
    ap.add_argument('--seed',type=int,default=42)
    ap.add_argument('--lr',type=float,default=1e-4)
    ap.add_argument('--max-delta',type=float,default=.08)
    ap.add_argument('--targets',type=float,nargs='+',default=[.1,.2,.4])
    ap.add_argument('--smoke',action='store_true')
    ap.add_argument('--max-batches',type=int,default=None)
    a=ap.parse_args()
    if a.epochs<1 or a.batch_size<1 or a.accumulate<1:raise ValueError('Need positive epochs/batch/accumulate')
    if not a.smoke and a.max_batches is not None:raise ValueError('--max-batches only for --smoke')
    torch.set_num_threads(min(4,torch.get_num_threads()))
    random.seed(a.seed);np.random.seed(a.seed);torch.manual_seed(a.seed)
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    manifest=Path(a.manifest) if a.manifest else out/'NEW_manifest.json'
    if not manifest.exists():make_manifest(a.data_root,manifest,seed=a.seed,smoke=a.smoke)
    manifest_hash=sha(manifest)
    tr=ImageDataset(manifest,'train',a.size)
    va=None
    try:va=ImageDataset(manifest,'val',a.size)
    except ValueError:pass
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model=CandidateAttentionResUNet(a.base).to(device)
    optimizer=torch.optim.Adam(model.parameters(),lr=a.lr)
    vloader=DataLoader(va,batch_size=a.batch_size,shuffle=False,num_workers=0) if va else None
    if vloader is None:raise ValueError('Fixed validation requires a nonempty validation split')
    meta={'status':'NEW_INDEPENDENT_RECONSTRUCTION','smoke_only':a.smoke,
          'not_original_checkpoint':True,'no_security_detector':True,'model':'CandidateAttentionResUNet',
          'model_base':a.base,'parameters':count_parameters(model),'source_note':'unverified 50-base Attention ResUNet shape summary',
          'manifest_sha256':manifest_hash,'manifest_file':str(manifest),'image_size':a.size,
          'epochs_requested':a.epochs,'batch_size':a.batch_size,'gradient_accumulation':a.accumulate,
          'effective_batch_size':a.batch_size*a.accumulate,'seed':a.seed,'lr':a.lr,
          'targets':a.targets,'max_delta':a.max_delta,'device':str(device),
          'training_objective':'AMBTC-only cover vs bitmap-preserving stego recon MSE; no steganalysis loss',
          'validation_protocol':'FIXED_VALIDATION','fixed_val_epoch':0,'fixed_val_targets':[.2,.4],
          'experiment_label':'NEW_INDEPENDENT_RECONSTRUCTION / SMOKE_ONLY / FIXED_VALIDATION'}
    start_epoch=0
    if a.resume:
        previous=torch.load(a.resume,map_location='cpu',weights_only=True)
        old=previous.get('meta',{})
        critical=('status','smoke_only','manifest_sha256','image_size','model_base','targets','max_delta','seed','batch_size','gradient_accumulation')
        if any(old.get(k)!=meta.get(k) for k in critical):
            raise ValueError('Resume checkpoint metadata differs from requested run')
        model.load_state_dict(previous['state_dict'],strict=True)
        optimizer.load_state_dict(previous['optimizer_state_dict'])
        start_epoch=int(previous['epoch_completed'])
        if start_epoch>=a.epochs:raise ValueError('Resume checkpoint already meets requested total epochs')
        if 'torch_rng_state' in previous:torch.set_rng_state(previous['torch_rng_state'])
    (out/'training_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
    log_mode='a' if a.resume else 'w'
    best_score=float('inf');best_epoch=None
    if a.resume:
        best_score=float(previous.get('best_score',float('inf')))
        best_epoch=previous.get('best_epoch')
    # Extra validation loader iterations must not change training RNG progression.
    rng_state=torch.get_rng_state()
    fixed_config=fixed_validation_config(vloader,device,(.2,.4),a.max_batches)
    torch.set_rng_state(rng_state)
    (out/'fixed_validation_config.json').write_text(json.dumps(fixed_config,indent=2),encoding='utf8')
    with (out/'training_log.jsonl').open(log_mode) as log:
        for ep in range(start_epoch,a.epochs):
            # Each epoch has its own deterministic shuffled order, allowing exact resume.
            loader=DataLoader(tr,batch_size=a.batch_size,shuffle=True,
                              generator=torch.Generator().manual_seed(a.seed+ep),num_workers=0)
            t=time.time()
            res=run_epoch(model,loader,optimizer,ep,device,a.targets,a.max_delta,a.max_batches,a.accumulate)
            val=run_epoch(model,vloader,None,ep,device,a.targets,a.max_delta,a.max_batches) if vloader else None
            rng_state=torch.get_rng_state()
            fixed_val={str(target):run_epoch(model,vloader,None,0,device,[target],a.max_delta,a.max_batches)
                       for target in (.2,.4)}
            current_config=fixed_validation_config(vloader,device,(.2,.4),a.max_batches)
            torch.set_rng_state(rng_state)
            if current_config['sha256']!=fixed_config['sha256']:
                raise RuntimeError('Fixed validation message/load configuration changed')
            fixed_score=sum(v['corrected_mse'] for v in fixed_val.values())/2
            is_best=fixed_score<best_score
            if is_best:best_score=fixed_score;best_epoch=ep+1
            record={'epoch':ep+1,'train':res,'validation':val,'fixed_val':fixed_val,
                    'fixed_score':fixed_score,'best_epoch':best_epoch,'is_best_so_far':is_best,
                    'fixed_validation_config_sha256':current_config['sha256'],
                    'seconds':round(time.time()-t,3),'status':meta['status'],
                    'experiment_label':meta['experiment_label']}
            log.write(json.dumps(record)+'\n');log.flush()
            print(json.dumps(record),flush=True)
            # Latest checkpoint and metadata every epoch; safe weights-only loading.
            ckpt={'state_dict':{k:v.detach().cpu() for k,v in model.state_dict().items()},
                  'meta':meta,'epoch_completed':ep+1,'optimizer_state_dict':optimizer.state_dict(),
                  'torch_rng_state':torch.get_rng_state(),'fixed_val':fixed_val,'fixed_score':fixed_score,
                  'best_score':best_score,'best_epoch':best_epoch,
                  'fixed_validation_config_sha256':current_config['sha256']}
            temp=out/'checkpoint_latest.tmp';torch.save(ckpt,temp);temp.replace(out/'checkpoint_latest.pth')
            epoch_path=out/f'checkpoint_epoch_{ep+1:03d}.pth'
            shutil.copyfile(out/'checkpoint_latest.pth',epoch_path)
            if is_best:
                shutil.copyfile(epoch_path,out/'checkpoint_best.pth')
                selection={'experiment_label':meta['experiment_label'],'best_epoch':best_epoch,
                           'fixed_score':fixed_score,'checkpoint_sha256':sha(out/'checkpoint_best.pth'),
                           'manifest_sha256':manifest_hash,'fixed_validation_config_sha256':current_config['sha256'],
                           'criterion':'Minimum mean fixed validation corrected_mse over 0.2 and 0.4; strict <, earliest tie',
                           'holdout_used_for_selection':False,
                           'selected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
                (out/'best_selection.json').write_text(json.dumps(selection,indent=2),encoding='utf8')
    (out/'TRAINING_COMPLETE.txt').write_text('NEW reconstruction only; NOT the original manuscript model.\n')

if __name__=='__main__':main()
