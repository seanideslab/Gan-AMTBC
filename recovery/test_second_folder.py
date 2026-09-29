import json, unittest
from pathlib import Path
from checkpoint_fingerprint import compare_shapes
from create_candidate_splits import split_ids

class RecoveryNoteTests(unittest.TestCase):
    def test_nine_shapes_match_only_when_exact(self):
        exp=json.loads(Path(__file__).with_name('pth_candidate_fingerprint.json').read_text())['fingerprint']
        obs={'module.'+k:tuple(v) for k,v in exp.items()}
        res=compare_shapes(obs,exp)
        self.assertEqual(sum(x['status']=='MATCH' for x in res.values()),9)
        obs['module.outc.weight']=(3,50,1,1)
        self.assertEqual(compare_shapes(obs,exp)['outc.weight']['status'],'SHAPE_MISMATCH')
    def test_all_candidate_splits_deterministic_disjoint(self):
        ids=[f'boss/{i:05d}.pgm' for i in range(10000)]
        expected={'half':(5000,0,5000),'monitoring':(4000,1000,5000),'capacity':(8000,0,2000)}
        for seed in [42,0,123,2025]:
            for scheme,c in expected.items():
                a=split_ids(ids,seed,scheme);b=split_ids(ids,seed,scheme)
                self.assertEqual(a,b)
                self.assertEqual(tuple(len(a[k]) for k in ('train','val','test')),c)
                self.assertEqual(len(set(a['train'])|set(a['val'])|set(a['test'])),10000)
if __name__=='__main__':unittest.main()
