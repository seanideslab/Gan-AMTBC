"""NEW AMBTC embedding core; not recovered original GAN-PPO-AMBTC implementation.
Bit locations are deterministically seeded, unique within each 4x4 block.
This is a functional baseline, not a secure steganographic embedding protocol.
"""
from __future__ import annotations
import hashlib
import math
import torch


def encode(x: torch.Tensor):
    if x.ndim != 4 or x.shape[1] != 1 or x.shape[-2] % 4 or x.shape[-1] % 4:
        raise ValueError('Expected [B,1,H,W], H and W multiples of four')
    b, _, h, w = x.shape
    tiles = x.unfold(2, 4, 4).unfold(3, 4, 4).contiguous() # [B,1,bh,bw,4,4]
    means = tiles.mean((-2,-1), keepdim=True)
    bm = (tiles >= means).float()
    count1 = bm.sum((-2,-1))
    count0 = 16. - count1
    hi = (tiles*bm).sum((-2,-1))/count1.clamp(min=1.)
    lo = (tiles*(1.-bm)).sum((-2,-1))/count0.clamp(min=1.)
    hi = torch.where(count1>0,hi,means.flatten(-2).mean(-1))
    lo = torch.where(count0>0,lo,hi)
    return bm[:,0], hi[:,0], lo[:,0]


def reconstruct(bm:torch.Tensor, hi:torch.Tensor, lo:torch.Tensor):
    if bm.ndim!=5 or bm.shape[-2:]!=(4,4):
        raise ValueError('Expected bitmap [B,bh,bw,4,4]')
    p = bm*hi[...,None,None]+(1.-bm)*lo[...,None,None]
    b,bh,bw,_,_=p.shape
    return p.permute(0,1,3,2,4).reshape(b,1,bh*4,bw*4)


def features(x:torch.Tensor):
    bm,hi,lo=encode(x)
    blocks=x.unfold(2,4,4).unfold(3,4,4)[:,0]
    variance=blocks.var((-2,-1),unbiased=False)
    return torch.stack((hi-lo,variance),dim=-1)


def _position_matrix(sample_id:str, nblocks:int, key:str):
    """Deterministic NEW per-image random permutations; not the original C permutation."""
    seed=int.from_bytes(hashlib.sha256(f'{key}:{sample_id}:matrix-v1'.encode()).digest()[:8],'big')%(2**63-1)
    g=torch.Generator(device='cpu').manual_seed(seed)
    return torch.rand((nblocks,16),generator=g).argsort(dim=1)


def _flat_indices(loads,sample_id,key):
    counts=torch.tensor(loads,dtype=torch.long)
    nblocks=len(loads)
    if nblocks==0:return torch.zeros(0,dtype=torch.long),torch.zeros(0,dtype=torch.long)
    rows=torch.repeat_interleave(torch.arange(nblocks),counts)
    starts=torch.cumsum(counts,dim=0)-counts
    offsets=torch.arange(int(counts.sum()))-torch.repeat_interleave(starts,counts)
    positions=_position_matrix(sample_id,nblocks,key)[rows,offsets]
    return rows,positions


def plan_loads(nblocks:int,target_bpp:float,actions=(1,2,4,8), scores=None):
    """Budget-constrained NEW baseline. Uses 0 bits for unused blocks and caps at 8.
    This is not the original PPO inference: it enforces a target at image level.
    """
    if not (0 <= target_bpp <= .5): raise ValueError('Target bpp must be [0,.5]')
    cap=int(round(16*nblocks*target_bpp))
    if cap>8*nblocks: raise ValueError('Insufficient physical capacity')
    if scores is None: ranked=list(range(nblocks))
    else:
        if len(scores)!=nblocks: raise ValueError('Score length mismatch')
        ranked=sorted(range(nblocks),key=lambda i:(-float(scores[i]),i))
    loads=[0]*nblocks
    for i in ranked:
        if cap==0:break
        t=min(8,cap); loads[i]=t;cap-=t
    if cap!=0: raise RuntimeError('Unfilled budget')
    return loads


def embed(bm:torch.Tensor, secret:torch.Tensor, loads:list[int], sample_id='sample',key='new-demo-v1'):
    """Actual reversible bitmap embedding; unique random positions, versioned key."""
    if bm.ndim!=5 or bm.shape[0]!=1: raise ValueError('One [1,bh,bw,4,4] bitmap per call')
    nblocks=bm.shape[1]*bm.shape[2]
    if len(loads)!=nblocks or any(k<0 or k>8 for k in loads):raise ValueError('Invalid loads')
    total=sum(loads)
    if len(secret)!=total or not ((secret==0)|(secret==1)).all(): raise ValueError('Invalid secret length/bits')
    rows,pos=_flat_indices(loads,sample_id,key)
    out=bm.clone().reshape(nblocks,16)
    if total:out[rows.to(out.device),pos.to(out.device)]=secret.to(device=out.device,dtype=out.dtype)
    return out.reshape_as(bm)


def extract(bm:torch.Tensor,loads:list[int],sample_id='sample',key='new-demo-v1'):
    nblocks=bm.shape[1]*bm.shape[2]
    if len(loads)!=nblocks:raise ValueError('Invalid loads')
    rows,pos=_flat_indices(loads,sample_id,key)
    if len(rows)==0:return torch.zeros(0,dtype=torch.uint8)
    flat=bm.reshape(nblocks,16)
    return flat[rows.to(flat.device),pos.to(flat.device)].round().to(dtype=torch.uint8,device='cpu')


def corrected_reconstruct(bm,hi,lo,delta_map, max_delta=.08):
    """Project a learned 1-channel residual onto two AMBTC levels per block.
    Bitmap remains unchanged, so the secret is extractable from the AMBTC triplet.
    """
    if delta_map.ndim!=4 or delta_map.shape[1]!=1:raise ValueError('delta map Bx1xHxW')
    b,bh,bw,_,_=bm.shape
    patches=delta_map.unfold(2,4,4).unfold(3,4,4)[:,0]
    # patches: [B,bh,bw,4,4]
    count1=bm.sum((-2,-1)).clamp(min=1.)
    count0=(1.-bm).sum((-2,-1)).clamp(min=1.)
    dH=(patches*bm).sum((-2,-1))/count1
    dL=(patches*(1.-bm)).sum((-2,-1))/count0
    high=(hi+dH.clamp(-max_delta,max_delta)).clamp(0,1)
    low=(lo+dL.clamp(-max_delta,max_delta)).clamp(0,1)
    high=torch.maximum(high,low)
    return reconstruct(bm,high,low),high,low


def psnr(target,pred, peak=1.):
    mse=(target-pred).pow(2).mean().item()
    return float('inf') if mse==0 else 10*math.log10(peak*peak/mse)
