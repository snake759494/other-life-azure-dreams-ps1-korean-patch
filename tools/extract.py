# 텍스트 세그먼트 추출: SJIS 문자 + 0x0a(줄바꿈) + fe00(이름) 연속 구간
import sys,json,re,collections
FILES=['MAIN.BIN','TOWN.BIN','DUNGEON.BIN','SLPM_860.47']

def is_lead(b): return 0x81<=b<=0x9f or 0xe0<=b<=0xea
def is_trail(b): return 0x40<=b<=0xfc and b!=0x7f

def valid_char(c):
    try: s=bytes(c).decode('cp932')
    except: return False
    return len(s)==1

KANA=set(range(0x829f,0x82f2))|set(range(0x8340,0x8397))
SYM=set('、。，．・：？！ー～…‥（）「」『』［］｛｝〔〕【】＋－×÷＝＜＞％＆＊＠☆★○●◎◇◆□■△▲▽▼→←↑↓“”‘’／＼￥＄　々〃')
def ok(t):
    c=t[0]<<8|t[1]
    if 0x889f<=c<=0x9872: return True
    if c in KANA: return True
    if 0x824f<=c<=0x829a: return True
    if 0x839f<=c<=0x83d6: return False
    s=bytes(t).decode('cp932')
    return s in SYM
def scan(d):
    i=0;n=len(d);out=[]
    while i<n-1:
        j=i;toks=[];
        while j<n:
            b=d[j]
            if is_lead(b) and j+1<n and is_trail(d[j+1]) and valid_char(d[j:j+2]):
                toks.append(d[j:j+2]); j+=2
            elif b==0x0a and toks: toks.append(b'\n'); j+=1
            elif b==0xfe and j+1<n and d[j+1]==0 and toks: toks.append(b'\xfe\x00'); j+=2
            else: break
        # trim trailing non-char tokens
        while toks and toks[-1] in (b'\n',b'\xfe\x00'): j-=len(toks[-1]); toks.pop()
        chars=[t for t in toks if len(t)==2 and t!=b'\xfe\x00']
        nbad=sum(1 for t in chars if not ok(t)); bad=nbad*10>len(chars) or (len(chars)<=6 and nbad>0)
        if len(chars)<=4 and not bad:
            nb=d[j] if j<n else 0; pb=d[i-1] if i>0 else 0
            if nb!=0 or not (pb<0x20 or pb in (0xff,)): bad=True
        if len(chars)>=2 and not bad:
            kn=sum(1 for t in chars if (t[0]<<8|t[1]) in KANA or t in (b'\x81\x42',b'\x81\x41',b'\x81\x45',b'\x81\x48',b'\x81\x49',b'\x81\x5b'))
            if kn>=1 and kn*3>=len(chars):
                out.append((i,j)); i=j; continue
        i=j+1 if j>i else i+1
    return out

def text(b):
    return b.replace(b'\xfe\x00',b'{N}').decode('cp932')

if __name__=='__main__':
    res=[]
    for f in FILES:
        d=open('orig/'+f,'rb').read()
        if f.startswith('SLPM'): d=d[:0x53800]
        for s,e in scan(d): res.append((f,s,e-s,text(d[s:e])))
    uniq=collections.OrderedDict()
    for f,s,l,t in res: uniq.setdefault(t,[]).append([f,s,l])
    print('segments',len(res),'unique',len(uniq),'chars',sum(len(t) for t in uniq))
    json.dump([{'ja':t,'loc':v} for t,v in uniq.items()],open('text/segments.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
