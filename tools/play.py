# usage: play.py state|- "seq" outprefix [cue]
import sys,time; sys.path.insert(0,'tools'); from emu import Emu,hold
st=None if sys.argv[1]=='-' else sys.argv[1]
cue=sys.argv[4] if len(sys.argv)>4 else '../Other Life Azure Dreams (Japan).cue'
e=Emu(cue,state=st)
time.sleep(3)
if 'FONT' in sys.argv[2].split():
    # 현재 빌드의 폰트/후킹 영역을 RAM에 주입(이전 빌드 상태 파일 사용 시)
    import build_exe as B
    from iso import Disc
    dd=Disc(cue.replace('.cue','.bin')); F={q:(l,z) for q,l,z,_,_ in dd.walk()}
    l,z=F['/SLPM_860.47']; img=dd.read(l,z)
    for a0,a1 in ((B.C0,B.END0),(B.C1,B.END1)):
        off=0x800+a0-B.ORG; e.write(a0,img[off:off+(a1-a0)])
    if 'DMSG' in sys.argv[2].split():
        l,z=F['/DUNGEON/DUNGEON.BIN']; dg=dd.read(l,z)
        e.write(0xfd484+0x7ffe6890,dg[0xfd484:0xfe163])
n=0
for tok in sys.argv[2].split():
    if tok.startswith('w'): time.sleep(float(tok[1:]))
    elif tok=='S': e.shot(f'{sys.argv[3]}{n}.png'); n+=1
    elif tok in ('RESUME','FONT','DMSG'): pass
    elif tok=='SAVE':
        import os
        sv='duck/savestates/SLPM-86047_1.sav'; t0=os.path.getmtime(sv) if os.path.exists(sv) else 0
        for _ in range(6):
            e.savestate(); time.sleep(2.5)
            if os.path.exists(sv) and os.path.getmtime(sv)>t0: break
    elif tok.startswith('D'): open(tok[1:],'wb').write(e.read(0x80000000,0x200000))
    elif tok.startswith('H'):
        k,_,t=tok[1:].partition(':'); hold(e,k,float(t))
    else:
        k,_,rep=tok.partition('*')
        for i in range(int(rep or 1)): e.key(k,0.1); time.sleep(0.35)
e.close_save() if 'RESUME' in sys.argv[2].split() else e.close()
