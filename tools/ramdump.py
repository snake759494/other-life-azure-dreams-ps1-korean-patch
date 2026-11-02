import sys,time; sys.path.insert(0,'tools'); from emu import Emu
e=Emu('../Other Life Azure Dreams (Japan).cue',state=sys.argv[1])
time.sleep(4); e.shot('tmp/rd.png')
open(sys.argv[2],'wb').write(e.read(0x80000000,0x200000)); e.close()
