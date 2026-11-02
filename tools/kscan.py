import sys,re,json;sys.path.insert(0,'tools');import klz
pat=re.compile(rb'(?:[\x81-\x84\x88-\x9f\xe0-\xea][\x40-\x7e\x80-\xfc]){3,}')
res=[]
for f in ['DUNGEON.BIN','TOWN.BIN','MAIN.BIN','SLPM_860.47','OVMOVIE.BIN']:
    try: d=open('orig/'+f,'rb').read()
    except: continue
    for a in range(0,len(d),0x800):
        for k in range(0,0x40,4):
            try: b,p=klz.dec(d,a+k,0x100000)
            except Exception: continue
            if len(b)<0x100 or p-(a+k)<0x40: continue
            n=sum(1 for m in pat.finditer(b))
            res.append((f,a+k,p-(a+k),len(b),n)); break
    print(f,len([r for r in res if r[0]==f]),file=sys.stderr)
json.dump(res,open('tmp/kblocks.json','w'))
