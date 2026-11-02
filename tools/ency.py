# 몬스터 도감(10자 줄 조각, 역순 저장) 문단 단위 추출/검사
import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG=[(0x8c0940,0x8c38ec),(0x9d317c,0x9d6200)]
def frags(d,a,b):
    out=[];o=a
    while o<b:
        e=d.index(b'\0',o)
        if e>o: out.append((o,e-o,(((e+4)&~3)-o)-1,d[o:e]))   # off,len,cap(널 제외 최대),bytes
        o=(e+4)&~3
    return out
def paragraphs(d):
    res=[]
    for a,b in REG:
        F=frags(d,a,b)
        k=[i for i,f in enumerate(F) if f[3].decode('cp932','replace')=='キューン'][0]+1
        body=F[k:][::-1]
        cur=None
        for o,l,cap,t in body:
            s=t.decode('cp932','replace')
            if s.startswith('　') or cur is None:
                cur={'ja':'','slots':[]}; res.append(cur)
            cur['ja']+=s; cur['slots'].append([o,cap])
    return res
if __name__=='__main__' and sys.argv[1]=='extract':
    d=open('orig/TOWN.BIN','rb').read()
    P=paragraphs(d)
    uniq={}
    for p in P:
        key=(p['ja'],tuple(c for o,c in p['slots']))
        uniq.setdefault(key,[]).append([o for o,c in p['slots']])
    out=[{'id':i,'ja':k[0],'caps':list(k[1]),'locs':v} for i,(k,v) in enumerate(uniq.items())]
    json.dump(out,open('text/ency_ja.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
    print(len(P),len(out),sum(len(x['ja']) for x in out))
if __name__=='__main__' and sys.argv[1]=='chk':
    from kenc import blen,bad_chars
    J=json.load(open('text/ency_ja.json',encoding='utf-8'))
    K={x['id']:x['ko'] for x in json.load(open('text/ency_ko.json',encoding='utf-8'))} if os.path.exists('text/ency_ko.json') else {}
    bad=0
    for x in J:
        k=K.get(x['id']); e=[]
        if k is None: e.append('번역 없음')
        else:
            ls=k.split('\n')
            if len(ls)>len(x['caps']): e.append(f"줄 수 초과 {len(ls)}/{len(x['caps'])}")
            for i,l in enumerate(ls[:len(x['caps'])]):
                if blen(l)>x['caps'][i]: e.append(f"{i+1}번째 줄 {blen(l)}바이트 > {x['caps'][i]}: {l}")
            if bad_chars(k): e.append('사용 불가 문자 '+''.join(bad_chars(k)))
        if e:
            bad+=1
            if bad<=40: print(x['id'],x['ja'],'\n  ->',repr(k),'\n  *',' / '.join(e))
    print(f'문제 문단: {bad} / {len(J)}')
