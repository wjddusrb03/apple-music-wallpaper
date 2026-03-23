import asyncio
import json
import base64
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/wallpaper", StaticFiles(directory="wallpaper"), name="wallpaper")

connected_clients: list[WebSocket] = []
current_state: dict = {}

# ── 캐시 ────────────────────────────────────────
_cached_art_b64: str = ""
_cached_art_key: str = ""       # "title|artist" 기반 캐시 키
_smtc_manager = None


async def _get_manager():
    global _smtc_manager
    if _smtc_manager is None:
        from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
        _smtc_manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
    return _smtc_manager


# ── 라우트 ──────────────────────────────────────
@app.get("/")
async def root():
    return FileResponse("wallpaper/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    if current_state:
        await websocket.send_text(json.dumps(current_state))
    try:
        while True:
            await asyncio.sleep(10)
    except (WebSocketDisconnect, Exception):
        if websocket in connected_clients:
            connected_clients.remove(websocket)


async def broadcast(data: dict):
    dead = []
    msg = json.dumps(data)
    for client in connected_clients:
        try:
            await client.send_text(msg)
        except Exception:
            dead.append(client)
    for d in dead:
        if d in connected_clients:
            connected_clients.remove(d)


# ── SMTC 세션 (매니저 캐싱) ────────────────────
async def get_session():
    manager = await _get_manager()
    sessions = manager.get_sessions()

    for session in sessions:
        src = session.source_app_user_model_id.lower()
        if "apple" in src or "itunes" in src:
            return session

    return None


# ── 앨범 아트 (캐시 사용) ──────────────────────
async def _read_album_art(thumbnail) -> str:
    from winrt.windows.storage.streams import DataReader, Buffer, InputStreamOptions

    stream = await thumbnail.open_read_async()
    size = stream.size
    buf = Buffer(size)
    await stream.read_async(buf, size, InputStreamOptions.READ_AHEAD)
    reader = DataReader.from_buffer(buf)
    data = bytearray(size)
    reader.read_bytes(data)
    return "data:image/jpeg;base64," + base64.b64encode(bytes(data)).decode()


async def get_album_art(title: str, artist: str, thumbnail) -> str:
    """곡이 바뀔 때만 앨범 아트를 다시 읽음"""
    global _cached_art_b64, _cached_art_key

    key = f"{title}|{artist}"
    if key == _cached_art_key and _cached_art_b64:
        return _cached_art_b64

    try:
        if thumbnail:
            _cached_art_b64 = await _read_album_art(thumbnail)
            _cached_art_key = key
            return _cached_art_b64
    except Exception as e:
        print(f"[Art Error] {e}")

    return _cached_art_b64  # fallback: 이전 아트


# ── 미디어 정보 ────────────────────────────────
async def get_media_info() -> dict | None:
    try:
        from winrt.windows.media.control import (
            GlobalSystemMediaTransportControlsSessionPlaybackStatus as Status,
        )

        session = await get_session()

        if session is None:
            return {"title": "", "artist": "", "album": "",
                    "is_playing": False, "position": 0, "duration": 0}

        media_props = await session.try_get_media_properties_async()
        playback_info = session.get_playback_info()
        timeline = session.get_timeline_properties()

        title = media_props.title or ""
        artist = media_props.artist or ""

        # 위치 / 길이
        position = 0.0
        duration = 0.0
        try:
            import datetime
            pos = timeline.position
            end = timeline.end_time
            if isinstance(pos, datetime.timedelta):
                position = pos.total_seconds()
                duration = end.total_seconds()
            else:
                position = int(pos) / 10_000_000
                duration = int(end) / 10_000_000
        except Exception:
            pass

        is_playing = playback_info.playback_status == Status.PLAYING

        return {
            "title": title,
            "artist": artist,
            "album": media_props.album_title or "",
            "_thumbnail": media_props.thumbnail,  # 내부용, 직렬화 안 됨
            "is_playing": is_playing,
            "position": round(position, 1),
            "duration": round(duration, 1),
        }
    except Exception as e:
        print(f"[SMTC Error] {e}")
        return None


# ── 폴링 (최적화) ──────────────────────────────
async def poll_media():
    global current_state
    last_title = ""
    last_artist = ""

    while True:
        try:
            info = await get_media_info()

            if info is not None:
                title = info["title"]
                artist = info["artist"]
                thumbnail = info.pop("_thumbnail", None)
                song_changed = (title != last_title or artist != last_artist)

                if song_changed:
                    # 곡 변경 → 앨범 아트 읽기 + 전체 브로드캐스트
                    album_art = await get_album_art(title, artist, thumbnail)
                    info["album_art"] = album_art
                    current_state = info
                    last_title = title
                    last_artist = artist
                    await broadcast(info)
                else:
                    # 같은 곡 → 위치만 브로드캐스트 (가볍게)
                    pos_update = {
                        "position": info["position"],
                        "duration": info["duration"],
                        "is_playing": info["is_playing"],
                    }
                    current_state.update(pos_update)
                    await broadcast(pos_update)
        except Exception as e:
            print(f"[Poll Error] {e}")

        await asyncio.sleep(1)


@app.on_event("startup")
async def startup():
    asyncio.create_task(poll_media())


if __name__ == "__main__":
    print("=" * 50)
    print(" Apple Music Wallpaper Server")
    print(" http://127.0.0.1:8765")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")
