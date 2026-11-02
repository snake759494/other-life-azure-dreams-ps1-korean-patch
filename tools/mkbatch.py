import json,re,sys
sys.path.insert(0,'tools')
S=json.load(open('text/segments.json',encoding='utf-8'))
FORD={'MAIN.BIN':0,'SLPM_860.47':1,'DUNGEON.BIN':2,'TOWN.BIN':3}
items=[]
for i,x in enumerate(S):
    ja=x['ja']
    lines=ja.split('\n')
    if re.search('ァィゥェォ|あいうえお|つてとなぬの|アイウエオカキ',ja): continue
    if all(l.startswith(('＠','（','＠（')) for l in lines): continue
    f,o,l=min(x['loc'],key=lambda t:(FORD[t[0]],t[1]))
    blen=min(t[2] for t in x['loc'])
    mw=max(len(l.replace('{N}','NNNN')) for l in lines)
    maxw=max(mw,22) if mw>=15 else mw+2
    items.append({'id':i,'ja':ja,'bytes':blen,'lines':len(lines),'maxw':maxw,'_k':(FORD[f],o)})
items.sort(key=lambda t:t['_k'])
for t in items: del t['_k']
# 배치 분할 ~13000자
import os
os.makedirs('text/ja',exist_ok=True); os.makedirs('text/ko',exist_ok=True)
b=[];cur=[];n=0
for t in items:
    cur.append(t); n+=len(t['ja'])
    if n>=13000: b.append(cur); cur=[]; n=0
if cur: b.append(cur)
for k,c in enumerate(b):
    json.dump(c,open(f'text/ja/b{k:02d}.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
    print(k,len(c),sum(len(t['ja']) for t in c))
print('total',len(items))
