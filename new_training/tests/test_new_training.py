import sys,tempfile,json,hashlib
from pathlib import Path
import unittest
import torch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from ambtc import encode,reconstruct,embed,extract,plan_loads,corrected_reconstruct
from models import CandidateAttentionResUNet,count_parameters,fingerprint
from data import make_manifest,ImageDataset

class NewReconstructionTests(unittest.TestCase):
    def test_bmp_codec_constant(self):
        x=torch.ones(1,1,32,32)*.45
        b,h,l=encode(x)
        self.assertTrue(torch.allclose(reconstruct(b,h,l),x,atol=1e-6))
    def test_roundtrip_all_payloads(self):
        x=torch.rand(1,1,32,32,generator=torch.Generator().manual_seed(11))
        b,h,l=encode(x)
        for r in [.1,.2,.4]:
            k=plan_loads(64,r,scores=list(range(64)))
            msg=torch.randint(0,2,(sum(k),),generator=torch.Generator().manual_seed(17),dtype=torch.uint8)
            s=embed(b,msg,k,sample_id='abc')
            self.assertTrue(torch.equal(msg,extract(s,k,sample_id='abc')))
            self.assertLess(abs(sum(k)/(32*32)-r),1/(32*32))
            y,hh,ll=corrected_reconstruct(s,h,l,torch.zeros_like(x))
            self.assertTrue(torch.equal(extract(s,k,sample_id='abc'),msg))
            self.assertTrue(torch.allclose(y,reconstruct(s,h,l)))
    def test_fingerprint(self):
        m=CandidateAttentionResUNet(base=50)
        f=fingerprint(m)
        expected=json.loads((ROOT.parent/'recovery/pth_candidate_fingerprint.json').read_text())['fingerprint']
        for key,shape in expected.items():self.assertEqual(f[key],shape,key)
        self.assertGreater(count_parameters(m),0)
    def test_gradients(self):
        torch.set_num_threads(2)
        x=torch.rand(1,1,32,32)
        model=CandidateAttentionResUNet(base=4)
        b,h,l=encode(x)
        k=plan_loads(64,.2)
        msg=torch.randint(0,2,(sum(k),),dtype=torch.uint8)
        sb=embed(b,msg,k)
        z=reconstruct(sb,h,l)
        prediction,_,_=corrected_reconstruct(sb,h,l,model(z))
        loss=(prediction-reconstruct(b,h,l)).pow(2).mean()
        loss.backward()
        self.assertIsNotNone(model.outc.weight.grad)
        self.assertTrue(torch.isfinite(model.outc.weight.grad).all())
    def test_leakage(self):
        from PIL import Image
        import numpy as np
        with tempfile.TemporaryDirectory() as temp:
            r=Path(temp)
            for i in range(4):Image.fromarray(np.full((32,32),i*61,dtype=np.uint8)).save(r/f'{i}.png')
            data=make_manifest(r,r/'manifest.json',seed=42,smoke=True)
            self.assertEqual(len(data['items']),4)
            self.assertTrue(all(a['sha256'] for a in data['items']))
            ds=ImageDataset(r/'manifest.json','train',32)
            self.assertEqual(ds[0][0].shape,(1,32,32))
if __name__=='__main__':unittest.main()
