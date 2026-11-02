# 상태 이어가며 진행: adv.py state "seq" iters outprefix
import sys,os,time,shutil,subprocess,glob
st,seq,n,pre=sys.argv[1],sys.argv[2],int(sys.argv[3]),sys.argv[4]
cue='../Other Life Azure Dreams (Japan) [KOR].cue'
SV='duck/savestates/SLPM-86047_1.sav'
cur=st
for it in range(n):
    for tr in range(3):
        subprocess.run('taskkill /F /IM tw_duck.exe',shell=True,capture_output=True)
        t0=os.path.getmtime(SV) if os.path.exists(SV) else 0
        out=f'{pre}{it}_'
        try: subprocess.run([sys.executable,'tools/play.py',cur,seq+' SAVE S',out,cue],timeout=240,capture_output=True)
        except subprocess.TimeoutExpired: pass
        subprocess.run('taskkill /F /IM tw_duck.exe',shell=True,capture_output=True)
        if os.path.exists(SV) and os.path.getmtime(SV)>t0:
            cur=f'tmp/adv{it%2}.sav'; shutil.copyfile(SV,cur); break
    else:
        print('fail at',it); break
    print('iter',it,'ok',flush=True)
print('last',cur)
