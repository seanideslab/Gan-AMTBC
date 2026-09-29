import csv, pathlib, subprocess, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Targeted(unittest.TestCase):
 def test_direct_pdf_transcription(self):
  with (ROOT/'paper_reported/figure8b_digitized_labels.csv').open(newline='') as f: r=list(csv.DictReader(f))
  row=next(x for x in r if x['clip_epsilon']=='0.3' and x['bpp']=='0.4')
  self.assertEqual(row['pe_percent'],'11.90')
 def test_crosscheck_provenance(self):
  with tempfile.TemporaryDirectory() as temp:
   proc=subprocess.run([sys.executable,str(ROOT/'targeted/run_checks.py'),'--outdir',temp],capture_output=True,text=True,check=True)
   self.assertIn('PRINTED_CONFLICTS: 5',proc.stdout)
   self.assertIn('remain unverified',proc.stdout)
if __name__=='__main__':unittest.main()
