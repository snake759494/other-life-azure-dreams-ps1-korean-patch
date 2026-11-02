import sys,zstandard,numpy as np
from PIL import Image
d=open(sys.argv[1],'rb').read()
out=b'';dc=zstandard.ZstdDecompressor();i=d.find(b'\x28\xb5\x2f\xfd')
while i>=0:
    try: out+=dc.decompressobj().decompress(d[i:])
    except Exception: pass
    i=d.find(b'\x28\xb5\x2f\xfd',i+4)
ram=out.find(b'PS-X')  # unused
# heuristic: locate RAM by exe code signature
sig=open('orig/SLPM_860.47','rb').read()[0x10800:0x10900]
j=out.find(sig)-(0x8003e800-0x80000000)
v=j+0x800000
a=np.frombuffer(out[v:v+0x100000],dtype='<u2').reshape(512,1024)
rgb=np.stack([(a&31)<<3,((a>>5)&31)<<3,((a>>10)&31)<<3],-1).astype('uint8')
used=(a!=0)
Image.fromarray(rgb).save(sys.argv[2])
np.save(sys.argv[2]+'.npy',a)
