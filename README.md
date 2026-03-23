# Apple Music Desktop Wallpaper

Windows 바탕화면에 현재 재생 중인 Apple Music 곡 정보를 실시간으로 표시하는 라이브 월페이퍼입니다.

![Windows](https://img.shields.io/badge/Windows_10%2F11-0078D6?style=flat&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

## 미리보기

> Apple Music에서 곡을 재생하면, 바탕화면 전체가 앨범 아트 기반의 라이브 월페이퍼로 변합니다.

**주요 화면 구성:**
- 앨범 아트를 활용한 블러 배경 (크로스페이드 전환)
- 중앙 글래스 카드에 고해상도 앨범 아트 표시
- 곡 제목 / 아티스트 정보
- 실시간 진행바 (현재 시간 / 총 시간)
- 재생 중 앨범 아트 미세 확대 + 글로우 효과

## 설치 방법

### 더블클릭 한 번! (추천)

1. [**Releases**](https://github.com/wjddusrb03/apple-music-wallpaper/releases) 페이지에서 **`AppleMusicWallpaper.exe`** 다운로드
2. **더블클릭**으로 실행
3. 끝!

> Python, Lively Wallpaper 등 **별도 설치가 필요 없습니다.**

> **SmartScreen 경고가 나오나요?**
> 코드 서명이 없는 오픈소스 앱이기 때문에 Windows가 경고를 표시할 수 있습니다.
> **"추가 정보"** → **"실행"** 을 클릭하면 정상적으로 실행됩니다.
> 소스 코드가 모두 공개되어 있으니 안심하세요!

### 요구 사항

- **Windows 10/11**
- **[Apple Music](https://apps.microsoft.com/detail/9PFHDD62MXS1)** (Microsoft Store 데스크톱 앱)

## 사용법

1. **AppleMusicWallpaper.exe** 실행
2. **Apple Music**에서 음악 재생
3. 바탕화면이 자동으로 변경됩니다!

### 종료 방법

- 시스템 트레이 (작업 표시줄 우측) 아이콘 → **우클릭** → **Exit**

## 작동 방식

```
Apple Music → Windows SMTC API → App → Desktop Wallpaper (WorkerW)
```

1. Windows SMTC API를 통해 Apple Music 재생 정보를 읽습니다
2. 앨범 아트, 곡 정보, 재생 위치를 실시간으로 가져옵니다
3. Windows WorkerW API로 HTML을 바탕화면에 직접 렌더링합니다

**모든 것이 하나의 .exe 안에 포함되어 있습니다.**

## 직접 빌드하기

소스에서 직접 빌드하고 싶다면:

```bash
git clone https://github.com/wjddusrb03/apple-music-wallpaper.git
cd apple-music-wallpaper
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --noconsole --name "AppleMusicWallpaper" --add-data "wallpaper;wallpaper" app.py
```

빌드된 파일: `dist/AppleMusicWallpaper.exe`

### 개발 모드 (빌드 없이 테스트)

```bash
pip install -r requirements.txt
python app.py
```

## 프로젝트 구조

```
apple-music-wallpaper/
├── app.py              # 메인 앱 (SMTC + WorkerW + 시스템 트레이)
├── wallpaper/
│   └── index.html      # 월페이퍼 UI
├── build.bat           # .exe 빌드 스크립트
├── requirements.txt    # Python 패키지 목록
└── README.md
```

## 기술 스택

| 구성 요소 | 기술 |
|-----------|------|
| 미디어 정보 | Windows SMTC API (`winrt-Windows.Media.Control`) |
| 바탕화면 렌더링 | Windows WorkerW API + pywebview (WebView2) |
| 시스템 트레이 | pystray |
| 프론트엔드 | 순수 HTML/CSS/JS |
| 패키징 | PyInstaller (단일 .exe) |

## 최적화

- **앨범 아트 캐싱**: 곡이 바뀔 때만 이미지를 다시 읽음
- **SMTC 매니저 싱글톤**: API 연결을 재사용
- **GPU 가속**: `translateZ(0)`, `contain: strict` 적용
- **마우스 패스스루**: `pointer-events: none`으로 바탕화면 조작에 영향 없음
- **rAF 보간**: `requestAnimationFrame`으로 진행바를 부드럽게 표시

## 문제 해결

| 증상 | 해결 방법 |
|------|----------|
| 바탕화면이 안 바뀜 | Apple Music 앱이 실행 중이고 곡이 재생 중인지 확인 |
| 트레이 아이콘이 안 보임 | 작업 표시줄 > 숨겨진 아이콘 (^) 클릭 |
| 바탕화면 원래대로 안 돌아옴 | 트레이 아이콘 우클릭 > Exit으로 정상 종료 |

## 주의 사항

- **Apple Music 전용**: Apple Music 데스크톱 앱의 재생만 감지합니다
- **보기 전용**: 바탕화면에서 음악 조작은 불가합니다. Apple Music 앱에서 조작하세요
- **로컬 전용**: 모든 데이터는 PC 내에서만 처리되며 외부 전송 없음

## License

MIT License
