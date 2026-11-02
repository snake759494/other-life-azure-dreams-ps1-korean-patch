# 압축 텍스처의 일본어 글자를 한글로 다시 그림
import os; os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","tmp"),exist_ok=True)
import sys,os,json,numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import klz,gfx
from PIL import Image,ImageDraw,ImageFont
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def F(name,size): return ImageFont.truetype(os.path.join(B,name) if not os.path.isabs(name) else name,size)
NB='../NanumSquareNeo-dEb.ttf'; NR='../NanumSquareNeo-cBd.ttf'; SH='../SeoulHangangEB.ttf'; G7='fonts/Galmuri7.ttf'; G9='fonts/Galmuri9.ttf'
def to_idx(b,w,h,bpp):
    if bpp==4:
        v=np.frombuffer(b[:w*h*2],np.uint16).reshape(h,w)
        return np.stack([(v>>(4*i))&15 for i in range(4)],-1).reshape(h,w*4).astype(np.int32)
    return np.frombuffer(b[:w*h*2],np.uint8).reshape(h,w*2).astype(np.int32)
def from_idx(a,bpp):
    if bpp==4:
        h,W=a.shape; a=a.reshape(h,W//4,4)
        return (a[...,0]|a[...,1]<<4|a[...,2]<<8|a[...,3]<<12).astype('<u2').tobytes()
    return a.astype(np.uint8).tobytes()
def mask(text,font,box,shear=0,stroke=0,align='c',dy=0):
    x0,y0,x1,y1=box; W=x1-x0; H=y1-y0
    S=4; f=ImageFont.truetype(font.path,font.size*S)
    im=Image.new('L',(W*S*2,H*S*2)); d=ImageDraw.Draw(im)
    bb=d.textbbox((0,0),text,font=f,stroke_width=stroke*S)
    tw=bb[2]-bb[0]; th=bb[3]-bb[1]
    ox=(W*S-tw)//2 if align=='c' else 0
    d.text((ox-bb[0]+W*S//2,(H*S-th)//2-bb[1]+dy*S),text,font=f,fill=255,stroke_width=stroke*S,stroke_fill=255)
    if shear: im=im.transform(im.size,Image.AFFINE,(1,shear,-shear*im.height/2,0,1,0),Image.BICUBIC)
    im=im.crop((W*S//2,0,W*S//2+W*S,H*S)).resize((W,H),Image.LANCZOS)
    return np.array(im,float)/255
def run(data,spec):
    """data: {파일:bytearray}, spec: [{f,addr,bpp,ops:[...]}]"""
    for s in spec:
        d=data[s['f']]; od=open(os.path.join(B,'orig',s['f']),'rb').read()
        e=[x for x in gfx.scan(od) if x['blk']+x['off']==s['addr']][0]
        b,end=klz.dec(od,s['addr']); clen=end-s['addr']
        offs=sorted(x['off'] for x in gfx.entries(od,e['blk']))
        nxt=[o for o in offs if o>e['off']]
        space=(e['blk']+nxt[0]-s['addr']) if nxt else clen
        a=to_idx(b,e['w'],e['h'],s['bpp']); a0=a.copy()
        for op in s['ops']:
            x0,y0,x1,y1=op['box']
            if op.get('clear',True):
                reg=a[y0:y1,x0:x1]; keep=op.get('keep')
                if keep is not None: reg[~np.isin(reg,keep)]=op.get('bg',0)
                else: reg[:]=op.get('bg',0)
            if 'text' not in op: continue
            st=op['style']; fnt=F(op['font'],op['size'])
            m=mask(op['text'],fnt,op['box'],op.get('shear',0),0,op.get('align','c'),op.get('dy',0))
            reg=a[y0:y1,x0:x1]
            if st=='plain':   # fg, aa
                fg,aa=op['fg'],op.get('aa',op['fg'])
                reg[m>=0.55]=fg; reg[(m>=0.2)&(m<0.55)]=aa
            elif st=='outline':  # 안쪽 값 목록(밝기순), 외곽 값
                ms=mask(op['text'],fnt,op['box'],op.get('shear',0),op.get('stroke',1),op.get('align','c'),op.get('dy',0))
                reg[ms>=0.35]=op['edge']
                lv=op['inner']
                for k,t in enumerate(np.linspace(0.8,0.3,len(lv))):
                    pass
                q=np.clip(((1-m)*len(lv)).astype(int),0,len(lv)-1)
                sel=m>=0.3; reg[sel]=np.array(lv)[q[sel]]
            elif st=='texture':  # 원본 글자 픽셀 값을 샘플링
                ox0,oy0,ox1,oy1=op.get('src',op['box'])
                pool=a0[oy0:oy1,ox0:ox1]; pool=pool[pool!=op.get('bg',0)]
                ms=mask(op['text'],fnt,op['box'],op.get('shear',0),op.get('stroke',1),op.get('align','c'),op.get('dy',0))
                eg=op['edge']
                if eg=='auto':
                    o=a0[oy0:oy1,ox0:ox1]; nz=o!=op.get('bg',0)
                    bd=nz&~(np.roll(nz,1,0)&np.roll(nz,-1,0)&np.roll(nz,1,1)&np.roll(nz,-1,1))
                    vals,cn=np.unique(o[bd],return_counts=True); eg=int(vals[cn.argmax()])
                reg[ms>=0.35]=eg
                ys,xs=np.where(m>=0.4)
                reg[ys,xs]=pool[(xs*7+ys*13)%len(pool)]
        nb=bytearray(b); raw=from_idx(a,s['bpp']); nb[:len(raw)]=raw
        c=klz.enc(bytes(nb)); assert klz.dec(c,0)[0]==bytes(nb)
        ok=len(c)<=space
        print('그래픽',s['f'],hex(s['addr']),len(c),'/',space,'OK' if ok else '초과')
        if ok: d[s['addr']:s['addr']+len(c)]=c
        import hashlib
        H=json.load(open(os.path.join(B,'tools','gfxhash.json')))
        for f2,a2 in H.get(hashlib.md5(b).hexdigest(),[]):
            if (f2,a2)==(s['f'],s['addr']) or f2 not in data: continue
            od2=open(os.path.join(B,'orig',f2),'rb').read()
            e2=[x for x in gfx.scan(od2) if x['blk']+x['off']==a2][0]
            _,end2=klz.dec(od2,a2); offs2=sorted(x['off'] for x in gfx.entries(od2,e2['blk']))
            n2=[o for o in offs2 if o>e2['off']]; sp2=(e2['blk']+n2[0]-a2) if n2 else end2-a2
            print('  사본',f2,hex(a2),'OK' if len(c)<=sp2 else '초과')
            if len(c)<=sp2: data[f2][a2:a2+len(c)]=c
        # 미리보기
        Image.fromarray((a*(17 if s['bpp']==4 else 1)).astype(np.uint8)).save(os.path.join(B,'tmp','gfx_%s_%x.png'%(s['f'][:2],s['addr'])))
