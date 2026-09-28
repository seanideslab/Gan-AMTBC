#!/usr/bin/env python3
"""Compare publication labels only. NO inference and NO artificial metrics."""
import csv
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def rows(path):
    with (ROOT / 'paper_reported' / path).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))
def main():
    full = next(r for r in rows('table4_published.csv') if r['algorithm']=='Proposed GAN-PPO-AMBTC')
    fig = [r for r in rows('figure8b_digitized_labels.csv') if r['clip_epsilon']=='0.2']
    print('Comparison: PUBLISHED TABLE 4 vs PUBLISHED FIGURE 8(b); no reproduced experiment')
    for r in fig:
        bpp = r['bpp']; table=float(full['pe_0p'+bpp.split('.')[-1]+'_bpp']); graphed=float(r['pe_percent'])
        print(f"epsilon=0.2, bpp={bpp}: Table4={table:.2f}% Figure8b={graphed:.2f}% difference={table-graphed:+.2f} percentage points")
    print('Table11 has ONLY 0.4 bpp, epsilon=0.1/0.2/0.3:')
    for r in rows('table11_published.csv'):
        print(f"epsilon={r['clip_epsilon']} bpp={r['bpp']} PE={r['pe_percent']}%")
    print('The Figure8(b) data cannot be repaired at 0.1/0.2 bpp without original per-epsilon logs.')
if __name__=='__main__': main()
