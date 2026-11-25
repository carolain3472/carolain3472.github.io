import json,collections,glob,sys
for f in sorted(glob.glob('results_*.json')):
    R=json.load(open(f)); print('==',f)
    for c in ('vague','rules','reads'):
        rs=[r for r in R if r['cond']==c]; ex=sum(r['total']==r['exact'] for r in rs); q=sum(r['total'] is None for r in rs)
        d=[len(set(r['total'] for r in rs if r['order']==i and r['total'] is not None)) for i in range(10)]
        print(c,'exact',ex,'asked',q,'distinct totals per order',d)
    for i in range(10):
        t=collections.Counter(r['total'] for r in R if r['cond']=='vague' and r['order']==i); print(' ',i,[r['exact'] for r in R if r['order']==i][0],dict(t))
