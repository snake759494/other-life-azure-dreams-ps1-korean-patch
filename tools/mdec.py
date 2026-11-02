# PSX STR v2 프레임 디코드/인코드 (계수 단위)
import math
T='''11:0/1 011:1/1 0100:0/2 0101:2/1 00101:0/3 00111:3/1 00110:4/1 000110:1/2 000111:5/1 000101:6/1 000100:7/1
0000110:0/4 0000100:2/2 0000111:8/1 0000101:9/1 00100110:0/5 00100001:0/6 00100101:1/3 00100100:3/2 00100111:10/1
00100011:11/1 00100010:12/1 00100000:13/1 0000001010:0/7 0000001100:1/4 0000001011:2/3 0000001111:4/2 0000001001:5/2
0000001110:14/1 0000001101:15/1 0000001000:16/1 000000011101:0/8 000000011000:0/9 000000010011:0/10 000000010000:0/11
000000011011:1/5 000000010100:2/4 000000011100:3/3 000000010010:4/3 000000011110:6/2 000000010101:7/2 000000010001:8/2
000000011111:17/1 000000011010:18/1 000000011001:19/1 000000010111:20/1 000000010110:21/1 0000000011010:0/12
0000000011001:0/13 0000000011000:0/14 0000000010111:0/15 0000000010110:1/6 0000000010101:1/7 0000000010100:2/5
0000000010011:3/4 0000000010010:5/3 0000000010001:9/2 0000000010000:10/2 0000000011111:22/1 0000000011110:23/1
0000000011101:24/1 0000000011100:25/1 0000000011011:26/1 00000000011111:0/16 00000000011110:0/17 00000000011101:0/18
00000000011100:0/19 00000000011011:0/20 00000000011010:0/21 00000000011001:0/22 00000000011000:0/23 00000000010111:0/24
00000000010110:0/25 00000000010101:0/26 00000000010100:0/27 00000000010011:0/28 00000000010010:0/29 00000000010001:0/30
00000000010000:0/31 000000000011000:0/32 000000000010111:0/33 000000000010110:0/34 000000000010101:0/35
000000000010100:0/36 000000000010011:0/37 000000000010010:0/38 000000000010001:0/39 000000000010000:0/40
000000000011111:1/8 000000000011110:1/9 000000000011101:1/10 000000000011100:1/11 000000000011011:1/12
000000000011010:1/13 000000000011001:1/14 0000000000010011:1/15 0000000000010010:1/16 0000000000010001:1/17
0000000000010000:1/18 0000000000010100:6/3 0000000000011010:11/2 0000000000011001:12/2 0000000000011000:13/2
0000000000010111:14/2 0000000000010110:15/2 0000000000010101:16/2 0000000000011111:27/1 0000000000011110:28/1
0000000000011101:29/1 0000000000011100:30/1 0000000000011011:31/1'''
DEC={}; ENC={}
for t in T.split():
    c,rl=t.split(':'); r,l=map(int,rl.split('/')); DEC[c]=(r,l); ENC[(r,l)]=c
ZZ=[0,1,8,16,9,2,3,10,17,24,32,25,18,11,4,5,12,19,26,33,40,48,41,34,27,20,13,6,7,14,21,28,35,42,49,56,57,50,43,36,29,22,15,23,30,37,44,51,58,59,52,45,38,31,39,46,53,60,61,54,47,55,62,63]
QT=[2,16,19,22,26,27,29,34,16,16,22,24,27,29,34,37,19,22,26,27,29,34,34,38,22,22,26,27,29,34,37,40,22,26,27,29,32,35,40,48,26,27,29,32,35,40,48,58,26,27,29,34,38,46,56,69,27,29,35,38,46,56,69,83]
class BR:
    def __init__(s,b): s.b=b; s.p=0; s.v=0; s.n=0
    def bits(s,k):
        r=0
        for _ in range(k):
            if s.n==0:
                s.v=s.b[s.p]|s.b[s.p+1]<<8; s.p+=2; s.n=16
            s.n-=1; r=r<<1|((s.v>>s.n)&1)
        return r
def sx(v,n): return v-(1<<n) if v&(1<<(n-1)) else v
def decode(frame,w,h):
    """frame: 데모드 데이터. 반환 qs,[MB][6블록][(run,level)...], dc 포함 (블록=[dc,[(r,l)]])"""
    q=frame[4]|frame[5]<<8; ver=frame[6]|frame[7]<<8; assert ver==2,ver
    br=BR(frame[8:]); mbs=[]
    for _ in range(((w+15)//16)*((h+15)//16)):
        mb=[]
        for b in range(6):
            dc=sx(br.bits(10),10); ac=[]
            while True:
                c=''
                while True:
                    c+=str(br.bits(1))
                    if c=='10': break
                    if c=='000001': break
                    if c in DEC and not (c=='11' and False): break
                    if len(c)>16: raise ValueError('vlc')
                if c=='10': break
                if c=='000001':
                    r=br.bits(6); l=sx(br.bits(10),10); ac.append((r,l)); continue
                r,l=DEC[c]; s=br.bits(1); ac.append((r,-l if s else l))
            mb.append([dc,ac])
        mbs.append(mb)
    return q,mbs
def idct8(blk):
    out=[0.0]*64
    C=[[ (math.sqrt(0.125) if u==0 else 0.5)*math.cos((2*x+1)*u*math.pi/16) for x in range(8)] for u in range(8)]
    tmp=[[sum(C[u][x]*blk[v*8+u] for u in range(8)) for x in range(8)] for v in range(8)]
    return [[sum(C[v][y]*tmp[v][x] for v in range(8)) for x in range(8)] for y in range(8)]
def coefs(b,q):
    blk=[0.0]*64; blk[0]=b[0]*QT[0]; i=0
    for r,l in b[1]:
        i+=r+1
        if i>63: break
        z=ZZ[i]; blk[z]=(l*QT[z]*q)/8
    return blk
def fdct8(px):
    C=[[ (math.sqrt(0.125) if u==0 else 0.5)*math.cos((2*x+1)*u*math.pi/16) for x in range(8)] for u in range(8)]
    tmp=[[sum(C[u][x]*px[y][x] for x in range(8)) for u in range(8)] for y in range(8)]
    return [sum(C[v][y]*tmp[y][u] for y in range(8)) for v in range(8) for u in range(8)]
def quant(px,q,maxac=63):
    F=fdct8(px); dc=int(round(F[0]/QT[0])); dc=max(-512,min(511,dc)); ac=[]; run=0
    for i in range(1,maxac+1):
        z=ZZ[i]; l=int(round(F[z]*8/(QT[z]*q)))
        l=max(-512,min(511,l))
        if l==0: run+=1
        else: ac.append((run,l)); run=0
    return [dc,ac]
class BW:
    def __init__(s): s.out=bytearray(); s.v=0; s.n=0
    def put(s,val,k):
        for i in range(k-1,-1,-1):
            s.v=s.v<<1|((val>>i)&1); s.n+=1
            if s.n==16: s.out+=s.v.to_bytes(2,'little'); s.v=0; s.n=0
    def code(s,c):
        for ch in c: s.put(int(ch),1)
    def flush(s):
        while s.n: s.put(0,1)
        return bytes(s.out)
def encode(q,mbs):
    bw=BW(); n=0
    for mb in mbs:
        for dc,ac in mb:
            bw.put(dc&0x3ff,10)
            for r,l in ac:
                k=(r,abs(l))
                if k in ENC: bw.code(ENC[k]); bw.put(1 if l<0 else 0,1)
                else: bw.code('000001'); bw.put(r,6); bw.put(l&0x3ff,10)
                n+=1
            bw.code('10'); n+=1
    bw.put(0x1ff,10)
    body=bw.flush()
    # MDEC 코드 수(32비트 단위 반올림) - 원본 헤더 필드: ((n+1)/2 를 32바이트 정렬)?
    return body,n
def ycc_to_rgb(mb_px):
    pass

import numpy as np
_C=np.array([[ (math.sqrt(0.125) if u==0 else 0.5)*math.cos((2*x+1)*u*math.pi/16) for x in range(8)] for u in range(8)])
def idct(blk64): B=np.array(blk64).reshape(8,8); return _C.T@B@_C
def fdct(px): return (_C@np.array(px,float)@_C.T).flatten()
def to_rgb(q,mbs,w,h):
    W=(w+15)//16*16; H=(h+15)//16*16
    Y=np.zeros((H,W)); Cb=np.zeros((H//2,W//2)); Cr=np.zeros((H//2,W//2))
    rows=H//16
    for i,mb in enumerate(mbs):
        mx=i//rows; my=i%rows
        bl=[idct(coefs(b,q)) for b in mb]
        Cr[my*8:my*8+8,mx*8:mx*8+8]=bl[0]; Cb[my*8:my*8+8,mx*8:mx*8+8]=bl[1]
        for k,(dy,dx) in enumerate(((0,0),(0,8),(8,0),(8,8))):
            Y[my*16+dy:my*16+dy+8,mx*16+dx:mx*16+dx+8]=bl[2+k]
    Y=Y+128; cr=Cr.repeat(2,0).repeat(2,1); cb=Cb.repeat(2,0).repeat(2,1)
    R=Y+1.402*cr; G=Y-0.344*cb-0.714*cr; B_=Y+1.772*cb
    return np.clip(np.stack([R,G,B_],-1),0,255).astype(np.uint8)[:h,:w]
def from_rgb(img,q,mask_mb=None,maxac=63):
    """img HxWx3 -> 매크로블록 목록 (mask_mb: 인코딩할 MB 인덱스 집합)"""
    H,W=img.shape[:2]; f=img.astype(float)
    Y=0.299*f[...,0]+0.587*f[...,1]+0.114*f[...,2]-128
    Cb=(f[...,2]-Y-128)/1.772; Cr=(f[...,0]-Y-128)/1.402
    cb=Cb.reshape(H//2,2,W//2,2).mean((1,3)); cr=Cr.reshape(H//2,2,W//2,2).mean((1,3))
    rows=H//16; out={}
    for i in range(rows*(W//16)):
        if mask_mb is not None and i not in mask_mb: continue
        mx=i//rows; my=i%rows
        bl=[cr[my*8:my*8+8,mx*8:mx*8+8],cb[my*8:my*8+8,mx*8:mx*8+8]]+[Y[my*16+dy:my*16+dy+8,mx*16+dx:mx*16+dx+8] for dy,dx in ((0,0),(0,8),(8,0),(8,8))]
        mb=[]
        for p in bl:
            F=fdct(p); dc=int(round(F[0]/QT[0])); ac=[]; run=0
            for k in range(1,maxac+1):
                z=ZZ[k]; l=int(round(F[z]*8/(QT[z]*q)))
                if l==0: run+=1
                else: ac.append((run,max(-512,min(511,l)))); run=0
            mb.append([max(-512,min(511,dc)),ac])
        out[i]=mb
    return out
