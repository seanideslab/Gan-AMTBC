#!/usr/bin/env python3
"""Create explicitly NEW candidate BOSSbase ID lists from a one-page archived note.

Never represent these as the original publication split. No benchmark images are bundled.
The exact order of --boss-manifest matters to sklearn's seeded split.
"""
import argparse,hashlib,json
from pathlib import Path

def split_ids(ids,seed,scheme):
    from sklearn.model_selection import train_test_split
    if len(ids)!=10000 or len(set(ids))!=10000:raise ValueError('Expected 10,000 unique BOSSbase IDs')
    if scheme=='half':
        tr,te=train_test_split(ids,train_size=.5,test_size=.5,random_state=seed)
        va=[]
    elif scheme=='monitoring':
        tr,te=train_test_split(ids,train_size=.4,test_size=.5,random_state=seed)
        selected=set(tr)|set(te)
        va=[x for x in ids if x not in selected]
    elif scheme=='capacity':
        tr,te=train_test_split(ids,train_size=.8,test_size=.2,random_state=seed)
        va=[]
    else:raise ValueError('Unknown scheme')
    assert len(tr)+len(va)+len(te)==10000
    assert len(set(tr)|set(va)|set(te))==10000
    return {'train':tr,'val':va,'test':te}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--boss-manifest',type=Path,required=True,help='One original dataset-qualified image ID per line in ORIGINAL order')
    p.add_argument('--out-dir',type=Path,required=True)
    p.add_argument('--seed',type=int,choices=[42,0,123,2025],required=True)
    p.add_argument('--scheme',choices=['half','monitoring','capacity'],required=True)
    args=p.parse_args()
    raw=args.boss_manifest.read_bytes();ids=[s.strip() for s in raw.decode('utf-8').splitlines() if s.strip()]
    splits=split_ids(ids,args.seed,args.scheme)
    out=args.out_dir;out.mkdir(parents=True,exist_ok=True)
    meta={'status':'NEW_CANDIDATE_NOT_HISTORICAL_SPLIT','source_note':'掃描檔案含pth的.pdf',
          'source_manifest_sha256':hashlib.sha256(raw).hexdigest(),
          'input_order_preserved':True,'seed':args.seed,'scheme':args.scheme,
          'preprocessing_size': 'UNRESOLVED: note=256x256; publication=512x512'}
    for name,values in splits.items():
        b=('\n'.join(values)+'\n').encode() if values else b''
        (out/(name+'.txt')).write_bytes(b)
        meta[name]={'count':len(values),'sha256':hashlib.sha256(b).hexdigest()}
    (out/'provenance.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(meta,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
