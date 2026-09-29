"""Export NEW generator, with provenance check, and compare scripted output to eager."""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
import torch
from evaluate_new import load_ckpt

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--checkpoint',required=True);p.add_argument('--out',required=True)
    p.add_argument('--allow-smoke',action='store_true')
    a=p.parse_args()
    model,meta=load_ckpt(a.checkpoint,a.allow_smoke)
    size=int(meta['image_size'])
    x=torch.rand(1,1,size,size)
    with torch.no_grad():
        reference=model(x)
        traced=torch.jit.trace(model,x,strict=True)
        actual=traced(x)
    maxdiff=(reference-actual).abs().max().item()
    if maxdiff>1e-6:raise RuntimeError('TorchScript export disagrees with eager output')
    path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
    traced.save(str(path))
    report={'status':'NEW_RECONSTRUCTION_TORCHSCRIPT','not_original_checkpoint':True,
            'smoke_only':meta['smoke_only'],'max_abs_diff':maxdiff,
            'checkpoint_sha256':hashlib.sha256(Path(a.checkpoint).read_bytes()).hexdigest(),
            'model_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'note':'Only the one-channel residual map network is exported. No PPO-DQN-SRM pipeline.'}
    path.with_suffix('.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
