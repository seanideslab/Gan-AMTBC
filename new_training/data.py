"""New, deterministic, leakage-checked image manifest; cannot recover original BOSSbase split."""
from __future__ import annotations
import hashlib,json,random
from pathlib import Path
import numpy as np
from PIL import Image
from torch.utils.data import Dataset
import torch

ALLOWED={'.png','.pgm','.bmp','.tif','.tiff'}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def make_manifest(root,out,seed=42,test_fraction=.5,val_fraction=.1,smoke=False):
    root=Path(root).resolve()
    files=sorted(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in ALLOWED)
    if len(files)<2:raise ValueError('Need at least two real files')
    if len(files)<100 and not smoke:raise ValueError('Too few images for a research run; use --smoke only for tests')
    hashes={};unique=[]
    for p in files:
        h=sha(p)
        if h in hashes:continue
        hashes[h]=str(p);unique.append((p,h))
    if len(unique)<2:raise ValueError('Need two distinct images')
    rng=random.Random(seed);rng.shuffle(unique)
    if smoke:
        ntest=max(1, round(len(unique)*.25))
        nval=max(0,round(len(unique)*.25))
    else:
        ntest=round(len(unique)*test_fraction);nval=round(len(unique)*val_fraction)
    ntrain=len(unique)-ntest-nval
    if ntrain<1:raise ValueError('Empty training split')
    records=[]
    for i,(p,h) in enumerate(unique):
        split='train' if i<ntrain else 'val' if i<ntrain+nval else 'test'
        records.append({'path':str(p),'sha256':h,'split':split})
    result={'status':'NEW_SPLIT_NOT_ORIGINAL', 'source_root':str(root),'seed':seed,
            'test_fraction':test_fraction,'val_fraction':val_fraction,
            'smoke':smoke,'items':records}
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    Path(out).write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    return result


class ImageDataset(Dataset):
    def __init__(self,manifest,split='train',size=256,require_hash=True):
        self.manifest_path=Path(manifest)
        data=json.loads(self.manifest_path.read_text(encoding='utf8'))
        if data.get('status')!='NEW_SPLIT_NOT_ORIGINAL':raise ValueError('This trainer requires explicit NEW split')
        if size%16:raise ValueError('Size divisible by 16')
        self.items=[r for r in data['items'] if r['split']==split];self.size=size
        if len(self.items)==0:raise ValueError(f'Empty split {split}')
        if require_hash:
            for r in self.items:
                if sha(r['path'])!=r['sha256']:raise ValueError('Dataset file modified: '+r['path'])
        self._check_hashes(data['items'])
    @staticmethod
    def _check_hashes(items):
        hashes={}
        for x in items:
            h=x['sha256']
            if h in hashes and hashes[h]!=x['split']:raise ValueError('Image hash leaked across split')
            hashes[h]=x['split']
    def __len__(self):return len(self.items)
    def __getitem__(self,i):
        r=self.items[i]
        with Image.open(r['path']) as im:
            x=im.convert('L').resize((self.size,self.size),Image.Resampling.BICUBIC)
            a=np.asarray(x,dtype='float32').copy()/255.
        return torch.from_numpy(a).unsqueeze(0),r['sha256']
