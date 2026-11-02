import sys,time; sys.path.insert(0,'tools'); from emu import Emu
e=Emu('../Other Life Azure Dreams (Japan).cue')
for i in range(12):
    time.sleep(4); e.shot(f'shots/b{i}.png')
    if i>=3: e.press('start',0.5); e.press('o',0.5)
e.savestate(); time.sleep(2)
e.close()
