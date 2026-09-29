import csv,subprocess,tempfile,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).parent
class DataTests(unittest.TestCase):
 def test_duplicates_cannot_cross_partition(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);src=d/'source';src.mkdir();out=d/'out'
   for i in range(7):
    im=Image.new('L',(16,16),i*20);im.save(src/f'{i}.png')
   (src/'duplicate.png').write_bytes((src/'0.png').read_bytes())
   p=subprocess.run(['python3',str(ROOT/'dataset_inventory.py'),'--image-root',str(src),
    '--out-dir',str(out),'--new-split','--seed','42'],capture_output=True,text=True)
   self.assertEqual(p.returncode,0,p.stderr)
   with (out/'NEW_split_not_paper.csv').open(newline='') as f: rows=list(csv.DictReader(f))
   by_hash={}
   for r in rows:
    by_hash.setdefault(r['sha256'],set()).add(r['partition'])
   self.assertTrue(all(len(v)==1 for v in by_hash.values()))
   self.assertEqual(len(rows),8)
 def test_empty_dataset_refused(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d)
   p=subprocess.run(['python3',str(ROOT/'dataset_inventory.py'),'--image-root',str(d),'--out-dir',str(d/'out')],capture_output=True,text=True)
   self.assertNotEqual(p.returncode,0)
if __name__=='__main__':unittest.main()
