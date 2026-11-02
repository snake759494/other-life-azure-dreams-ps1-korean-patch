# 테스트 이미지: KOR 이미지에서 지정 파일의 [lo,hi) 구간만 원본으로 되돌림
import sys,os,shutil
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from disc import Writer
KOR='../Other Life Azure Dreams (Japan) [KOR].bin'
fs=sys.argv[1].split(','); lo=int(sys.argv[2],16); hi=int(sys.argv[3],16)
if not os.path.exists('tmp/test.bin'): shutil.copyfile(KOR,'tmp/test.bin')
w=Writer('tmp/test.bin')
# 먼저 KOR 상태로 복원(전 파일), 다음 구간 원본
import iso
k=iso.Disc(KOR); K={p:(l,s) for p,l,s,_,_ in k.walk()}
P={'TOWN.BIN':'/TOWN/TOWN.BIN','DUNGEON.BIN':'/DUNGEON/DUNGEON.BIN','MAIN.BIN':'/MAIN/MAIN.BIN','SLPM_860.47':'/SLPM_860.47'}
for name,p in P.items():
    l,s=K[p]; cur=bytearray(k.read(l,s))
    if name in fs:
        o=open('orig/'+name,'rb').read(); cur[lo:hi]=o[lo:hi]
    print(name,w.patch(p,bytes(cur)))
open('tmp/test.cue','w').write('FILE "test.bin" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
