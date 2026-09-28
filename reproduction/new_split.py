#!/usr/bin/env python3
"""Create a NEW deterministic split from legal image manifests; not the historical paper split."""
import argparse, hashlib, json, random
from pathlib import Path

def read(path):
    ids=[s.strip() for s in Path(path).read_text().splitlines() if s.strip()]
    if len(ids)!=len(set(ids)): raise ValueError(f'duplicate identifiers in {path}')
    return ids
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--boss-list',required=True);p.add_argument('--bows-list',required=True)
p.add_argument('--out',required=True);p.add_argument('--seed',type=int,default=0)
a=p.parse_args()
boss=read(a.boss_list);bows=read(a.bows_list)
if len(boss)!=10000: raise SystemExit('Expected 10000 BOSSbase image IDs; cannot invent missing images')
if set(boss)&set(bows): raise SystemExit('IDs overlap; use dataset-qualified relative IDs')
rng=random.Random(a.seed);rng.shuffle(boss);rng.shuffle(bows)
test=boss[:5000];remain=boss[5000:]+bows
rng.shuffle(remain);v=max(1,int(0.1*len(remain)))
parts={'train':remain[v:],'val':remain[:v],'test':test}
if sum(map(len,parts.values()))!=len(boss)+len(bows): raise AssertionError
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
meta={'origin':'NEW independent split, NOT original publication split','seed':a.seed}
for name,ids in parts.items():
    content='\n'.join(ids)+'\n';(out/(name+'.txt')).write_text(content)
    meta[name]={'count':len(ids),'sha256':hashlib.sha256(content.encode()).hexdigest()}
(out/'split_provenance.json').write_text(json.dumps(meta,indent=2)+'\n')
print(meta)
