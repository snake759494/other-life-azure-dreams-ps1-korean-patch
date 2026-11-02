# 한국어 문자열 -> 게임 바이트 변환 규칙 (길이 계산/인코딩 공용)
import unicodedata
# ASCII -> 전각 치환 (자체 글리프로 렌더링)
def norm(s):
    out=[]
    for ch in s:
        o=ord(ch)
        if ch==' ': out.append('　')
        elif 0x21<=o<=0x7e: out.append(chr(o+0xfee0))
        else: out.append(ch)
    s=''.join(out)
    return s.replace('...','…').replace('．．．','…')

# 원본 BIOS 글리프를 그대로 쓰는 기호(일본어 폰트에 있는 모양 유지)
KEEP=set('　、。・：；？！ー～…‥「」『』［］（）【】〔〕＋－×÷＝＜＞％＆＊＠☆★○●◎◇◆□■△▲▽▼→←↑↓♪‰／＼￥＄“”‘’０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ，．＇＂＃｜＿＾｀｛｝')

def is_hangul(ch): return 0xac00<=ord(ch)<=0xd7a3

def tokens(s):
    """{N} 태그, 줄바꿈, 문자 단위로 분해"""
    s=norm(s); i=0; out=[]
    while i<len(s):
        if s.startswith('{N}',i) or s.startswith('｛Ｎ｝',i):
            out.append('{N}'); i+=3; continue
        out.append(s[i]); i+=1
    return out

def blen(s):
    return sum(1 if t=='\n' else 2 for t in tokens(s))

def bad_chars(s):
    return sorted(set(t for t in tokens(s) if t not in ('{N}','\n') and not is_hangul(t) and t not in KEEP))

def width(line):
    return sum(4 if t=='{N}' else 1 for t in tokens(line))
