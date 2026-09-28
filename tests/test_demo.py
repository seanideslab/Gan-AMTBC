import csv, pathlib, subprocess, tempfile, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
class DemoTests(unittest.TestCase):
    def run_command(self,*args):
        return subprocess.run([str(ROOT/'bin'/args[0]),*map(str,args[1:])],cwd=ROOT,check=True,capture_output=True,text=True).stdout
    def test_distinct_requested_payloads_and_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            outputs=[]
            for target in (0.1,0.2,0.4):
                p=pathlib.Path(d)/f'target_{target}.pgm'
                msg=self.run_command('gan_ppo_ambtc_infer',ROOT/'example/lena_like_64.pgm',p,target,ROOT/'weight/policy_smoke.txt')
                self.assertIn('DEMO_ONLY',msg)
                output_bits=int(msg.split('embedded_bits=')[1].split()[0]);self.assertLessEqual(abs(output_bits/4096-target),1/4096)
                rec=p.with_suffix('.recovered.bin')
                self.run_command('gan_ppo_ambtc_extract',str(p)+'.ambtc',str(p)+'.map',rec)
                self.assertEqual(pathlib.Path(str(p)+'.payload.bin').read_bytes(),rec.read_bytes())
                outputs.append(p.read_bytes())
            self.assertEqual(len(set(outputs)),3)
    def test_evaluation_uses_measured_data_and_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            manifest=pathlib.Path(d)/'list.txt';manifest.write_text(str(ROOT/'example/lena_like_64.pgm')+'\n')
            report=pathlib.Path(d)/'demo.csv'
            self.run_command('gan_ppo_ambtc_eval',manifest,report,0.4,ROOT/'weight/policy_smoke.txt')
            with report.open() as f: rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),1)
            self.assertEqual(rows[0]['provenance'],'DEMO_NOT_PAPER')
            self.assertEqual(rows[0]['embedded_bits'],'1638')
            self.assertEqual(rows[0]['verified_bitmap_bit_errors'],'0')
    def test_figure8_audit(self):
        p=subprocess.run(['python3',str(ROOT/'reproduction/figure8_audit.py')],capture_output=True,text=True,check=True)
        self.assertIn('difference=+19.82',p.stdout)
    def test_aggregate_measured_confusion_math_with_explicit_test_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            src=pathlib.Path(d)/'UNIT_TEST_ONLY_raw.csv';dst=pathlib.Path(d)/'out.csv'
            with src.open('w',newline='') as f:
                w=csv.writer(f)
                w.writerow(['variant','detector','bpp','seed','psnr','ssim','fp','tn','fn','tp','split_sha256','model_sha256'])
                for seed in range(5):
                    w.writerow(['unit_test_only','unit_test_detector',0.4,seed,30,0.95,5,95,20,80,'unit_test_split',f'unit_test_model_{seed}'])
            p=subprocess.run(['python3',str(ROOT/'reproduction/aggregate_runs.py'),str(src),str(dst)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            with dst.open() as f: rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),1)
            self.assertAlmostEqual(float(rows[0]['pe_mean_percent']),12.5)
            self.assertEqual(rows[0]['provenance'],'calculated_from_supplied_raw_runs')
    def test_aggregate_refuses_empty_and_missing(self):
        with tempfile.TemporaryDirectory() as d:
            out=pathlib.Path(d)/'out.csv'
            p=subprocess.run(['python3',str(ROOT/'reproduction/aggregate_runs.py'),str(ROOT/'reproduction/raw_runs_template.csv'),str(out)],capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)
            self.assertFalse(out.exists())
if __name__=='__main__':unittest.main()
