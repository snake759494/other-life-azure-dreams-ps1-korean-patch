# 16x15 1bpp 한글 글리프 렌더링 (BIOS 폰트 형식: 행당 2바이트, 왼쪽=MSB)
from PIL import Image,ImageDraw,ImageFont
import numpy as np,os
BASE=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT=os.path.join(BASE,'NanumSquareNeo-cBd.ttf')
SIZE=14; TH=110
_f={}
def font(p=FONT,s=SIZE):
    if (p,s) not in _f: _f[(p,s)]=ImageFont.truetype(p,s*4)
    return _f[(p,s)]
def glyph(ch,p=FONT,s=SIZE,th=TH,yoff=0):
    f=font(p,s); S=4
    im=Image.new('L',(16*S,15*S),0); d=ImageDraw.Draw(im)
    # 가로 중앙, 세로: 한글 '한' 기준 박스 중앙
    bb=d.textbbox((0,0),'한',font=f)
    hb=d.textbbox((0,0),ch,font=f)
    x=(16*S-(hb[2]-hb[0]))//2-hb[0] if ch not in '，．、。' else S-hb[0]
    y=(15*S-(bb[3]-bb[1]))//2-bb[1]+yoff*S
    d.text((x,y),ch,font=f,fill=255)
    a=np.array(im.resize((16,15),Image.BOX))
    return (a>=th).astype(np.uint8)
GAL=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'fonts','Galmuri11.ttf')
_g=ImageFont.truetype(GAL,12)   # 갈무리11 원본 픽셀 크기(12px, 높이 11줄) 그대로
def glyph(ch):
    """갈무리11을 화면 공간(11x15)에 1:1로 그린 뒤, 게임의 가로 축소를 역산해 16폭으로 배치"""
    bb=ImageDraw.Draw(Image.new('L',(1,1))).textbbox((0,0),'한',font=_g)
    im=Image.new('L',(32,15),0); d=ImageDraw.Draw(im)
    d.text((8,2-bb[1]),ch,font=_g,fill=255)   # '한' 위끝을 2행에 → 화면 1~11행(저장 1~13행 중)
    a=(np.array(im)>=128).astype(np.uint8)
    xs=np.nonzero(a.any(0))[0]
    s=np.zeros((15,11),np.uint8)
    if len(xs):
        w=xs[-1]-xs[0]+1                  # 실제 잉크 폭 기준 가운데 정렬(구두점은 왼쪽)
        x=0 if ch in '，．、。' else max(0,(11-w)//2)
        s[:,x:x+min(w,11-x)]=a[:,xs[0]:xs[0]+min(w,11-x)]
    g=np.zeros((15,16),np.uint8); g[:,:11]=s   # 원본 픽셀 그대로(0~10열). 화면별 배치는 후킹 코드가 처리
    return g
def tobytes(g):
    out=b''
    for r in g:
        v=0
        for b in r: v=(v<<1)|int(b)
        out+=v.to_bytes(2,'big')
    return out
def bios(code):
    b=open(os.path.join(BASE,'work','duck','bios','SCPH5500.bin'),'rb').read()
    l,t=code>>8,code&0xff
    # Krom2RawAdd 계산(레벨1 한자 영역)
    if 0x889f<=code<=0x9872:
        idx=(l-0x88)*188+(t-0x40-(1 if t>0x7f else 0))-0x5f
        off=0x66000+0x2e20+idx*30  # 대략값, show용
    return None
