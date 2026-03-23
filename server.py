import asyncio
import json
import base64
import os
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Use absolute paths (fixes VBS launch from different working directory)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/wallpaper", StaticFiles(directory=os.path.join(BASE_DIR, "wallpaper")), name="wallpaper")

connected_clients: list[WebSocket] = []
current_state: dict = {}

_cached_art_b64: str = ""
_cached_art_key: str = ""
_smtc_manager = None


async def _get_manager():
    global _smtc_manager
    if _smtc_manager is None:
        from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
        _smtc_manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
    return _smtc_manager


@app.get("/")
async def root():
    return FileResponse(os.path.join(BASE_DIR, "wallpaper", "index.html"))


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


async def get_session():
    manager = await _get_manager()
    sessions = manager.get_sessions()

    # Priority 1: Apple Music / iTunes (exact match)
    for session in sessions:
        src = session.source_app_user_model_id.lower()
        if "apple" in src or "itunes" in src:
            return session

    # Priority 2: Any app with "music" but NOT Windows built-in players
    EXCLUDE = ["zune", "groove", "microsoft"]
    for session in sessions:
        src = session.source_app_user_model_id.lower()
        if "music" in src and not any(ex in src for ex in EXCLUDE):
            return session

    return None


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
    return _cached_art_b64


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
            "_thumbnail": media_props.thumbnail,
            "is_playing": is_playing,
            "position": round(position, 1),
            "duration": round(duration, 1),
        }
    except Exception as e:
        print(f"[SMTC Error] {e}")
        return None


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
                    album_art = await get_album_art(title, artist, thumbnail)
                    info["album_art"] = album_art
                    current_state = info
                    last_title = title
                    last_artist = artist
                    await broadcast(info)
                else:
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
    # Save PID for clean shutdown
    pid_file = os.path.join(BASE_DIR, "server.pid")
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

    print("=" * 50)
    print(" Apple Music Wallpaper Server")
    print(" http://localhost:8765")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")
