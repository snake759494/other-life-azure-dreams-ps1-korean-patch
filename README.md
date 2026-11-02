# 아더 라이프 애저 드림스 PS1 한글패치

PS1 일본판 **アザーライフ アザードリームス (Other Life Azure Dreams, SLPM-86047)**용 비공식 한국어 패치입니다. 마을과 「마물의 탑」의 **대사·이벤트·선택지**를 모두 한국어로 옮겼습니다. **아이템·장비 설명, 메뉴, 던전 메시지, 몬스터 도감, 오프닝 무비 자막**도 한국어로 바꿨습니다. **타이틀 메뉴와 탑 로고 같은 그림 글자**는 한글로 다시 그렸습니다. 현재 배포판은 **v1.0 (2026-11-02)**입니다.

[패치 다운로드](https://github.com/snake759494/other-life-azure-dreams-ps1-korean-patch/releases/latest) · [기술 설명](docs/TECHNICAL.md) · [재빌드](docs/BUILD.md) · [변경 기록](CHANGELOG.md) · [권리 안내](RIGHTS.md)

릴리즈에는 한글패치 **OtherLifeAzureDreams_PS1_KO_v1.0.xdelta** 하나만 첨부합니다. 저장소에는 제작 도구와 기술 문서만 공개합니다. 다음은 포함하지 않습니다.

- 원본·완성 디스크 이미지와 추출한 게임 파일
- 일본어 원문과 번역 대본
- 글꼴 파일과 외부 실행 파일

GitHub가 자동으로 만드는 Source code ZIP/TAR는 저장소 소스를 압축한 것이며, 게임 파일이 아닙니다.

## 게임 소개 및 대상 버전

『アザーライフ アザードリームス』는 코나미가 1997년에 PS1으로 낸 로그라이크 RPG입니다. 사막 마을 몬스바이아에 사는 열다섯 살 소년이 주인공입니다. 소년은 사역마와 함께 들어갈 때마다 모습이 바뀌는 「마물의 탑」을 오르며, 탑에서 얻은 돈으로 마을을 키워 갑니다.

이 패치는 **PS1 일본판 SLPM-86047의 BIN/CUE 이미지(단일 트랙, MODE2/2352)**에만 적용됩니다. 파일 이름보다 아래 표의 크기와 해시가 일치하는지가 중요합니다.

## 적용할 원본

| 항목 | 값 |
| --- | --- |
| 게임 ID | SLPM-86047 |
| 원본 형식 | 수정되지 않은 일본판 BIN/CUE (트랙 1개) |
| 원본 BIN 크기 | 546,609,504 바이트 |
| **원본 BIN MD5** | `3c8073be475eae2d870f9ca1f122d50b` |
| 원본 BIN SHA-1 | `51c7eff6c516ed21dae58fcaf29711dace9b5e1a` |
| 원본 BIN SHA-256 | `0cecb1ba798e773797ee0a89c25202e92849ba162bbe84676759dec347760bc8` |
| xdelta 파일 크기 | 25,841,265 바이트 |
| xdelta SHA-256 | `f93ff0a7595b78e9b228e6eb5389e8c44891ee17b73f6f73978fd4d8bd9a71b7` |
| 적용 결과 BIN 크기 | 546,609,504 바이트 (원본과 같음) |
| 적용 결과 BIN SHA-1 | `dde725a499f837b6ab5b57aca69d74f72eebb912` |
| 적용 결과 BIN SHA-256 | `5ab9da63f6bae8f6c3ae8e9280ecb5e92e98848d5947ea3d051c0968bf9d768e` |

원본 게임 파일은 사용자가 직접 준비해야 합니다.

## 패치 적용 방법

### Windows에서 원본 확인

```powershell
Get-FileHash -Algorithm MD5 -LiteralPath '.\Other Life Azure Dreams (Japan).bin'
```

위 표와 다르면 적용을 중단하세요. CHD, PBP, ECM, 압축 이미지에는 적용할 수 없습니다.

### xdelta UI 사용

1. 릴리즈에서 `OtherLifeAzureDreams_PS1_KO_v1.0.xdelta`를 받습니다.
2. xdelta3 패치를 지원하는 도구에서 **Apply Patch** 기능을 엽니다.
3. **Patch**에는 xdelta 파일을, **Source File**에는 해시가 일치하는 원본 `.bin`을 선택합니다.
4. **Output File**에는 새 파일 이름을 지정합니다(예: `Other Life Azure Dreams (Korean).bin`).
5. 원본 `.cue`를 복사해 결과 BIN과 같은 이름으로 바꿉니다. 그리고 안의 `FILE "..."` 줄을 결과 BIN 파일 이름으로 고칩니다.

```
FILE "Other Life Azure Dreams (Korean).bin" BINARY
  TRACK 01 MODE2/2352
    INDEX 01 00:00:00
```

xdelta 파일은 호환성을 위해 압축, 2차 압축, 파일 경로 헤더를 모두 빼고 만들었습니다. xdelta 자체는 [공식 프로젝트](https://github.com/jmacd/xdelta)를 참고하세요.

### 명령줄 사용

```powershell
.\xdelta3.exe -d -s '.\Other Life Azure Dreams (Japan).bin' '.\OtherLifeAzureDreams_PS1_KO_v1.0.xdelta' '.\Other Life Azure Dreams (Korean).bin'
```

해시 검사와 CUE 생성까지 자동으로 해 주는 도구도 있습니다. Python 3과 xdelta3가 필요합니다. 같은 이름의 출력 파일이 이미 있으면 덮어쓰지 않습니다.

```powershell
python tools/apply_release.py --xdelta '.\xdelta3.exe' --source '.\Other Life Azure Dreams (Japan).bin' --patch '.\OtherLifeAzureDreams_PS1_KO_v1.0.xdelta' --output '.\Other Life Azure Dreams (Korean).bin'
```

### 실행

에뮬레이터에서 결과 `.cue`를 여세요. 원본판의 세이브 스테이트는 불러오지 마세요(실행파일과 데이터가 다릅니다). 메모리 카드 세이브는 원본판과 형식이 같아 그대로 쓸 수 있을 것으로 봅니다. 다만 직접 확인하지는 못했습니다.

## 작업 내용과 범위

| 구분 | 작업량 및 내용 |
| --- | --- |
| 대사·이벤트 | 마을·탑의 대화, 이벤트, 선택지, 시스템 안내 텍스트 블록 6,560개 |
| 짧은 문자열 | 아이템·장비 설명, 상태 이상 등 300개<br>장소 이름 등 단독 라벨 115개<br>메뉴 명령 96개 |
| 던전 | 던전 메시지 206개(함정, 상태 변화, 전투 결과 등) |
| 도감 | 몬스터 도감 설명 185항목 |
| 무비 | 오프닝 무비 한국어 자막 46줄(화면 아래쪽 매크로블록만 다시 인코딩) |
| 글꼴 | 갈무리11 한글 1,113자(12×15 비트맵, 원본 픽셀 그대로) |
| 이름 입력 | 「한자」 모드를 한글 음절표로 교체 |
| 그림 글자 | 타이틀 메뉴(처음부터 시작/이어서 시작/옵션)<br>「마물의 탑」 로고와 층 표시<br>던전 메뉴(소지품·마물선택·대열·융합·명령 등)<br>속성 표시(수·화·풍) |

이 게임은 한자를 PS1 BIOS의 한자 글꼴로 그립니다. 그래서 실행파일의 BIOS 글꼴 조회(`Krom2RawAdd`)를 가로채, 비어 있는 한자 코드 자리에 한글 글리프를 돌려주게 했습니다. 대화창은 게임이 글자에 테두리 효과를 섞어 그리는데, 이 효과를 거친 출력을 원래 글리프 비트로 다시 써서 글자가 선명하게 보이도록 했습니다. 자세한 내용은 [docs/TECHNICAL.md](docs/TECHNICAL.md)를 참고하세요.

### 번역 원칙

- 기계 번역 없이 문맥을 보고 직접 번역했습니다(`docs/TRANSLATION_GUIDE.md`).
- 원문 자리에 덮어쓰는 방식이라, 바이트 수와 줄 폭에 맞춰 간결하게 의역했습니다.
- 인명·지명은 일본어 발음대로 적었습니다(코우, 큐운, 몬스바이아 등). 오사카 사투리 캐릭터는 가벼운 경상도 말투로 옮겼습니다.

### 번역하지 않은 것

- 음성
- 오프닝 외 무비(코나미 로고, 스태프 롤 등)
- 제작사 로고·저작권 표기
- 이름 입력의 기본 가나 모드와 가타카나 모드(한글 입력은 「한자」 모드 자리에 넣음)

## 알려진 한계

- 모든 화면을 직접 확인하지는 못했습니다. 타이틀, 데모, 새 게임 첫 대화, 이동 안내, 장소 이름은 에뮬레이터로 확인했습니다. 대화창 글꼴을 마지막으로 고친 뒤에는 이름 입력과 옵션 화면을 다시 확인하지 못했습니다. 칸을 넘치거나 어긋난 문구가 있으면 이슈로 알려 주세요.
- 원문 자리에 덮어쓰므로, 몇몇 문장은 원문보다 짧게 줄였습니다.
- 개발용 메모나 깨진 데이터로 보이는 블록은 원문 그대로 두었습니다.
- 인게임 확인은 DuckStation으로 했습니다. 실기에서의 동작은 확인하지 못했습니다.

## 저장소 구성

| 경로 | 내용 |
| --- | --- |
| `tools/build.py` | 전체 빌드(텍스트 교체, 글꼴 생성, 실행파일 패치, 그림 글자, 디스크 기록) |
| `tools/build_exe.py` | 실행파일 패치: 한글 글꼴 배치, BIOS 글꼴 조회 후킹, 대화창 출력 보정 |
| `tools/font.py`, `tools/kenc.py` | 한글 글리프 렌더링과 문자열 인코딩 |
| `tools/gfxedit.py`, `tools/gfxspec.py`, `tools/klz.py` | 압축 텍스처의 그림 글자 다시 그리기와 압축 |
| `tools/mov.py`, `tools/str.py`, `tools/mdec.py` | 오프닝 무비 자막(STR 프레임 부분 재인코딩) |
| `tools/disc.py`, `tools/iso.py`, `tools/cdsec.py` | 디스크 섹터 교체와 EDC/ECC 재계산 |
| `tools/extract_orig.py`, `tools/extract.py`, `tools/dmsg.py`, `tools/ency.py` | 원본 파일과 원문 추출 |
| `tools/chk.py`, `tools/survey.py`, `tools/residual.py` | 번역 검사와 남은 일본어 전수 조사 |
| `tools/apply_release.py` | 해시 검사 후 적용 |
| `tools/emu.py`, `tools/play.py`, `tools/run.py` | DuckStation 테스트 조작 |
| `docs/` | 기술 설명, 재빌드 방법, 글꼴 출처, 번역 지침 |

권리 관련 내용은 [RIGHTS.md](RIGHTS.md)를 참고하세요.
