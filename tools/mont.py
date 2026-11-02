import sys
from PIL import Image
fs=sys.argv[2:]; out=sys.argv[1]
ims=[Image.open(f).convert('RGB').resize((320,240)) for f in fs]
c=4; r=(len(ims)+3)//4
o=Image.new('RGB',(320*c,240*r))
for i,m in enumerate(ims): o.paste(m,((i%c)*320,(i//c)*240))
o.save(out)
