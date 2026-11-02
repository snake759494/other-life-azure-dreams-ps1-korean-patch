# 오프닝(LOP2) 자막 교체: 하단 MB 행만 재인코딩해 KOR 이미지 섹터에 직접 기록
import sys,os,json,struct,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import str as S,mdec
from disc import Writer
from cdsec import form1
from iso import SEC
from PIL import Image,ImageDraw,ImageFont
OUT=sys.argv[1]
L=json.load(open('text/movie_ko.json',encoding='utf-8'))
FONT=ImageFont.truetype('../NanumSquareNeo-bRg.ttf',12)
def render(t):
    im=Image.new('L',(320,16)); d=ImageDraw.Draw(im)
    w=d.textlength(t,font=FONT); d.text(((320-w)/2,2),t,font=FONT,fill=235)
    return np.array(im,float)
R=[render(t) for t in L]
w=Writer(OUT); lba,size=w.files['/STR/LOP2_WS.STR'][1:3]
from iso import Disc
fr=S.frames(Disc('../Other Life Azure Dreams (Japan).bin'),lba,size)
segs=json.load(open('tools/movie_segs.json'))
assert len(segs)==len(L)
P=[]  # 세그먼트 기준 원본 밴드
cnt=0
ONLY=set(map(int,sys.argv[2].split(','))) if len(sys.argv)>2 else None
for i,f in enumerate(fr):
    if ONLY and i not in ONLY: continue
    q,m=mdec.decode(f['data'],320,192)
    img=mdec.to_rgb(q,m,320,192)
    band=img[176:192].max(2).astype(float)
    if band.max()<40: continue
    cand=[k for k,s in enumerate(segs) if s['start']-8<=i<=s['end']+8]
    if not cand: continue
    A=np.stack([s['ref'] for s in (segs[k] for k in cand)],1) if False else None
    refs=[np.array(segs[k]['refimg'],float) if 'refimg' in segs[k] else None for k in cand]
    A=np.stack([r.flatten() for r in refs],1)
    wts,*_=np.linalg.lstsq(A,band.flatten(),rcond=None); wts=np.clip(wts,0,1.2)
    new=sum(wt*R[k] for wt,k in zip(wts,cand))
    img=img.copy(); img[176:192]=np.clip(new,0,255)[...,None].repeat(3,2)
    bot={j for j in range(240) if j%12==11}
    cap=f['cc']*2016
    for mx in (63,40,28,20,14,10):
        nm=mdec.from_rgb(img.astype(np.uint8),q,bot,mx)
        for j,mb in nm.items(): m[j]=mb
        body,n=mdec.encode(q,m)
        hdr=struct.pack('<HHHH',((n+1440+1)//2+31)//32*32,0x3800,q,2)
        data=hdr+body
        if len(data)<=cap: break
    if len(data)>cap: print('초과',i,len(data),cap); continue
    data=data+bytes(cap-len(data))
    for c,sl in enumerate(f['secs']):
        sec=bytearray(w.sector(sl)); sec[24+32:24+2048]=data[c*2016:(c+1)*2016]
        struct.pack_into('<I',sec,24+12,len(hdr)+len(body)); form1(sec)
        w.f.seek(sl*SEC); w.f.write(sec)
    cnt+=1
print('자막 프레임',cnt)
