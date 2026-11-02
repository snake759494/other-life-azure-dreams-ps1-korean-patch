# 그래픽 한글화 사양
from gfxedit import NB,NR,SH,G7,G9
M=dict(style='plain',fg=15,aa=13,font=NB,size=11)
SPEC=[
 dict(f='DUNGEON.BIN',addr=0x4c1758,bpp=4,ops=[
   dict(M,box=(32,0,64,16),text='소지품'),
   dict(M,box=(20,16,64,32),text='마물선택'),
   dict(M,box=(33,32,63,48),text='대열',size=12),
   dict(M,box=(33,48,63,64),text='융합',size=12),
   dict(M,box=(33,64,63,80),text='명령',size=12),
   dict(M,box=(33,80,63,96),text='중단',size=12),
   dict(M,box=(104,64,120,80),text='손',size=12),
   dict(M,box=(89,80,120,96),text='발밑',size=12),
 ]+[dict(style='plain',fg=1,font=G7,size=8,box=(x+3,99,x+29,110),text='전송') for x in (0,32,64)]),
 dict(f='MAIN.BIN',addr=0x258024,bpp=4,ops=[
   dict(style='outline',inner=[1,2,4,6,9],edge=14,stroke=1,font=NB,size=14,box=(0,80,128,96),text='처음부터 시작'),
   dict(style='outline',inner=[1,2,4,6,9],edge=14,stroke=1,font=NB,size=14,box=(0,96,128,112),text='이어서 시작'),
   dict(style='outline',inner=[1,2,4,6,9],edge=14,stroke=1,font=NB,size=14,box=(0,112,128,128),text='옵션'),
 ]),
 dict(f='DUNGEON.BIN',addr=0x4bace4,bpp=8,ops=[
   dict(style='texture',edge='auto',stroke=1,font=SH,size=17,shear=0.25,box=(0,87,113,104),text='마물의 탑'),
   dict(style='texture',edge='auto',stroke=1,font=SH,size=13,shear=0.2,box=(102,7,128,23),text='층'),
   dict(style='texture',edge='auto',stroke=1,font=SH,size=20,shear=0.2,box=(101,24,128,48),text='층'),
 ]),
 dict(f='TOWN.BIN',addr=0x8bacec,bpp=8,ops=[
   dict(style='plain',fg=0x93,aa=0xa9,bg=0xfe,font=NB,size=12,box=(x,8,x+15,23),text=t) for x,t in ((13,'수'),(53,'화'),(93,'풍'))
 ]+[
   dict(style='plain',fg=0x01,aa=0x96,bg=0xf8,font=NB,size=12,box=(x,40,x+15,55),text=t) for x,t in ((13,'수'),(53,'화'),(93,'풍'))
 ]),
]
