#!/usr/bin/env python3
"""Targeted source / paper consistency checks; no GAN-PPO training or output claims."""
import argparse,csv,hashlib,json,math,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def inventory():
 groups={
 'PUBLISHED_ARTICLE_RESEARCH_ASSETS':[
  'original_assets/ppo_actor.pt','original_assets/dqn.pt','original_assets/unet.pt',
  'original_assets/srm_srnet.pt','original_assets/srm_extractor.py',
  'original_assets/maxsrmd2_extractor.py','original_assets/ERANet.pt',
  'original_assets/SiaStegNet.pt','original_assets/train.py',
  'original_assets/bossbase_test_ids.txt','original_assets/five_seed_raw_runs.csv',
  'original_assets/figure8b_raw.csv'],
 'DEMO_ASSETS':['src/infer.c','src/generator.c','src/budget.c',
  'weight/policy_smoke.txt','verification/DEMO_RESULTS.csv'],
 'MEASUREMENT_ADAPTER':['reproduction/score_torchscript.py']}
 data=[]
 for group,files in groups.items():
  for f in files:
   p=ROOT/f
   data.append({'kind':group,'path':f,'exists':p.is_file(),
                'sha256':sha(p) if p.is_file() else None})
 return data

def check_publication():
 def rows(n):
  with (ROOT/'paper_reported'/n).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
 fig=rows('figure8b_digitized_labels.csv')
 full=next(x for x in rows('table4_published.csv') if x['algorithm']=='Proposed GAN-PPO-AMBTC')
 t11={x['clip_epsilon']:x for x in rows('table11_published.csv')}
 assert len(fig)==9 and len(t11)==3
 out=[]
 for row in fig:
  eps,bpp=row['clip_epsilon'],row['bpp'];fv=float(row['pe_percent'])
  v4=float(full['pe_0p'+bpp[-1]+'_bpp']) if eps=='0.2' else None
  v11=float(t11[eps]['pe_percent']) if bpp=='0.4' else None
  iscomp=v4 is not None or v11 is not None
  conflict=iscomp and any(abs(v-fv)>0.0001 for v in (v4,v11) if v is not None)
  out.append({'epsilon':eps,'bpp':bpp,'figure_label':fv,'table4':v4,
              'table11':v11,'state':'PRINTED_CONFLICT' if conflict else 'NO_DIRECT_COMPARATOR' if not iscomp else 'PRINTED_AGREEMENT'})
 assert [x['state'] for x in out].count('PRINTED_CONFLICT')==5
 return out

def formula():
 tau,alpha,beta=.5,10.,5.
 pub=lambda t:math.tanh(alpha*(t-tau))-math.tanh(beta*(t+tau))
 raw=lambda t: .5*(math.tanh(alpha*(t-tau))+math.tanh(beta*(t+tau)))
 off=raw(0)
 candidate=lambda t: (raw(t)-off)/(1-off) if raw(t)>=off else (raw(t)-off)/(1+off)
 out={'published_subtraction_at_zero':pub(0),
      'uncompensated_sum_half_at_zero':raw(0),
      'independent_centered_candidate_at_zero':candidate(0),
      'published_limits_at_large_values':[pub(-100),pub(100)],
      'candidate_limits_at_large_values':[candidate(-100),candidate(100)],
      'original_PyTorch_training_formula':'NOT_AVAILABLE',
      'C_demo_calls_double_tanh':False}
 assert abs(pub(0)+1.986524)<.00001
 assert abs(candidate(0))<1e-10
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--outdir',default=str(ROOT/'targeted/out'))
 a=ap.parse_args();out=pathlib.Path(a.outdir);out.mkdir(parents=True,exist_ok=True)
 inv=inventory();diff=check_publication();fn=formula()
 (out/'source_inventory.json').write_text(json.dumps(inv,indent=2)+'\n')
 (out/'formula_numeric.json').write_text(json.dumps(fn,indent=2)+'\n')
 with (out/'publication_crosscheck.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(diff[0]));w.writeheader();w.writerows(diff)
 missing=sum(not i['exists'] for i in inv if i['kind']=='PUBLISHED_ARTICLE_RESEARCH_ASSETS')
 print('PRINTED_CONFLICTS:',sum(x['state']=='PRINTED_CONFLICT' for x in diff))
 print('NO_DIRECT_COMPARATOR:',sum(x['state']=='NO_DIRECT_COMPARATOR' for x in diff))
 print('ORIGINAL_RESEARCH_ASSET_PLACEHOLDERS_MISSING:',missing)
 print('C demo status: separate software functional test, NOT PPO/GAN reproduction')
 print('Original experiment results remain unverified.')
if __name__=='__main__':main()
