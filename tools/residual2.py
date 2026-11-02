import sys,os,re,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
exec(open('tools/residual.py',encoding='utf-8').read().split('items=sorted')[0])
out=[]
for t,v in res.items():
    ls=[l for l in t.split('\n') if l.strip('　')]
    real=[l for l in ls if not (l.startswith('＠') or l.startswith('（') or l.startswith('＜'))]
    if not real: continue
    out.append((t,v))
out.sort(key=lambda kv:(kv[1][0][0],kv[1][0][1]))
json.dump([{'ja':t,'loc':v} for t,v in out],open('tmp/resid.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(len(out))
for t,v in out: print(len(v),v[0][0][-8:],hex(v[0][1]),repr(t[:60]))
