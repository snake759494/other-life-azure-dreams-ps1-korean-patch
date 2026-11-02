# 빌드된 이미지에서 남은 가나 문자열 검사
import sys,os,re,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from iso import Disc
d=Disc(sys.argv[1] if len(sys.argv)>1 else '../Other Life Azure Dreams (Japan) [KOR].bin')
F={p:(l,s) for p,l,s,_,_ in d.walk()}
pat=re.compile(rb'(?:[\x81-\x9f\xe0-\xea][\x40-\x7e\x80-\xfc]|\n)*(?:\x82[\x9f-\xf1]|\x83[\x40-\x96])(?:[\x81-\x9f\xe0-\xea][\x40-\x7e\x80-\xfc]|\n)*')
res={}
for p in ['/MAIN/MAIN.BIN','/TOWN/TOWN.BIN','/DUNGEON/DUNGEON.BIN','/SLPM_860.47']:
    l,s=F[p]; b=d.read(l,min(s,0x53800) if 'SLPM' in p else s)
    for m in pat.finditer(b):
        t=m.group()
        kn=sum(1 for i in range(0,len(t)-1) if (t[i]==0x82 and 0x9f<=t[i+1]<=0xf1) or (t[i]==0x83 and 0x40<=t[i+1]<=0x96))
        if kn<2: continue
        try: txt=t.decode('cp932')
        except: continue
        res.setdefault(txt,[]).append((p,m.start()))
items=sorted(res.items(),key=lambda kv:-len(kv[0]))
print(len(items))
for t,v in items[:int(sys.argv[2]) if len(sys.argv)>2 else 80]: print(len(v),v[0][0],hex(v[0][1]),repr(t[:70]))
