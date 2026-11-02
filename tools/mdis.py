import sys,capstone
d=open('orig/SLPM_860.47','rb').read()
def dis(addr,n):
    off=addr-0x8002e800+0x800
    md=capstone.Cs(capstone.CS_ARCH_MIPS,capstone.CS_MODE_MIPS32+capstone.CS_MODE_LITTLE_ENDIAN)
    for i in md.disasm(d[off:off+n*4],addr): print(hex(i.address),i.mnemonic,i.op_str)
dis(int(sys.argv[1],16),int(sys.argv[2]))
