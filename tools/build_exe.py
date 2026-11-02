# SLPM 실행파일 패치: 한글 폰트 + Krom2RawAdd 후킹
#  - 더블 패킷 버퍼 각각의 끝 STEAL 바이트를 줄여(오버플로 검사 한도 변경) 그 자리에 폰트/코드 배치
#  - 실행파일 로드 크기를 늘려 부팅 시 폰트가 함께 RAM에 올라가게 함
import struct,sys,os
import keystone
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
ORG=0x8002e800
END0=0x801dad7a; END1=0x801eb64e      # 원래 패킷 버퍼 한도
STEAL=0x5000
LIM0=END0-STEAL; LIM1=END1-STEAL
GUARD=0x1400                            # 데모 등에서 한도를 넘겨 쓰는 패킷(약 3KB) 대비 여유
C0=(LIM0+GUARD+0xf)&~0xf; C1=(LIM1+GUARD+0xf)&~0xf
# 대화창 변환(0x80050948)은 이웃 픽셀 무늬로 점프 테이블을 찾는데, 원래 글꼴에 없는 무늬면
# 멈출 수 있음 → 변환에는 원래 형태로 펼친 글리프를 주고, 출력은 감싸기 코드가 원본 비트로 다시 씀
GB=26                                   # 글리프당 바이트(행 1~13)
ks=keystone.Ks(keystone.KS_ARCH_MIPS,keystone.KS_MODE_MIPS32+keystone.KS_MODE_LITTLE_ENDIAN)

def asm(src,addr):
    enc,_=ks.asm('.set noreorder;'+src,addr); return bytes(enc)

def hi(x): return ((x+0x8000)>>16)&0xffff
def lo(x): return x&0xffff if (x&0xffff)<0x8000 else (x&0xffff)-0x10000

def luiaddiu(reg,val):
    return asm(f'lui ${reg},{hi(val)}; addiu ${reg},${reg},{lo(val)}',0)

def code_for(idx):
    l=0x89+idx//188; t=idx%188
    tr=0x40+t+(1 if t>=0x3f else 0)
    return (l<<8)|tr

def build(exe,glyphs):
    """exe: 원본 SLPM bytes, glyphs: [26바이트]*N (index 순서 = code_for)"""
    hook=C0
    buf=hook+0x160
    tab=hook+0x180
    sv=hook+0x190                       # 감싸기 저장 영역(스택을 쓰지 않음: 작은 스레드 스택 넘침 방지)
    wrap=hook+0x1a0
    data0=hook+0x2b0
    n0=(END0-4-data0)//GB
    n1=(END1-4-C1)//GB
    N=len(glyphs)
    assert N<=n0+n1, (N,n0+n1)
    src=f'''
    andi $t0,$a0,0xffff
    srl $t1,$t0,8
    addiu $t1,$t1,-0x89
    sltiu $t3,$t1,23
    beqz $t3,fb
    nop
    andi $t2,$t0,0xff
    addiu $t2,$t2,-0x40
    sltiu $t3,$t2,0x40
    bnez $t3,l1
    nop
    addiu $t2,$t2,-1
l1:
    addiu $t3,$zero,188
    multu $t1,$t3
    mflo $t3
    nop
    nop
    addu $t3,$t3,$t2
    sltiu $t4,$t3,{N}
    beqz $t4,fb
    nop
    sltiu $t4,$t3,{n0}
    beqz $t4,c1
    nop
    lui $t5,{hi(data0)}
    addiu $t5,$t5,{lo(data0)}
    b cp
    nop
c1:
    addiu $t3,$t3,-{n0}
    lui $t5,{hi(C1)}
    addiu $t5,$t5,{lo(C1)}
cp:
    sll $t6,$t3,4
    sll $t7,$t3,3
    addu $t6,$t6,$t7
    sll $t7,$t3,1
    addu $t6,$t6,$t7
    addu $t5,$t5,$t6
    lui $v0,{hi(buf)}
    addiu $v0,$v0,{lo(buf)}
    sh $zero,0($v0)
    sh $zero,28($v0)
    addiu $t7,$v0,2
    addiu $t6,$zero,13
    lui $a1,{hi(wrap+0x30)}
    addiu $a1,$a1,{lo(wrap+0x30)}
    xor $a1,$a1,$ra
    sltu $a1,$zero,$a1
    lui $a2,0x8005
    ori $a2,$a2,0x37b4
    xor $a2,$a2,$ra
    sltu $a2,$zero,$a2
    and $a1,$a1,$a2
row:
    lbu $t8,0($t5)
    lbu $t9,1($t5)
    addiu $t5,$t5,2
    sll $t8,$t8,8
    beqz $a1,full
    or $t8,$t8,$t9
    move $t9,$zero
    lui $a2,{hi(tab)}
    addiu $a2,$a2,{lo(tab)}
    addiu $a3,$zero,15
sl:
    lbu $t4,0($a2)
    addiu $a2,$a2,1
    srlv $t4,$t8,$t4
    andi $t4,$t4,1
    sllv $t4,$t4,$a3
    or $t9,$t9,$t4
    addiu $a3,$a3,-1
    bnez $a3,sl
    nop
    b st
    nop
full:
    srl $t9,$t8,2
st:
    srl $t4,$t9,8
    sb $t4,0($t7)
    sb $t9,1($t7)
    addiu $t6,$t6,-1
    bnez $t6,row
    addiu $t7,$t7,2
    jr $ra
    nop
fb:
    addiu $t2,$zero,0xb0
    jr $t2
    addiu $t1,$zero,0x51
'''
    code=asm(src,hook)
    # 대화창 변환(0x80050948)은 안티에일리어싱 중간색(1~8)을 섞어 획이 들쭉날쭉함.
    # 변환 직후, 한글이면 출력 텍스처(4bpp 12x15, 행당 6바이트)를 원본 비트로 다시 씀(글자=4, 그 외=0)
    wsrc=f'''
    lui $t0,{hi(sv)}
    addiu $t0,$t0,{lo(sv)}
    sw $ra,0($t0)
    sw $a0,4($t0)
    jal 0x80050948
    sw $a1,8($t0)
    lui $t0,{hi(sv)}
    addiu $t0,$t0,{lo(sv)}
    sw $v0,12($t0)
    lw $a0,4($t0)
    jal {hook}
    nop
    lui $t0,{hi(buf)}
    addiu $t0,$t0,{lo(buf)}
    bne $v0,$t0,wd
    nop
    lui $a1,{hi(sv)}
    addiu $a1,$a1,{lo(sv)}
    lw $a1,8($a1)
    addiu $t6,$zero,15
    move $t7,$v0
wr:
    lbu $t8,0($t7)
    lbu $t9,1($t7)
    sll $t8,$t8,8
    or $t8,$t8,$t9
    addiu $t7,$t7,2
    addiu $t5,$zero,6
wb:
    srl $t4,$t8,13
    andi $t4,$t4,1
    sll $t4,$t4,2
    srl $t3,$t8,12
    andi $t3,$t3,1
    sll $t3,$t3,6
    or $t4,$t4,$t3
    sb $t4,0($a1)
    addiu $a1,$a1,1
    sll $t8,$t8,2
    addiu $t5,$t5,-1
    bnez $t5,wb
    nop
    addiu $t6,$t6,-1
    bnez $t6,wr
    nop
wd:
    lui $t0,{hi(sv)}
    addiu $t0,$t0,{lo(sv)}
    lw $v0,12($t0)
    lw $ra,0($t0)
    nop
    jr $ra
    nop
'''
    wcode=asm(wsrc,wrap)
    assert wcode[0x28:0x2c]==asm(f'jal {hook}',wrap+0x28)   # 감싸기의 두 번째 호출 → ra=wrap+0x30 (R3000 로드 지연 때문에 a0는 jal 전에 읽음)
    assert len(wcode)<=data0-wrap,len(wcode)
    assert len(code)<=buf-hook,len(code)
    tsize=((END1+0x7ff-ORG)//0x800)*0x800
    img=bytearray(0x800+tsize)
    img[:len(exe[:0x53800])]=exe[:0x53800]
    struct.pack_into('<I',img,0x1c,tsize)
    def put(addr,b): img[0x800+addr-ORG:0x800+addr-ORG+len(b)]=b
    def get(addr,n): return bytes(img[0x800+addr-ORG:0x800+addr-ORG+n])
    # 원래 명령 확인 후 패치
    assert get(0x8006cd48,12)==asm('addiu $t2,$zero,0xb0; jr $t2; addiu $t1,$zero,0x51',0x8006cd48)
    put(0x8006cd48,asm(f'j {hook}; nop',0x8006cd48))
    assert get(0x8003c520,8)==luiaddiu('v0',END0)
    put(0x8003c520,luiaddiu('v0',LIM0))
    assert get(0x8003c530,8)==luiaddiu('v0',END1)
    put(0x8003c530,luiaddiu('v0',LIM1))
    put(hook,code)
    put(wrap,wcode)
    assert get(0x80051e28,4)==asm('jal 0x80050948',0x80051e28)
    put(0x80051e28,asm(f'jal {wrap}',0x80051e28))
    # 감싸기 재호출·이름 입력 표 외의 호출자(부팅 중 포함)에는 원래 글꼴처럼 펼친 글리프를 줌(좁은 글리프면 멈춤). 대화창 출력은 감싸기 코드가 덮어씀
    put(tab,bytes(15-x for x in (0,1,1,2,3,4,4,5,6,7,7,8,9,10,10)))
    for i,g in enumerate(glyphs):
        assert len(g)==GB
        put(data0+i*GB if i<n0 else C1+(i-n0)*GB, g)
    return bytes(img), n0+n1

if __name__=='__main__':
    exe=open('orig/SLPM_860.47','rb').read()
    img,cap=build(exe,[bytes(GB)]*10)
    print(hex(len(img)),'capacity',cap,hex(C0),hex(C1))
