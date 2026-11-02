import sys,re,struct,collections
d=open(sys.argv[1],'rb').read()
lo=int(sys.argv[2],16); hi=int(sys.argv[3],16)
pat=re.compile(rb'(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]){2,}')
starts=set(m.start() for m in pat.finditer(d,lo,hi) if m.start()%4==0 or d[m.start()-1]==0)
vals=collections.Counter()
ptrs=[struct.unpack_from('<I',d,i)[0] for i in range(0,len(d)-3,4)]
sp=set(p for p in ptrs if 0x80000000<=p<0x80200000)
c=collections.Counter()
for s in starts:
    for p in sp:
        b=p-s
        if (b&0x7ff)==0 or True: c[b]+=1
print([(hex(b),n) for b,n in c.most_common(8)])
