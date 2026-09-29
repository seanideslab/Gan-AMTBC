#!/usr/bin/env python3
"""Compare only transcribed PRINTED Figure 8(b), Table 4 and Table 11.
No model inference. No experimental reproduction. Never generates replacement measurements.
"""
from __future__ import annotations
import csv
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'paper_reported'
OUT = ROOT / 'audit' / 'FIG8B_PUBLICATION_CROSSCHECK.csv'

def load(name):
    with (DATA / name).open(encoding='utf-8-sig', newline='') as file:
        return list(csv.DictReader(file))


def main():
    figs=load('figure8b_digitized_labels.csv')
    table=next(row for row in load('table4_published.csv') if row['algorithm']=='Proposed GAN-PPO-AMBTC')
    t11={row['clip_epsilon']:row for row in load('table11_published.csv')}
    assert len(figs)==9 and len(t11)==3
    fields=['source','clip_epsilon','bpp','fig8b_pe_pct','table4_full_pe_pct','table11_at_0p4_pe_pct','table4_minus_fig_pp','table11_minus_fig_pp','comparison_status','provenance']
    OUT.parent.mkdir(exist_ok=True)
    counts={'MATCH':0,'CONFLICT':0,'NOT_COMPARABLE':0}
    with OUT.open('w',encoding='utf-8',newline='') as file:
        w=csv.DictWriter(file,fields);w.writeheader()
        for row in figs:
            eps=row['clip_epsilon'];bpp=row['bpp'];value=Decimal(row['pe_percent'])
            t4=Decimal(table['pe_0p'+bpp.split('.')[-1]+'_bpp']) if eps=='0.2' else None
            t11val=Decimal(t11[eps]['pe_percent']) if bpp=='0.4' else None
            d4=(t4-value) if t4 is not None else None
            d11=(t11val-value) if t11val is not None else None
            status=('CONFLICT' if any(d is not None and d != 0 for d in (d4,d11)) else
                    'MATCH' if t4 is not None or t11val is not None else 'NOT_COMPARABLE')
            counts[status]+=1
            w.writerow({'source':'published_Figure_8b','clip_epsilon':eps,'bpp':bpp,
                'fig8b_pe_pct':str(value),'table4_full_pe_pct':str(t4) if t4 is not None else '',
                'table11_at_0p4_pe_pct':str(t11val) if t11val is not None else '',
                'table4_minus_fig_pp':str(d4) if d4 is not None else '',
                'table11_minus_fig_pp':str(d11) if d11 is not None else '',
                'comparison_status':status,'provenance':'PUBLICATION_TRANSCRIPTION_ONLY_NOT_RAW_RESULTS'})
            print(f'eps={eps} bpp={bpp}: Fig8b={value} Table4={t4} Table11={t11val} status={status}')
    assert next(row for row in figs if row['clip_epsilon']=='0.3' and row['bpp']=='0.4')['pe_percent']=='11.09'
    assert counts=={'MATCH':0,'CONFLICT':5,'NOT_COMPARABLE':4}, counts
    print('Summary: 5 PRINT conflicts; 4 cells have no direct comparable printed table condition.')
    print('No replacement value is inferred, and no experimental measurements were produced.')

if __name__=='__main__': main()
