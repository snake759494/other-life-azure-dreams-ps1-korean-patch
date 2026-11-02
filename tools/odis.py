import sys,capstone
f,base,ram=sys.argv[1],int(sys.argv[2],16),int(sys.argv[3],16)
a=int(sys.argv[4],16); n=int(sys.argv[5])
d=open('orig/'+f,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32+capstone.CS_MODE_LITTLE_ENDIAN)
off=base+(a-ram)
for i in md.disasm(d[off:off+n*4],a): print(hex(i.address),i.mnemonic,i.op_str)
