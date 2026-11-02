# 디스크 이미지에서 파일 내용을 섹터 단위로 덮어쓰기 (변경된 섹터만, 서브헤더 유지, EDC/ECC 재계산)
import os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from cdsec import form1
from iso import Disc,SEC

class Writer(Disc):
    def __init__(s,p):
        s.f=open(p,'r+b'); s.files={x[0]:x for x in s.walk()}
    def patch(s,path,new,old=None):
        _,lba,size,_,_=s.files[path]
        assert len(new)<=((size+2047)//2048)*2048, path
        n=0
        for i in range(0,len(new),2048):
            nd=new[i:i+2048]
            if old is not None and old[i:i+2048]==nd: continue
            sec=bytearray(s.sector(lba+i//2048))
            if bytes(sec[24:24+len(nd)])==nd: continue
            sec[24:24+len(nd)]=nd
            form1(sec); s.f.seek((lba+i//2048)*SEC); s.f.write(sec); n+=1
        return n
