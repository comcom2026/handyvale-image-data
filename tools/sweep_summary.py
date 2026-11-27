#!/usr/bin/env python3
"""Summarise a sweep CSV from this repository without third-party packages."""
import csv,sys,statistics

def main():
    if len(sys.argv)!=2:
        print('usage: python3 tools/sweep_summary.py data/bulk-threshold-sweep.csv',file=sys.stderr)
        return 2
    with open(sys.argv[1],newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    if not rows:
        print('no rows'); return 1
    numcols=[k for k in rows[0] if k not in ('source_page','method','measured_at')]
    print('rows',len(rows))
    for k in numcols:
        vals=[float(r[k]) for r in rows if r.get(k) not in ('',None)]
        if vals:
            print(f'{k}: min={min(vals)} max={max(vals)} mean={statistics.fmean(vals):.3f}')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
