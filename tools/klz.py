# 게임 압축(SLPM 0x8003f560) 해제/압축
def dec(d,p,lim=1<<22):
    out=bytearray(); bits=0; n=0
    def bit():
        nonlocal bits,n,p
        if n==0: bits=d[p]; p+=1; n=8
        b=bits&1; bits>>=1; n-=1; return b
    while True:
        if not bit(): out.append(d[p]); p+=1; continue
        if not bit():
            w=d[p]<<8|d[p+1]; p+=2
            if w==0: return bytes(out),p
            ln=w&0xf
            if ln: ln+=2
            else: ln=d[p]+1; p+=1
            dist=w>>4
        else:
            ln=bit()*2; ln+=bit()+2
            dist=d[p] or 0x100; p+=1
        s=len(out)-dist
        if s<0 or len(out)>lim: raise ValueError
        for i in range(ln): out.append(out[s+i])
def enc(src):
    """최적 파싱(DP, 비트 비용 최소)"""
    N=len(src); from collections import defaultdict
    H=defaultdict(list)
    for j in range(N-1): H[src[j:j+2]].append(j)
    import bisect
    INF=1<<60; cost=[INF]*(N+1); cost[N]=18; ch=[None]*(N+1)
    # 뒤에서부터: cost[i]=i부터 끝까지 비트 수
    def matches(i):
        res=[]  # (len,dist) 후보: 거리 구간별 최장
        if i+2>N: return res
        L=H[src[i:i+2]]; k=bisect.bisect_left(L,i)-1; bs=0; bl=0
        cnt=0
        while k>=0 and cnt<400:
            j=L[k]; dd=i-j
            if dd>0xfff: break
            l=2
            while i+l<N and l<256 and src[j+l]==src[i+l]: l+=1
            if dd<=0x100 and l>bs: bs=l; res.append(('s',min(l,5),dd))
            if l>bl: bl=l; res.append(('l',l,dd))
            k-=1; cnt+=1
        return res
    for i in range(N-1,-1,-1):
        best=9+cost[i+1]; c=('c',)
        for t,l,dd in matches(i):
            if t=='s':
                for ll in range(2,l+1):
                    v=12+cost[i+ll]
                    if v<best: best=v; c=('s',ll,dd)
            else:
                for ll in range(3,l+1):
                    v=(18 if ll<=17 else 26)+cost[i+ll]
                    if v<best: best=v; c=('l',ll,dd)
        cost[i]=best; ch[i]=c
    items=[]; i=0
    while i<N:
        c=ch[i]
        if c[0]=='c': items.append(('c',src[i])); i+=1
        else: items.append(c); i+=c[1]
    items.append(('e',))
    out=bytearray(); flagpos=None; nb=8
    def putbit(b):
        nonlocal flagpos,nb
        if nb==8: flagpos=len(out); out.append(0); nb=0
        out[flagpos]|=b<<nb; nb+=1
    for it in items:
        if it[0]=='c': putbit(0); out.append(it[1])
        elif it[0]=='s':
            putbit(1);putbit(1); l=it[1]-2; putbit(l>>1); putbit(l&1); out.append(it[2]&0xff)
        elif it[0]=='l':
            putbit(1);putbit(0); l=it[1]
            if 3<=l<=17: out+=((it[2]<<4)|(l-2)).to_bytes(2,'big')
            else: out+=(it[2]<<4).to_bytes(2,'big'); out.append(l-1)
        else: putbit(1);putbit(0); out+=bytes(2)
    return bytes(out)
