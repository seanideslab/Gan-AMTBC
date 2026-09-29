"""NEW PPO *quality-and-budget-only* experiment, without trained steganalysis detector or DQN.
A generated checkpoint is never evidence that paper's security reward was reconstructed.
"""
from __future__ import annotations
import argparse,json,random,time
from pathlib import Path
import numpy as np, torch
from torch import nn
from torch.utils.data import DataLoader
from torch.distributions import Categorical
from ambtc import encode,reconstruct
from data import ImageDataset,make_manifest,sha
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'recovery'))
from architecture_scaffold import ActorCriticScaffold,ACTIONS_BITS_PER_BLOCK


def rollout(model,x,target):
    with torch.no_grad():
        bm,hi,lo=encode(x)
        block=x.unfold(2,4,4).unfold(3,4,4)[:,0]
        variance=block.var((-2,-1),unbiased=False)
        states=torch.stack((hi-lo,4*variance),dim=-1).reshape(-1,2).detach()
        logits,values=model(states)
        dist=Categorical(logits=logits)
        actions=dist.sample();old_logprob=dist.log_prob(actions)
        bits=torch.tensor(ACTIONS_BITS_PER_BLOCK,device=x.device,dtype=torch.float32)[actions]
        flatbm=bm.reshape(-1,16)
        # Randomized, unique per-block embedding-position candidates for honest distortion reward.
        ranks=torch.rand(flatbm.shape,device=x.device).argsort(dim=1).argsort(dim=1)
        mask=(ranks<bits[:,None]).float()
        msg=torch.randint(0,2,flatbm.shape,device=x.device,dtype=torch.float32)
        changed=(1-mask)*flatbm+mask*msg
        delta=(hi-lo).reshape(-1,1)
        block_mse=(((changed-flatbm)*delta)**2).mean(dim=1)
        # Sequential running budget penalty; deliberately excludes security reward.
        running=bits.cumsum(0)/torch.arange(1,len(bits)+1,device=x.device)
        reward=0.05*bits/8. - 4.*block_mse - .1*(running-16*target).square()
        # Contextual PPO return with immediate quality/budget reward and zero terminal bootstrap.
        returns=reward
        advantages=returns-values
        return states,actions,old_logprob,returns,advantages,bits.mean().item()/16.,block_mse.mean().item()


def update(model,opt,roll,epochs=3,epsilon=.2):
    states,actions,oldlp,returns,adv,_,_=roll
    adv=(adv-adv.mean())/(adv.std(unbiased=False)+1e-6)
    losses=[]
    for _ in range(epochs):
        logits,values=model(states)
        lp=Categorical(logits=logits).log_prob(actions)
        ratio=(lp-oldlp).exp()
        policy_loss=-torch.minimum(ratio*adv,ratio.clamp(1-epsilon,1+epsilon)*adv).mean()
        value_loss=(values-returns).square().mean()
        loss=policy_loss+.5*value_loss
        opt.zero_grad(set_to_none=True);loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1.)
        opt.step();losses.append(loss.detach().item())
    return sum(losses)/len(losses)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--data-root',required=True);p.add_argument('--output-dir',required=True)
    p.add_argument('--manifest',default=None);p.add_argument('--size',type=int,default=64)
    p.add_argument('--epochs',type=int,default=200);p.add_argument('--seed',type=int,default=42)
    p.add_argument('--target-bpp',type=float,default=.2);p.add_argument('--smoke',action='store_true')
    p.add_argument('--max-images',type=int,default=None)
    a=p.parse_args()
    torch.set_num_threads(min(4,torch.get_num_threads()))
    if not a.smoke and a.max_images is not None:raise ValueError('--max-images only for --smoke')
    if not (0<a.target_bpp<=.5):raise ValueError('Invalid target')
    random.seed(a.seed);np.random.seed(a.seed);torch.manual_seed(a.seed)
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    manifest=Path(a.manifest) if a.manifest else out/'NEW_manifest.json'
    if not manifest.exists():make_manifest(a.data_root,manifest,seed=a.seed,smoke=a.smoke)
    ds=ImageDataset(manifest,'train',a.size)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model=ActorCriticScaffold(shared_backbone=True).to(device)
    opt=torch.optim.Adam(model.parameters(),lr=3e-4)
    meta={'status':'NEW_QUALITY_BUDGET_PPO_ONLY','smoke_only':a.smoke,
          'not_original_checkpoint':True,'security_reward':False,'dqn_trained':False,
          'architecture':'ActorCriticScaffold shared 256x256','manifest_sha256':sha(manifest),
          'image_size':a.size,'target_bpp':a.target_bpp,'seed':a.seed,'epochs_requested':a.epochs}
    (out/'training_metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf8')
    with (out/'training_log.jsonl').open('w') as f:
        for ep in range(a.epochs):
            order=torch.randperm(len(ds)).tolist()
            if a.max_images:order=order[:a.max_images]
            for i in order:
                x,_=ds[i];x=x.unsqueeze(0).to(device)
                roll=rollout(model,x,a.target_bpp)
                loss=update(model,opt,roll)
                record={'epoch':ep+1,'image_index':i,'loss':loss,
                        'achieved_policy_bpp':roll[-2],'block_mse':roll[-1],
                        'status':meta['status']}
                f.write(json.dumps(record)+'\n');f.flush()
            ckpt={'state_dict':{k:v.detach().cpu() for k,v in model.state_dict().items()},
                  'meta':meta,'epoch_completed':ep+1,'optimizer_state_dict':opt.state_dict()}
            tmp=out/'checkpoint_latest.tmp';torch.save(ckpt,tmp);tmp.replace(out/'checkpoint_latest.pth')
            print(json.dumps(record),flush=True)

if __name__=='__main__':main()
