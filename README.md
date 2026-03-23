# Apple Music Desktop Wallpaper

Windows 바탕화면에 현재 재생 중인 Apple Music 곡 정보를 실시간으로 표시하는 라이브 월페이퍼입니다.

![Windows](https://img.shields.io/badge/Windows_10%2F11-0078D6?style=flat&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

## 미리보기

> Apple Music에서 곡을 재생하면, 바탕화면 전체가 앨범 아트 기반의 라이브 월페이퍼로 변합니다.

- 앨범 아트를 활용한 블러 배경 (크로스페이드 전환)
- 중앙 글래스 카드에 고해상도 앨범 아트
- 곡 제목 / 아티스트 / 실시간 진행바
- 재생 중 앨범 아트 글로우 효과

## 설치 및 실행

### 준비물

- **Windows 10/11**
- **[Apple Music](https://apps.microsoft.com/detail/9PFHDD62MXS1)** (Microsoft Store)
- **[Lively Wallpaper](https://apps.microsoft.com/detail/9NTM2QC6QWS7)** (Microsoft Store, 무료)

> Python 설치는 **필요 없습니다.** 자동으로 다운로드됩니다.

### 3단계로 시작

**1단계: 다운로드**
```
git clone https://github.com/wjddusrb03/apple-music-wallpaper.git
```
또는 [**Download ZIP**](https://github.com/wjddusrb03/apple-music-wallpaper/archive/refs/heads/master.zip)

**2단계: 실행**
```
start.bat 더블클릭
```
> 첫 실행 시 Python과 필요한 패키지가 자동으로 다운로드됩니다 (1~2분).
> 이후 실행은 즉시 시작됩니다.

**3단계: Lively 설정 (최초 1회)**
1. Lively Wallpaper에서 **[+]** 버튼 클릭
2. **"URL 입력"** 선택
3. `http://localhost:8765` 입력
4. 확인!

> 한 번 등록하면 Lively가 기억하므로, 이후에는 `start.bat`만 실행하면 됩니다.

## 작동 방식

```
Apple Music --> Windows SMTC API --> Python Server --> WebSocket --> HTML Wallpaper <-- Lively Wallpaper
```

- Windows SMTC API로 Apple Music 재생 정보를 실시간으로 읽습니다
- 임베디드 Python이 포함되어 있어 별도 설치가 필요 없습니다
- Lively Wallpaper가 HTML 페이지를 바탕화면으로 렌더링합니다

## 프로젝트 구조

```
apple-music-wallpaper/
├── server.py          # FastAPI 서버 (SMTC + WebSocket)
├── wallpaper/
│   └── index.html     # 라이브 월페이퍼 UI
├── start.bat          # 원클릭 실행 (자동 Python 설치 포함)
├── requirements.txt   # Python 패키지 목록
├── python/            # (자동 생성) 임베디드 Python
└── README.md
```

## 최적화

- **앨범 아트 캐싱**: 곡이 바뀔 때만 이미지를 다시 읽음
- **SMTC 매니저 싱글톤**: API 연결을 재사용
- **최소 브로드캐스트**: 같은 곡이면 재생 위치만 전송
- **GPU 가속**: `translateZ(0)`, `contain: strict` 적용
- **마우스 패스스루**: `pointer-events: none`으로 바탕화면 조작에 영향 없음
- **rAF 보간**: `requestAnimationFrame`으로 진행바 부드럽게 표시

## 문제 해결

| 증상 | 해결 방법 |
|------|----------|
| 검은 화면만 보임 | Apple Music 앱에서 곡을 재생하세요 |
| 우측 하단 점이 빨간색 | `start.bat`으로 서버를 실행하세요 |
| 첫 실행에서 멈춤 | 인터넷 연결을 확인하세요 (Python 다운로드 필요) |
| Lively가 안 열림 | Microsoft Store에서 Lively Wallpaper를 설치하세요 |

## 주의 사항

- **Apple Music 전용**: Apple Music 데스크톱 앱의 재생만 감지합니다
- **보기 전용**: 바탕화면에서 음악 조작은 불가합니다. Apple Music 앱에서 조작하세요
- **로컬 전용**: 모든 데이터는 PC 내에서만 처리됩니다

## License

MIT License
