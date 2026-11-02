# 던전 메시지 압축 해제 실험
import sys
def dec(d,p,var,maxout=0x8000,msb=False):
    out=bytearray()
    while len(out)<maxout and p<len(d):
        fl=d[p];p+=1
        for k in range(8):
            bit=(fl>>(7-k))&1 if msb else (fl>>k)&1
            if p>=len(d): break
            if bit==(0 if var[1] else 1) if False else (bit==var[1]):
                out.append(d[p]);p+=1
            else:
                b0,b1=d[p],d[p+1];p+=2
                if var[0]=='A': v=b0|b1<<8; off=v&0xfff; ln=(v>>12)+3; dist=off
                elif var[0]=='A2': v=b0<<8|b1; off=v&0xfff; ln=(v>>12)+3; dist=off
                elif var[0]=='B': v=b0<<8|b1; off=v>>4; ln=(v&0xf)+3; dist=off
                elif var[0]=='C': v=b0|b1<<8; off=v>>4; ln=(v&0xf)+3; dist=off
                elif var[0]=='D': off=b0|((b1&0xf0)<<4); ln=(b1&0xf)+3; dist=None
                if dist is None:
                    # ring 0xfee
                    base=(len(out)+0xfee)&0xfff
                    s=len(out)-((base-off)&0xfff)
                else:
                    s=len(out)-dist-var[2]
                for i in range(ln):
                    out.append(out[s+i] if 0<=s+i<len(out) else 0)
    return bytes(out),p
def score(b):
    ok=0;i=0
    while i<len(b)-1:
        if b[i]==0x82 and 0x9f<=b[i+1]<=0xf1: ok+=1;i+=2
        else: i+=1
    return ok
if __name__=='__main__':
    d=open('orig/DUNGEON.BIN','rb').read()
    st=int(sys.argv[1],16)
    for v in [('A',1,0),('A',1,1),('A',0,0),('A',0,1),('A2',1,0),('A2',1,1),('B',1,0),('B',1,1),('C',1,0),('C',1,1),('D',1,0),('D',0,0)]:
        for msb in (False,True):
            try: o,p=dec(d,st,v,0x3000,msb)
            except Exception as e: continue
            print(v,msb,score(o),o[:120].decode('cp932','replace')[:60].replace('\n','/'))
