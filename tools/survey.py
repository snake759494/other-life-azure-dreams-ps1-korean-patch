# 빌드 결과에서 남은 일본어 문자열 전수 조사 (널/제어 경계, 가나 또는 한자 2자 이상)
import sys,re,json,collections
sys.path.insert(0,'tools'); from iso import Disc
img=sys.argv[1]
dd=Disc(img);F={q:(l,z) for q,l,z,_,_ in dd.walk()}
pat=re.compile(rb'(?<=[\x00-\x1f])((?:[\x81-\x84\x88-\x9f\xe0-\xea][\x40-\x7e\x80-\xfc]|[\x20-\x7e\n])*?(?:\x82[\x9f-\xf1]|\x83[\x40-\x96]|[\x88-\x9f\xe0-\xea][\x40-\x7e\x80-\xfc])(?:[\x81-\x84\x88-\x9f\xe0-\xea][\x40-\x7e\x80-\xfc]|[\x20-\x7e\n])*)(?=\x00)')
cmap=json.load(open('text/cmap.json',encoding='utf-8'))
K=set(int(v,16) for v in cmap.values())
out=collections.OrderedDict()
for p in ['/SLPM_860.47','/MAIN/MAIN.BIN','/TOWN/TOWN.BIN','/DUNGEON/DUNGEON.BIN']:
    d=dd.read(*F[p]); od=open('orig/'+p.split('/')[-1],'rb').read()
    for m in pat.finditer(d):
        b=m.group(1)
        try: t=b.decode('cp932')
        except: continue
        # 한글 코드가 섞였으면 패치된 것
        if od[m.start(1):m.end(1)]!=b: continue
        if re.search('[ぁ-ゖ]',t) is None and re.search('[ァ-ヺ]{2}',t) is None and not re.fullmatch('[一-龠々]{2,6}',t): continue
        kana=len(re.findall('[ぁ-ゖァ-ヺー]',t)); kan=len(re.findall('[一-龠々]',t))
        if kana+kan<2: continue
        if kana==0 and kan<2: continue
        if re.search('[\x20-\x7e]',t) and kana<2: continue
        out.setdefault(t,[]).append((p.split('/')[-1],m.start(1)))
json.dump([[t,v] for t,v in out.items()],open('tmp/survey.json','w',encoding='utf-8'),ensure_ascii=False)
print(len(out))
for t,v in out.items(): print(len(v),v[0][0],hex(v[0][1]),repr(t)[:60])
