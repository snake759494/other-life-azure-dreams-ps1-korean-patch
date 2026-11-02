# play.py 재시도 래퍼: run.py state "seq" prefix
import sys,subprocess,glob,os
st,seq,pre=sys.argv[1:4]
cue='../Other Life Azure Dreams (Japan) [KOR].cue'
for t in range(3):
    for f in glob.glob(pre+'*.png'): os.remove(f)
    subprocess.run('taskkill /F /IM tw_duck.exe',shell=True,capture_output=True)
    try: r=subprocess.run([sys.executable,'tools/play.py',st,seq,pre,cue],timeout=400,capture_output=True)
    except subprocess.TimeoutExpired: pass
    subprocess.run('taskkill /F /IM tw_duck.exe',shell=True,capture_output=True)
    n=seq.split().count('S')
    if len(glob.glob(pre+'*.png'))>=max(1,n-1): break
print('shots',sorted(glob.glob(pre+'*.png'),key=lambda x:int(''.join(c for c in os.path.basename(x) if c.isdigit()) or 0)))
