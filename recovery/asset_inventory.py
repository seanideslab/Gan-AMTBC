"""Hash and classify located assets without claiming they are original model weights."""
import argparse,hashlib,json
from pathlib import Path
EXT={'.pt','.pth','.ckpt','.bin','.npy','.npz','.csv','.json','.txt'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--search-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();root=a.search_root.resolve()
 if not root.is_dir():p.error('Not a directory')
 rows=[]
 for f in sorted(root.rglob('*')):
  if f.is_file() and f.suffix.lower() in EXT and f.resolve()!=a.out.resolve():
   name=f.relative_to(root).as_posix()
   status='UNVERIFIED_NEEDS_PROVENANCE'
   if f.name=='policy_smoke.txt':status='DEMO_TOY_NOT_TRAINED_CHECKPOINT'
   elif f.suffix.lower() in ('.pt','.pth','.ckpt'):status='POSSIBLE_CHECKPOINT_UNVERIFIED_DO_NOT_LOAD_UNTRUSTED'
   elif 'paper_reported/' in name:status='PUBLICATION_TRANSCRIPTION_ONLY'
   rows.append({'path':name,'bytes':f.stat().st_size,'sha256':sha(f),'status':status})
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps({'searched_root':str(root),'n_files':len(rows),'assets':rows},indent=2),encoding='utf-8')
 print(f'Inventoried {len(rows)} files; no file is automatically verified as original experiment evidence.')
if __name__=='__main__':main()
