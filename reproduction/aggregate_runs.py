#!/usr/bin/env python3
"""Compute detector P_E from independently measured confusion counts and audit five seeds.
Input must be actual measured rows. Published summary tables must NOT be used as input.
"""
import argparse, csv, hashlib, math, statistics, sys
from collections import defaultdict
from pathlib import Path
REQUIRED = ['variant','detector','bpp','seed','psnr','ssim','fp','tn','fn','tp','split_sha256','model_sha256']

def aggregate(src, dest, expected_seeds=5):
    with open(src,newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        absent=set(REQUIRED)-set(reader.fieldnames or [])
        if absent: raise ValueError('Missing required raw-data columns: '+', '.join(sorted(absent)))
        records=list(reader)
    if not records: raise ValueError('No original run records; refusing to export publication metrics')
    groups=defaultdict(list)
    for line,r in enumerate(records,2):
        try:
            counts=[int(r[k]) for k in ('fp','tn','fn','tp')]
            if min(counts)<0 or counts[0]+counts[1]==0 or counts[2]+counts[3]==0:
                raise ValueError('invalid confusion counts')
            p=float(r['psnr']); s=float(r['ssim']); b=float(r['bpp'])
            if not (math.isfinite(p) and math.isfinite(s) and math.isfinite(b) and 0 <= s <= 1):
                raise ValueError('invalid metric')
            seed=int(r['seed'])
            if not r['split_sha256'] or not r['model_sha256']:
                raise ValueError('missing provenance hash')
        except (ValueError,TypeError) as exc:
            raise ValueError(f'Bad run record line {line}: {exc}') from exc
        key=(r['variant'],r['detector'],r['bpp'])
        r['_pe']=50*(counts[0]/(counts[0]+counts[1])+counts[2]/(counts[2]+counts[3]))
        r['_seed']=seed;r['_psnr']=p;r['_ssim']=s
        groups[key].append(r)
    result=[]
    for key, data in sorted(groups.items()):
        seeds=[r['_seed'] for r in data]
        if len(data)!=expected_seeds or len(set(seeds))!=expected_seeds:
            raise ValueError(f'{key}: expected {expected_seeds} independent unique seed records; got {seeds}')
        if len({r['split_sha256'] for r in data})!=1:
            raise ValueError(f'{key}: inconsistent split manifests; comparison invalid')
        def mean_std(name):
            vals=[r[name] for r in data]
            return statistics.mean(vals),statistics.stdev(vals)
        pe,ps=mean_std('_pe');pr,prs=mean_std('_psnr'); ss,sss=mean_std('_ssim')
        result.append(dict(zip(['variant','detector','bpp'],key),seeds=';'.join(map(str,sorted(seeds))),
                           n_runs=len(data),pe_mean_percent=f'{pe:.6f}',pe_sd_percent=f'{ps:.6f}',
                           psnr_mean=f'{pr:.6f}',psnr_sd=f'{prs:.6f}',ssim_mean=f'{ss:.6f}',ssim_sd=f'{sss:.6f}',
                           split_sha256=data[0]['split_sha256'],provenance='calculated_from_supplied_raw_runs'))
    fields=list(result[0])
    with open(dest,'w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(result)
    return len(result)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw_run_csv');parser.add_argument('output_csv');parser.add_argument('--expected-seeds',type=int,default=5)
    args=parser.parse_args()
    try: print(f'Aggregated {aggregate(args.raw_run_csv,args.output_csv,args.expected_seeds)} groups')
    except ValueError as e: print('VALIDATION FAILED:',e,file=sys.stderr);sys.exit(2)
