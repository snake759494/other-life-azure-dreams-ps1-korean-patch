# 원본 디스크에서 빌드에 쓰는 파일 4개를 orig/로 추출: python tools/extract_orig.py "../Other Life Azure Dreams (Japan).bin"
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from iso import Disc
WANT={'MAIN.BIN','TOWN.BIN','DUNGEON.BIN','SLPM_860.47'}
d=Disc(sys.argv[1]); os.makedirs('orig',exist_ok=True)
for p,l,sz,_,_ in d.walk():
    n=p.split('/')[-1].split(';')[0]
    if n in WANT:
        open(os.path.join('orig',n),'wb').write(d.read(l,sz)); print(n,sz)
