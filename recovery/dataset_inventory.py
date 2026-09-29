"""Read-only image inventory or clearly NEW deterministic split; never reconstructs original BOSSbase split.

Examples:
  python3 recovery/dataset_inventory.py --image-root /path/to/licensed/images --out-dir /tmp/audit
  python3 recovery/dataset_inventory.py --image-root /path/to/licensed/images --out-dir /tmp/audit --new-split --seed 2026 --train 0.7 --val 0.1
"""
import argparse,csv,hashlib,json,random
from pathlib import Path
SUFFIX={'.png','.pgm','.bmp','.tif','.tiff','.jpg','.jpeg'}
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def build_manifest(root):
 from PIL import Image
 rows=[]
 for p in sorted(root.rglob('*')):
  if not p.is_file() or p.suffix.lower() not in SUFFIX:continue
  with Image.open(p) as im:
   shape=(im.width,im.height);mode=im.mode
  rows.append(dict(image_id=p.relative_to(root).as_posix(),sha256=digest(p),width=shape[0],height=shape[1],mode=mode,source_root=str(root.resolve())))
 return rows

def write_csv(path,rows,fields):
 with path.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--image-root',required=True,type=Path);p.add_argument('--out-dir',required=True,type=Path)
 p.add_argument('--new-split',action='store_true');p.add_argument('--seed',type=int,default=None)
 p.add_argument('--train',type=float,default=.7);p.add_argument('--val',type=float,default=.1)
 a=p.parse_args();root=a.image_root.resolve()
 if not root.is_dir():p.error('image-root does not exist; no dataset supplied')
 rows=build_manifest(root)
 if not rows:p.error('No readable image files; refusing empty pretend dataset')
 a.out_dir.mkdir(parents=True,exist_ok=True)
 write_csv(a.out_dir/'inventory.csv',rows,['image_id','sha256','width','height','mode','source_root'])
 dup={}
 for r in rows:dup.setdefault(r['sha256'],[]).append(r['image_id'])
 dups={k:v for k,v in dup.items() if len(v)>1}
 summary={'provenance':'USER_SUPPLIED_IMAGE_INVENTORY_NOT_ORIGINAL_PUBLICATION_SPLIT',
  'source_root':str(root),'n_files':len(rows),'n_unique_bytes':len(dup),
  'duplicates_by_content':dups,'original_published_5000_test_split_recovered':False}
 if a.new_split:
  if a.seed is None:p.error('Explicit --seed required when --new-split is used')
  if not (0<a.train<1 and 0<=a.val<1 and a.train+a.val<1):p.error('Invalid proportions')
  groups=sorted(dup.items());random.Random(a.seed).shuffle(groups)
  n=len(groups);ntrain=round(n*a.train);nval=round(n*a.val)
  split=[]
  for i,(sha,names) in enumerate(groups):
   part='NEW_TRAIN' if i<ntrain else ('NEW_VAL' if i<ntrain+nval else 'NEW_TEST')
   for name in names:split.append({'image_id':name,'sha256':sha,'partition':part})
  write_csv(a.out_dir/'NEW_split_not_paper.csv',sorted(split,key=lambda r:r['image_id']),['image_id','sha256','partition'])
  summary.update(new_split=True,new_split_seed=a.seed,split_groups={'NEW_TRAIN':ntrain,'NEW_VAL':nval,'NEW_TEST':n-ntrain-nval})
 else:summary['new_split']=False
 (a.out_dir/'provenance.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
