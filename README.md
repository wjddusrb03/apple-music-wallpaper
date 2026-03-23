# Apple Music 바탕화면 월페이퍼

Windows 바탕화면에 현재 재생 중인 Apple Music 곡 정보를 실시간으로 표시하는 라이브 월페이퍼입니다.

![Windows](https://img.shields.io/badge/Windows_10%2F11-0078D6?style=flat&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.10+-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

## 미리보기

> Apple Music에서 곡을 재생하면, 바탕화면 전체가 앨범 아트 기반의 라이브 월페이퍼로 변합니다.

**주요 화면 구성:**
- 앨범 아트를 활용한 블러 배경 (크로스페이드 전환)
- 중앙 글래스 카드에 고해상도 앨범 아트 표시
- 곡 제목 / 아티스트 정보
- 실시간 진행바 (현재 시간 / 총 시간)
- 재생 중 앨범 아트 미세 확대 + 글로우 효과

## 작동 방식

```
Apple Music (Windows) ← SMTC API → Python 서버 ← WebSocket → HTML 월페이퍼 ← Lively Wallpaper
```

1. **Python 서버**가 Windows SMTC(System Media Transport Controls) API를 통해 Apple Music의 재생 정보를 읽습니다
2. WebSocket으로 곡 정보(제목, 아티스트, 앨범 아트, 재생 위치)를 실시간 전송합니다
3. **Lively Wallpaper**가 HTML 페이지를 바탕화면으로 렌더링합니다

## 요구 사항

- **Windows 10/11**
- **Python 3.10 이상**
- **[Apple Music](https://apps.microsoft.com/detail/9PFHDD62MXS1)** (Microsoft Store 데스크톱 앱)
- **[Lively Wallpaper](https://apps.microsoft.com/detail/9NTM2QC6QWS7)** (Microsoft Store, 무료)

## 설치 및 실행

### 1. 프로젝트 다운로드

```bash
git clone https://github.com/wjddusrb03/apple-music-wallpaper.git
cd apple-music-wallpaper
```

### 2. 원클릭 실행

```
start.bat
```

`start.bat`이 자동으로 처리하는 작업:
- 기존 서버 프로세스 종료
- 필요한 Python 패키지 설치
- 서버 시작 (백그라운드)
- Lively Wallpaper 실행

### 3. Lively Wallpaper 설정 (최초 1회)

1. Lively Wallpaper에서 **[+]** 버튼 클릭
2. **"URL 입력"** 선택
3. `http://127.0.0.1:8765` 입력
4. 확인 → 바탕화면에 월페이퍼 적용

> 한 번 등록하면 Lively가 기억하므로, 이후에는 `start.bat`만 실행하면 됩니다.

### 4. Apple Music에서 음악 재생

Apple Music 데스크톱 앱에서 곡을 재생하면 바탕화면에 자동으로 표시됩니다.

## 수동 설치 (start.bat 없이)

```bash
pip install -r requirements.txt
python server.py
```

서버가 `http://127.0.0.1:8765`에서 실행됩니다.

## 프로젝트 구조

```
apple-music-wallpaper/
├── server.py          # FastAPI 서버 (SMTC 연동 + WebSocket)
├── wallpaper/
│   └── index.html     # 라이브 월페이퍼 (Lively에서 렌더링)
├── start.bat          # 원클릭 실행 스크립트
├── requirements.txt   # Python 패키지 목록
└── README.md
```

## 기술 스택

| 구성 요소 | 기술 |
|-----------|------|
| 미디어 정보 | Windows SMTC API (`winrt-Windows.Media.Control`) |
| 백엔드 서버 | FastAPI + uvicorn |
| 실시간 통신 | WebSocket |
| 프론트엔드 | 순수 HTML/CSS/JS (프레임워크 없음) |
| 바탕화면 렌더링 | Lively Wallpaper (WebView2) |

## 최적화

- **앨범 아트 캐싱**: 곡이 바뀔 때만 이미지를 다시 읽음
- **SMTC 매니저 싱글톤**: API 연결을 재사용
- **최소 브로드캐스트**: 같은 곡이면 재생 위치만 전송
- **GPU 가속**: `translateZ(0)`, `contain: strict` 적용
- **마우스 패스스루**: `pointer-events: none`으로 바탕화면 조작에 영향 없음
- **rAF 보간**: `requestAnimationFrame`으로 진행바를 부드럽게 표시

## 문제 해결

| 증상 | 해결 방법 |
|------|----------|
| 검은 화면만 보임 | Apple Music 데스크톱 앱이 실행 중인지 확인 |
| 우측 하단 점이 빨간색 | 서버가 실행 중인지 확인 (`python server.py`) |
| 곡 정보가 안 바뀜 | Apple Music 앱을 재시작해보세요 |
| Lively가 안 열림 | Microsoft Store에서 Lively Wallpaper 설치 확인 |

## 주의 사항

- **Apple Music 전용**: Apple Music 데스크톱 앱의 재생만 감지합니다 (웹 브라우저, YouTube 등은 무시)
- **보기 전용**: 바탕화면에서 음악 조작은 불가합니다. 재생/정지/곡 변경은 Apple Music 앱에서 하세요
- **로컬 전용**: 서버는 `127.0.0.1`에서만 실행되며, 외부 네트워크에 노출되지 않습니다

## 라이선스

MIT License
