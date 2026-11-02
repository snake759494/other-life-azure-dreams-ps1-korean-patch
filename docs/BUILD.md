# 재빌드

번역 대본과 원문은 저장소에 없습니다. 아래는 자신이 가진 원본과 번역 파일로 다시 빌드하는 절차입니다.

## 준비물

빌드 스크립트는 저장소 폴더를 작업 폴더로 씁니다. 원본 디스크와 일부 글꼴은 **그 상위 폴더**에서 찾습니다.

```
<상위 폴더>/
  Other Life Azure Dreams (Japan).bin    ← README의 해시와 일치해야 함
  NanumSquareNeo-dEb.ttf  NanumSquareNeo-bRg.ttf  SeoulHangangEB.ttf
  xdelta3.exe (배포 파일을 만들 때만)
  <이 저장소>/
    fonts/Galmuri11.ttf  fonts/Galmuri7.ttf  fonts/Galmuri9.ttf
    orig/                ← 원본 디스크에서 추출 (아래 1단계)
    text/                ← 원문·번역 (저장소 미포함)
    tools/movie_segs.json ← 무비 자막 위치 정보 (저장소 미포함, 원본 무비에서 만든 자료)
```

- Python 3.13, `numpy`, `Pillow`, `keystone-engine` (`unicorn`은 분석용)
- 글꼴 출처는 `docs/FONT_CREDITS.md`를 참고하세요.

## 순서

모든 명령은 저장소 폴더에서 실행합니다.

1. 원본 파일 추출: `python tools/extract_orig.py "../Other Life Azure Dreams (Japan).bin"` → `orig/MAIN.BIN`, `TOWN.BIN`, `DUNGEON.BIN`, `SLPM_860.47`
2. 원문 추출: `python tools/extract.py` → `text/segments.json`
   - 장 단위로 나누려면 `tools/mkbatch.py`를 씁니다(→ `text/ja/bNN.json`).
   - 몬스터 도감은 `python tools/ency.py extract`(→ `text/ency_ja.json`)로 뽑습니다. 던전 메시지 표는 `tools/dmsg.py`로 해석합니다.
3. 번역 작성 (형식은 `docs/TRANSLATION_GUIDE.md`)
   - `text/ko/bNN.json` = `[{"id", "ko"}]`, `text/ency_ko.json`, `text/dmsg_ko.json`, `text/movie_ko.json`
   - `text/extra.json` = `{"items": [{"ja", "ko", "loc"}]}`
   - `text/resid_ko.json`, `text/kblock_ko.json` = `{원문: 번역}`
   - 검사: `python tools/chk.py bNN`
4. 빌드: `python tools/build.py "../Other Life Azure Dreams (Japan) [KOR].bin"`
5. 무비 자막: `python tools/mov.py "../Other Life Azure Dreams (Japan) [KOR].bin"`. `build.py`가 이미지를 새로 쓰므로 빌드할 때마다 다시 실행해야 합니다.
6. 남은 일본어 검사: `python tools/survey.py "../Other Life Azure Dreams (Japan) [KOR].bin"`(→ `tmp/survey.json`)
7. 배포 파일:

```powershell
xdelta3 -e -0 -S none -A -s "Other Life Azure Dreams (Japan).bin" "Other Life Azure Dreams (Japan) [KOR].bin" OtherLifeAzureDreams_PS1_KO_v1.0.xdelta
```

## 화면 확인

`tools/emu.py`, `tools/play.py`, `tools/run.py`는 DuckStation 휴대용 복사본(`duck/`, GDB 서버 포트 2399)을 백그라운드로 띄웁니다. 그 상태에서 키 입력, 메모리 읽기·쓰기, 스크린샷을 합니다. 에뮬레이터는 저장소에 넣지 않았습니다. 테스트 전에 이전에 띄운 에뮬레이터가 남아 있지 않은지 확인하세요. 남아 있으면 GDB 연결이 옛 인스턴스로 붙습니다.
