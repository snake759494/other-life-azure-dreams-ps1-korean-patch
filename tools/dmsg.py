# 던전 메시지(문자표 모드) 추출/인코딩
import sys,os,json,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
TBL=0xfd484; B=0x7ffe6890
def table(d): return [d[TBL+2*i:TBL+2*i+2] for i in range(255)]
def decode(d,p,T):
    """게임 루틴(0x8009a364)과 동일하게 해석. (토큰목록, 끝위치) 반환"""
    toks=[]; mode=0
    while True:
        b=d[p]
        if mode==0 and b==0x51: mode=1; toks.append(('ON',)); p+=1; continue
        if b==0:
            p+=1
            if mode==0: return toks,p
            mode=0; toks.append(('OFF',)); continue
        if mode: toks.append(('T',T[b-1])); p+=1
        elif b<0x80: toks.append(('R',bytes([b]))); p+=1
        else: toks.append(('R',d[p:p+2])); p+=2
def text(toks):
    out=''
    for t in toks:
        if t[0]=='T':
            out+=t[1].decode('cp932')
        elif t[0]=='R':
            b=t[1]
            if len(b)==2 and b[0]>=0x81:
                try: out+=b.decode('cp932'); continue
                except: pass
            out+='<'+b.hex()+'>'
    return out
if __name__=='__main__':
    d=open('orig/DUNGEON.BIN','rb').read(); T=table(d)
    p=0xfd682; recs=[]
    while p<int(sys.argv[1],16):
        while d[p]==0: p+=1
        s=p; toks,p=decode(d,p,T)
        recs.append({'off':s,'len':p-s,'ja':text(toks),'tbl':any(t[0]=='T' for t in toks)})
    for r in recs[:int(sys.argv[2])]: print(hex(r['off']),r['len'],r['ja'])
    print(len(recs))

# ---- 인코더 ----
import re
def fw(c):
    if c==' ': return '　'
    if '!'<=c<='~': return chr(ord(c)+0xfee0)
    return c
def ktoks(s):
    out=[]
    for m in re.finditer(r'<([0-9a-f]+)>|(.)',s):
        out.append(('R',bytes.fromhex(m[1])) if m[1] else ('C',fw(m[2])))
    return out
def build(d,recs,cmap):
    """d: DUNGEON bytearray, recs: [{off,cap,ko}], cmap: 한글→코드. 문자표와 레코드를 덮어씀"""
    from collections import Counter
    cnt=Counter(t[1] for r in recs for t in ktoks(r['ko']) if t[0]=='C')
    tbl=[c for c,_ in cnt.most_common(255)]
    idx={c:i+1 for i,c in enumerate(tbl)}
    def code(c): return cmap[c].to_bytes(2,'big') if c in cmap else c.encode('cp932')
    for i in range(255):
        d[TBL+2*i:TBL+2*i+2]=code(tbl[i]) if i<len(tbl) else b'\x81\x40'
    for r in recs:
      ko=r['ko']
      while True:
        out=bytearray(); tk=ktoks(ko); i=0
        while i<len(tk):
            j=i
            while j<len(tk) and tk[j][0]=='C' and tk[j][1] in idx: j+=1
            if j-i>=3 or (j-i>=1 and j==len(tk) and False):
                out.append(0x51); out+=bytes(idx[t[1]] for t in tk[i:j]); out.append(0); i=j
            elif j>i:
                for t in tk[i:j]: out+=code(t[1])
                i=j
            else:
                t=tk[i]; out+=t[1] if t[0]=='R' else code(t[1]); i+=1
        out.append(0)
        if len(out)<=r['cap']: break
        # 초과 시 공백을 뒤에서부터(맨 앞 공백은 마지막에) 제거
        k=ko.rfind(' ',1)
        if k<0: k=ko.find(' ')
        if k<0: break
        ko=ko[:k]+ko[k+1:]
      if len(out)>r['cap']: print('초과',r['cap'],len(out),ko); continue
      d[r['off']:r['off']+r['cap']]=out+bytes(r['cap']-len(out))
    return tbl
