# 한글패치 빌드: python tools/build.py [출력bin]
import json,glob,os,sys,shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kenc import tokens,is_hangul
from build_exe import build as build_exe,code_for
from font import glyph,tobytes
from disc import Writer
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ORIG='../Other Life Azure Dreams (Japan).bin'
OUT=sys.argv[1] if len(sys.argv)>1 else '../Other Life Azure Dreams (Japan) [KOR].bin'
PATHS={'MAIN.BIN':'/MAIN/MAIN.BIN','TOWN.BIN':'/TOWN/TOWN.BIN','DUNGEON.BIN':'/DUNGEON/DUNGEON.BIN','SLPM_860.47':'/SLPM_860.47'}

S=json.load(open('text/segments.json',encoding='utf-8'))
ko={}
for p in sorted(glob.glob('text/ko/*.json')):
    for x in json.load(open(p,encoding='utf-8')): ko[x['id']]=x['ko']
extra=json.load(open('text/extra.json',encoding='utf-8')) if os.path.exists('text/extra.json') else {}

# 1) 글리프 집합(가나다순 → 이름 입력 '한자' 모드에서 가나다순으로 보임)
chars=set()
for i,t in ko.items():
    if t!=S[i]['ja']: chars.update(c for c in tokens(t) if len(c)==1 and is_hangul(c))
for it in extra.get('items',[]): chars.update(c for c in tokens(it['ko']) if len(c)==1 and is_hangul(c))
ency=json.load(open('text/ency_ko.json',encoding='utf-8')) if os.path.exists('text/ency_ko.json') else []
for it in ency: chars.update(c for c in tokens(it['ko']) if len(c)==1 and is_hangul(c))
MENU=chr(10).join(['가나','가타','한글','영숫','기호','사전','삭제','이전','완료'])
chars.update(c for c in MENU if is_hangul(c))
for t in extra.get('force_chars',''): chars.add(t)
for v in json.load(open('text/resid_ko.json',encoding='utf-8')).values(): chars.update(c for c in v if is_hangul(c))
chars.update('청녹적대소')
KB=json.load(open('text/kblock_ko.json',encoding='utf-8'))
for v in KB.values(): chars.update(c for c in v if is_hangul(c))
for t in json.load(open('text/movie_ko.json',encoding='utf-8')): pass
DK=json.load(open('text/dmsg_ko.json',encoding='utf-8'))
for x in DK: chars.update(c for c in x['ko'] if is_hangul(c))
chars=sorted(chars)
cmap={c:code_for(i) for i,c in enumerate(chars)}
print('글리프',len(chars))

def enc(t):
    out=bytearray()
    for tk in tokens(t):
        if tk=='\n': out+=b'\n'
        elif tk=='{N}': out+=b'\xfe\x00'
        elif tk in cmap: out+=cmap[tk].to_bytes(2,'big')
        else: out+=tk.encode('cp932')
    return bytes(out)

def fit(t,n,nul):
    """번역 t를 정확히 n바이트로. nul=True면 0으로 채움"""
    b=enc(t)
    assert len(b)<=n,(t,len(b),n)
    if nul: return b+b'\0'*(n-len(b))
    rem=n-len(b)
    if rem%2: b+=b'\n'; rem-=1
    return b+b'\x81\x40'*(rem//2)

data={f:bytearray(open('orig/'+f,'rb').read()) for f in PATHS}
cnt=0
for i,t in ko.items():
    x=S[i]
    if t==x['ja']: continue
    for f,o,l in x['loc']:
        d=data[f]
        nul=(o+l<len(d) and d[o+l]==0)
        d[o:o+l]=fit(t,l,nul); cnt+=1
for it in extra.get('items',[]):
    for f,o,l in it['loc']:
        data[f][o:o+l]=fit(it['ko'],l,True); cnt+=1
# 몬스터 도감: 문단 -> 줄 칸
if ency:
    EJ={x['id']:x for x in json.load(open('text/ency_ja.json',encoding='utf-8'))}
    orgT=open('orig/TOWN.BIN','rb').read(); orgD=open('orig/DUNGEON.BIN','rb').read()
    for it in ency:
        x=EJ[it['id']]; ls=it['ko'].split(chr(10))
        for offs in x['locs']:
            for k,(o,cap) in enumerate(zip(offs,x['caps'])):
                line=ls[k] if k<len(ls) else ''
                b=fit(line,cap,True)
                same=orgD[o:o+cap]==orgT[o:o+cap]
                data['TOWN.BIN'][o:o+cap]=b; cnt+=1
                if same: data['DUNGEON.BIN'][o:o+cap]=b
print('적용 위치',cnt)

# 잔여 패스: 추출에서 빠진 사본/짧은 문자열을 남은 가나 문자열 끝부분 일치로 메움
import re
J={x['ja']:t for i,t in ko.items() if t!=(x:=S[i])['ja'] and '{N}' not in x['ja']}
J.update(json.load(open('text/resid_ko.json',encoding='utf-8')))
pat=re.compile(rb'(?:[\x81-\x9f\xe0-\xea][\x40-\x7e\x80-\xfc]|\n)*(?:\x82[\x9f-\xf1]|\x83[\x40-\x96])(?:[\x81-\x9f\xe0-\xea][\x40-\x7e\x80-\xfc]|\n)*')
rc=0
for f,d in data.items():
    lim=0x53800 if f.startswith('SLPM') else len(d)
    for m in list(pat.finditer(bytes(d[:lim]))):
        try: t=m.group().decode('cp932')
        except UnicodeDecodeError: continue
        for k in range(len(t)):
            s=t[k:]
            for c in (s,s.rstrip('\n')):
                if c in J and (len(c)>=3 or k==0 and c==t):
                    o=m.start()+len(t[:k].encode('cp932')); l=len(c.encode('cp932'))
                    # DUNGEON 압축 데이터 속 우연한 일치 방지: 앞(문자열 시작일 때)·뒤 바이트가 제어 코드여야 함
                    if f=='DUNGEON.BIN' and (o+l>=len(d) or d[o+l]>=0x20 or (k==0 and d[o-1]>=0x20 and d[o-1]!=0x80)): continue
                    d[o:o+l]=fit(J[c],l,o+l<len(d) and d[o+l]==0); rc+=1; break
            else: continue
            break
print('잔여 적용',rc)
# 가나 없는 짧은 한자 라벨(도감 서식지 등): 앞뒤가 널인 정확한 일치만
for f in ('TOWN.BIN','DUNGEON.BIN','SLPM_860.47','MAIN.BIN'):
    d=data[f]; o=open('orig/'+f,'rb').read()
    for k,v in J.items():
        kb=k.encode('cp932')
        if len(v)*2>len(kb): continue
        p=o.find(kb)
        while p>=0:
            # 4바이트 정렬 또는 앞이 널, 뒤가 널인 독립 문자열만
            if (p%4==0 or o[p-1]==0) and o[p+len(kb)]==0 and d[p:p+len(kb)]==kb and (p<0x53800 or not f.startswith('SLPM')) and not any(b<=p<b+0x8000 for b in (0x235000,0x1830000)):
                d[p:p+len(kb)]=fit(v,len(kb),True); rc+=1
            p=o.find(kb,p+1)
# 옵션 화면 한 글자 라벨(MAIN 0x230fc~)
for i,c in enumerate('청녹적대소'): data['MAIN.BIN'][0x230fc+4*i:0x230fe+4*i]=fit(c,2,True)
print('라벨 포함',rc)

# 던전 메시지(문자표 모드)
import dmsg
DJ=json.load(open('text/dmsg_ja.json',encoding='utf-8'))
ends=[x['off'] for x in DJ[1:]]+[DJ[-1]['off']+DJ[-1]['len']]
tb=dmsg.build(data['DUNGEON.BIN'],[{'off':x['off'],'cap':e-x['off'],'ko':k['ko']} for x,e,k in zip(DJ,ends,DK)],cmap)
print('던전 메시지 문자표',len(tb))

# 압축 블록(던전 메뉴/명령 설명)
import klz
for a in (0xf824,0x4a3014,0x4a7014):
    d=data['DUNGEON.BIN']; od=open('orig/DUNGEON.BIN','rb').read()
    b,p=klz.dec(od,a); b=bytearray(b); clen=p-a; n=0
    for k,v in KB.items():
        kb=k.encode('cp932'); i=b.find(kb)
        while i>=0:
            e=i+len(kb)
            if e<len(b) and b[e] in (0,10) and (i==0 or b[i-1]<0x20 or b[i-1] in (0x70,0x80,0x32,0xff,0x5,0x0a)):
                cap=len(kb)
                if b[e]==0:
                    z=e
                    while z<len(b) and b[z]==0: z+=1
                    cap=z-i-1 if z<len(b) else len(kb)
                    cap=max(cap,len(kb))
                eb=enc(v)
                if len(eb)>cap: print('KB 초과',k,v,len(eb),cap)
                else: b[i:i+cap]=eb+bytes(cap-len(eb)) if b[e]==0 else eb+bytes([0x81,0x40])*((cap-len(eb))//2)+b' '*((cap-len(eb))%2); n+=1
            i=b.find(kb,i+1)
    c=klz.enc(bytes(b)); assert klz.dec(c,0)[0]==bytes(b)
    print('압축블록',hex(a),n,'크기',len(c),'/',clen)
    if len(c)>clen: print('  !! 압축 초과 - 원본 유지')
    else: d[a:a+clen]=c+bytes(clen-len(c))

# 그래픽(텍스처) 한글화
import gfxedit,gfxspec
gfxedit.run(data,gfxspec.SPEC)

# 이름 입력: '한자' 모드를 한글 음절표로 (43그룹 머리글자 + 46칸 라벨 + 끝 코드)
import struct
NG=44
starts=[round(k*len(chars)/NG) for k in range(NG)]
for f,base in (('TOWN.BIN',0x235000),('DUNGEON.BIN',0x1830000)):
    d=data[f]
    menu='かな\nカナ\n漢字\n英数\n記号\n辞書\n消去\n後退\n終了'.encode('cp932')
    assert d[base:base+len(menu)]==menu
    d[base:base+len(menu)]=enc(MENU)
    heads=bytes.fromhex('889f88c88945')
    h=d.find(heads,base,base+0x8000); assert h>0
    for k,s in enumerate(starts): d[h+2*k:h+2*k+2]=code_for(s).to_bytes(2,'big')
    lab='あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもや　ゆ　よらりるれろわ'.encode('cp932')
    l=d.find(lab,base,base+0x8000); assert l>0
    cells=iter(chars[s] for s in starts); out=b''
    for k in range(0,len(lab),2):
        out+=lab[k:k+2] if lab[k:k+2]==b'\x81\x40' else cmap[next(cells)].to_bytes(2,'big')
    d[l:l+len(lab)]=out
    end=code_for(len(chars))
    for off,reg in ((0x214,0x12),(0x2f4,0x11)):
        assert d[base+off:base+off+4]==bytes([0x73,0x98,reg,0x34])
        d[base+off:base+off+2]=end.to_bytes(2,'little')

# 2) 폰트 + 실행파일
gl=[tobytes(glyph(c))[2:28] for c in chars]
exe,cap=build_exe(bytes(data['SLPM_860.47']),gl)
print('폰트 용량',len(gl),'/',cap)
data['SLPM_860.47'][:len(exe)]=exe

# 3) 디스크 이미지
if not os.path.exists(OUT) or os.path.getmtime(OUT)<os.path.getmtime(ORIG):
    shutil.copyfile(ORIG,OUT)
w=Writer(OUT)
for f,p in PATHS.items():
    print(f,'섹터',w.patch(p,bytes(data[f])))
cue=os.path.splitext(OUT)[0]+'.cue'
open(cue,'w').write(f'FILE "{os.path.basename(OUT)}" BINARY\n  TRACK 01 MODE2/2352\n    FLAGS DCP\n    INDEX 01 00:00:00\n')
json.dump({c:'%04x'%v for c,v in cmap.items()},open('text/cmap.json','w',encoding='utf-8'),ensure_ascii=False)
