"""Export a smaller, provenance-labelled state_dict from a newly trained checkpoint."""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
import torch

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--checkpoint',required=True);p.add_argument('--out',required=True)
    a=p.parse_args()
    src=Path(a.checkpoint)
    ckpt=torch.load(src,weights_only=True,map_location='cpu')
    meta=ckpt.get('meta',{})
    if meta.get('status')!='NEW_INDEPENDENT_RECONSTRUCTION':raise ValueError('Not a matching NEW checkpoint')
    if 'state_dict' not in ckpt or int(ckpt.get('epoch_completed',0))<1:raise ValueError('No trained weights')
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    data={'state_dict':ckpt['state_dict'],'meta':meta,'epoch_completed':ckpt['epoch_completed']}
    torch.save(data,out)
    report={'status':meta['status'],'smoke_only':meta['smoke_only'],
            'original_model':False,'epoch_completed':ckpt['epoch_completed'],
            'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
            'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
            'note':'No optimizer. All provenance tags preserved. No reported-paper metrics.'}
    out.with_suffix('.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
