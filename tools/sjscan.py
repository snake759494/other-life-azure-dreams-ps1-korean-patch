import sys,re
d=open(sys.argv[1],'rb').read(); mn=int(sys.argv[2]) if len(sys.argv)>2 else 6
pat=re.compile(rb'(?:[\x81-\x9f\xe0-\xef][\x40-\x7e\x80-\xfc]){%d,}'%mn)
n=0;tot=0
for m in pat.finditer(d):
    tot+=1
    if n<int(sys.argv[3] if len(sys.argv)>3 else 30):
        try: print(hex(m.start()),m.group().decode('cp932')[:60]); n+=1
        except: pass
print('total',tot)
