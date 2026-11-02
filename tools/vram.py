import sys,zstandard
from PIL import Image
d=open(sys.argv[1],'rb').read()
i=d.find(b'\x28\xb5\x2f\xfd')
out=b''
dc=zstandard.ZstdDecompressor()
while i>=0:
    try:
        o=dc.decompressobj(); out+=o.decompress(d[i:]); 
    except Exception as ex: print('err',ex)
    i=d.find(b'\x28\xb5\x2f\xfd',i+4)
print(len(out))
r=open(sys.argv[2],'rb').read() if len(sys.argv)>2 else None
# RAM in state: locate
if r:
    j=out.find(r[0x30000:0x30100]); print('ram at',hex(j-0x30000))
open('tmp/state.raw','wb').write(out)
