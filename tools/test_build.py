import sys; sys.path.insert(0,'tools')
from build_exe import build,code_for
from font import glyph,tobytes
from disc import Writer
txt=sys.argv[1] if len(sys.argv)>1 else '안녕, 정신이 들었니?'
chars=sorted(set(c for c in txt if c not in ' '))
cmap={c:code_for(i) for i,c in enumerate(chars)}
gl=[tobytes(glyph(c))[2:28] for c in chars]
exe=open('orig/SLPM_860.47','rb').read()
img,cap=build(exe,gl)
w=Writer('tmp/test.bin')
print('exe secs',w.patch('/SLPM_860.47',img.ljust(0x200000,b'\0')[:len(exe)] if False else img+exe[len(img):]))
def enc(s):
    return b''.join(b'\x81\x40' if c==' ' else cmap[c].to_bytes(2,'big') for c in s)
d=open('orig/TOWN.BIN','rb').read(); n=bytearray(d)
src='やあ、気が付いたかい？'.encode('cp932')
rep=enc(txt).ljust(len(src),b'\0')[:len(src)]
rep=enc(txt)+b'\x81\x40'*((len(src)-len(enc(txt)))//2)
i=d.find(src)
while i>=0: n[i:i+len(src)]=rep; i=d.find(src,i+1)
print('town secs',w.patch('/TOWN/TOWN.BIN',bytes(n),d))
