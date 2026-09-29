"""Fresh holdout evaluation of NEW reconstruction only. No security/detection metric."""
from __future__ import annotations
import argparse,csv,json,math,hashlib
from pathlib import Path
import torch
from torch.utils.data import DataLoader
from ambtc import encode,reconstruct,embed,extract,plan_loads,corrected_reconstruct,psnr
from data import ImageDataset,sha
from models import CandidateAttentionResUNet


def load_ckpt(path,allow_smoke=False):
    ckpt=torch.load(path,map_location='cpu',weights_only=True)
    meta=ckpt.get('meta',{})
    if meta.get('status')!='NEW_INDEPENDENT_RECONSTRUCTION':raise ValueError('Unknown model provenance')
    if meta.get('smoke_only') and not allow_smoke:raise ValueError('Smoke weights require --allow-smoke')
    m=CandidateAttentionResUNet(meta['model_base'])
    m.load_state_dict(ckpt['state_dict'],strict=True)
    m.eval()
    return m,meta


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--manifest',required=True);p.add_argument('--checkpoint',required=True)
    p.add_argument('--out',required=True);p.add_argument('--target-bpp',type=float,default=.4)
    p.add_argument('--allow-smoke',action='store_true');p.add_argument('--max-images',type=int,default=None)
    a=p.parse_args()
    model,meta=load_ckpt(a.checkpoint,a.allow_smoke)
    if sha(a.manifest)!=meta['manifest_sha256']:
        raise ValueError('Manifest does not match training checkpoint; new evaluation must document a separate manifest')
    ds=ImageDataset(a.manifest,'test',meta['image_size'])
    rows=[]
    with torch.no_grad():
        for i in range(len(ds) if a.max_images is None else min(len(ds),a.max_images)):
            x,id_=ds[i];x=x.unsqueeze(0)
            bm,hi,lo=encode(x);cover_ambtc=reconstruct(bm,hi,lo)
            score=(hi-lo).flatten().tolist()
            nblock=len(score);loads=plan_loads(nblock,a.target_bpp,scores=score)
            seed=int.from_bytes(hashlib.sha256(f'eval:{id_}:{a.target_bpp}'.encode()).digest()[:8],'big')%(2**63-1)
            g=torch.Generator().manual_seed(seed)
            message=torch.randint(0,2,(sum(loads),),generator=g,dtype=torch.uint8)
            sbm=embed(bm,message,loads,sample_id=id_)
            recovered=extract(sbm,loads,sample_id=id_)
            baseline=reconstruct(sbm,hi,lo)
            out,hh,ll=corrected_reconstruct(sbm,hi,lo,model(baseline),max_delta=meta['max_delta'])
            rows.append({'image_sha256':id_,'requested_bpp':a.target_bpp,
                         'achieved_bpp':sum(loads)/(x.shape[-1]*x.shape[-2]),
                         'embedded_bits':sum(loads),'bit_errors':int((message!=recovered).sum().item()),
                         'cover_ambtc_psnr_vs_raw':psnr(x,cover_ambtc),
                         'baseline_psnr_vs_ambtc':psnr(cover_ambtc,baseline),
                         'corrected_psnr_vs_ambtc':psnr(cover_ambtc,out),
                         'baseline_psnr_vs_raw':psnr(x,baseline),
                         'corrected_psnr_vs_raw':psnr(x,out),
                         'baseline_mse_vs_ambtc':(baseline-cover_ambtc).square().mean().item(),
                         'corrected_mse_vs_ambtc':(out-cover_ambtc).square().mean().item(),
                         'experiment_label':meta.get('experiment_label',meta['status']),
                         'status':meta['status']})
    if not rows:raise ValueError('No test images')
    outpath=Path(a.out);outpath.parent.mkdir(parents=True,exist_ok=True)
    with outpath.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={'status':'NEW_INDEPENDENT_RECONSTRUCTION_EVALUATION','smoke_only':meta['smoke_only'],
             'n_images':len(rows),'checkpoint':str(Path(a.checkpoint).resolve()),
             'manifest_sha256':sha(a.manifest),'target_bpp':a.target_bpp,
             'mean_achieved_bpp':sum(r['achieved_bpp'] for r in rows)/len(rows),
             'total_bit_errors':sum(r['bit_errors'] for r in rows),
             'mean_corrected_psnr_vs_ambtc':sum(r['corrected_psnr_vs_ambtc'] for r in rows)/len(rows),
             'mean_baseline_psnr_vs_ambtc':sum(r['baseline_psnr_vs_ambtc'] for r in rows)/len(rows),
             'mean_baseline_mse_vs_ambtc':sum(r['baseline_mse_vs_ambtc'] for r in rows)/len(rows),
             'mean_corrected_mse_vs_ambtc':sum(r['corrected_mse_vs_ambtc'] for r in rows)/len(rows),
             'improved_images':sum(r['corrected_mse_vs_ambtc']<r['baseline_mse_vs_ambtc'] for r in rows),
             'checkpoint_sha256':sha(a.checkpoint),'epoch_completed':torch.load(a.checkpoint,map_location='cpu',weights_only=True)['epoch_completed'],
             'experiment_label':meta.get('experiment_label',meta['status']),
             'no_detection_metric':'No trained steganalysis detector available; P_E not estimated',
             'not_comparable_to_paper':True}
    outpath.with_suffix('.summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
