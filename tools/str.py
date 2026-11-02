# STR 파일 프레임 단위 읽기/쓰기 (디스크 섹터 직접)
import struct,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from iso import Disc
def frames(dd,lba,size):
    """프레임 목록: {num,w,h,secs:[lba..],data}"""
    n=size//2048; fr={}
    for i in range(n):
        s=dd.sector(lba+i)
        if s[18]&0x08 and s[24:26]==b'\x60\x01':
            ci,cc,fn,fs,w,h=struct.unpack_from('<HHIIHH',s,24+4)
            f=fr.setdefault(fn,{'num':fn,'w':w,'h':h,'cc':cc,'size':fs,'secs':[None]*cc})
            f['secs'][ci]=lba+i
    out=[]
    for fn in sorted(fr):
        f=fr[fn]; f['data']=b''.join(dd.sector(x)[24+32:24+2048] for x in f['secs'])
        out.append(f)
    return out
