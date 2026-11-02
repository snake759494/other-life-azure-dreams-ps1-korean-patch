# 압축 컨테이너 엔트리 목록
import struct,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import klz
def entries(d,a):
    out=[];p=a
    while p+16<=len(d):
        t,h,off,x,y,w,hh=struct.unpack_from('<HHIHHHH',d,p)
        if h!=0x10 or t==0 or t>16: break
        out.append(dict(t=t,blk=a,off=off,x=x,y=y,w=w,h=hh)); p+=16
    return out
def scan(d):
    res=[]
    for a in range(0,len(d),0x800):
        t,h=struct.unpack_from('<HH',d,a)
        if h==0x10 and 0<t<16: res+=entries(d,a)
    return res
