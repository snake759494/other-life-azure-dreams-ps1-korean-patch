# 번역 검사: python tools/chk.py b03
import json,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from kenc import blen,bad_chars,width,tokens
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
name=sys.argv[1]
ja=json.load(open(f'text/ja/{name}.json',encoding='utf-8'))
p=f'text/ko/{name}.json'
ko={x['id']:x['ko'] for x in json.load(open(p,encoding='utf-8'))} if os.path.exists(p) else {}
bad=0
for t in ja:
    k=ko.get(t['id'])
    errs=[]
    if k is None: errs.append('번역 없음')
    elif k!=t['ja']:
        if blen(k)>t['bytes']: errs.append(f"바이트 초과 {blen(k)}/{t['bytes']} (한글·공백·기호 2, 줄바꿈 1)")
        ls=k.split('\n')
        if len(ls)>t['lines']: errs.append(f"줄 수 초과 {len(ls)}/{t['lines']}")
        for l in ls:
            if width(l)>t['maxw']: errs.append(f"줄 폭 초과 {width(l)}/{t['maxw']}: {l}")
        if k.count('{N}')!=t['ja'].count('{N}'): errs.append('{N} 개수 불일치')
        bc=bad_chars(k)
        if bc: errs.append('사용 불가 문자: '+''.join(bc))
        if '‰' in t['ja'] and '‰' not in k: errs.append('‰(하트) 기호 누락')
    if errs:
        bad+=1
        if bad<=60: print(f"[{t['id']}] {t['ja']!r}\n   -> {k!r}\n   * "+' / '.join(errs))
print(f'문제 블록: {bad} / {len(ja)}')
