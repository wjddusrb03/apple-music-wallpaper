"""
Apple Music Desktop Wallpaper
Single .exe - no Python, no Lively Wallpaper needed
"""
import os
import sys
import ctypes
import ctypes.wintypes as wintypes
import threading
import asyncio
import json
import base64
import time
import webview


# ── PyInstaller resource path ──
def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative)


# ══════════════════════════════════════════
#  Win32: Desktop Wallpaper (WorkerW)
# ══════════════════════════════════════════
user32 = ctypes.windll.user32

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def embed_into_desktop(title):
    """Find window by title and embed behind desktop icons via WorkerW"""
    hwnd = user32.FindWindowW(None, title)
    if not hwnd:
        print("[Wallpaper] Window not found")
        return False

    # 1) Find Progman
    progman = user32.FindWindowW("Progman", None)
    if not progman:
        print("[Wallpaper] Progman not found")
        return False

    # 2) Spawn WorkerW
    result = wintypes.DWORD()
    user32.SendMessageTimeoutW(
        progman, 0x052C, 0xD, 0x1,
        0x0, 1000, ctypes.byref(result)
    )

    # 3) Find WorkerW behind desktop icons
    target_worker = [None]

    @WNDENUMPROC
    def enum_cb(h, _):
        shell = user32.FindWindowExW(h, None, "SHELLDLL_DefView", None)
        if shell:
            target_worker[0] = user32.FindWindowExW(None, h, "WorkerW", None)
        return True

    user32.EnumWindows(enum_cb, 0)

    if not target_worker[0]:
        print("[Wallpaper] WorkerW not found")
        return False

    # 4) Reparent our window into WorkerW
    user32.SetParent(hwnd, target_worker[0])

    # 5) Resize to fill primary monitor
    w = user32.GetSystemMetrics(0)
    h = user32.GetSystemMetrics(1)
    user32.MoveWindow(hwnd, 0, 0, w, h, True)

    print(f"[Wallpaper] Embedded OK  ({w}x{h})")
    return True


def detach_from_desktop(title):
    """Restore: detach window from WorkerW"""
    hwnd = user32.FindWindowW(None, title)
    if hwnd:
        user32.SetParent(hwnd, None)


# ══════════════════════════════════════════
#  SMTC (System Media Transport Controls)
# ══════════════════════════════════════════
_cached_art_b64 = ""
_cached_art_key = ""
_smtc_manager = None


async def _get_manager():
    global _smtc_manager
    if _smtc_manager is None:
        from winrt.windows.media.control import (
            GlobalSystemMediaTransportControlsSessionManager,
        )
        _smtc_manager = (
            await GlobalSystemMediaTransportControlsSessionManager.request_async()
        )
    return _smtc_manager


async def get_session():
    manager = await _get_manager()
    sessions = manager.get_sessions()
    for session in sessions:
        src = session.source_app_user_model_id.lower()
        if "apple" in src or "itunes" in src or "music" in src:
            return session
    return None


async def _read_art_bytes(thumbnail) -> str:
    from winrt.windows.storage.streams import DataReader, Buffer, InputStreamOptions

    stream = await thumbnail.open_read_async()
    size = stream.size
    buf = Buffer(size)
    await stream.read_async(buf, size, InputStreamOptions.READ_AHEAD)
    reader = DataReader.from_buffer(buf)
    data = bytearray(size)
    reader.read_bytes(data)
    return "data:image/jpeg;base64," + base64.b64encode(bytes(data)).decode()


async def get_album_art(title, artist, thumbnail):
    global _cached_art_b64, _cached_art_key
    key = f"{title}|{artist}"
    if key == _cached_art_key and _cached_art_b64:
        return _cached_art_b64
    try:
        if thumbnail:
            _cached_art_b64 = await _read_art_bytes(thumbnail)
            _cached_art_key = key
            return _cached_art_b64
    except Exception as e:
        print(f"[Art] {e}")
    return _cached_art_b64


async def get_media_info():
    try:
        from winrt.windows.media.control import (
            GlobalSystemMediaTransportControlsSessionPlaybackStatus as Status,
        )

        session = await get_session()
        if session is None:
            return {
                "title": "", "artist": "", "album": "",
                "is_playing": False, "position": 0, "duration": 0,
            }

        media = await session.try_get_media_properties_async()
        pb = session.get_playback_info()
        tl = session.get_timeline_properties()

        title = media.title or ""
        artist = media.artist or ""

        position = 0.0
        duration = 0.0
        try:
            import datetime
            pos, end = tl.position, tl.end_time
            if isinstance(pos, datetime.timedelta):
                position = pos.total_seconds()
                duration = end.total_seconds()
            else:
                position = int(pos) / 10_000_000
                duration = int(end) / 10_000_000
        except Exception:
            pass

        return {
            "title": title,
            "artist": artist,
            "album": media.album_title or "",
            "_thumb": media.thumbnail,
            "is_playing": pb.playback_status == Status.PLAYING,
            "position": round(position, 1),
            "duration": round(duration, 1),
        }
    except Exception as e:
        print(f"[SMTC] {e}")
        return None


# ══════════════════════════════════════════
#  Media Polling → JS Bridge
# ══════════════════════════════════════════
def start_media_poll(window):
    def _poll():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        last_title = ""
        last_artist = ""

        while True:
            try:
                info = loop.run_until_complete(get_media_info())
                if info:
                    title = info["title"]
                    artist = info["artist"]
                    thumb = info.pop("_thumb", None)
                    changed = title != last_title or artist != last_artist

                    if changed and title:
                        art = loop.run_until_complete(
                            get_album_art(title, artist, thumb)
                        )
                        info["album_art"] = art
                        last_title = title
                        last_artist = artist

                    safe = json.dumps(info, ensure_ascii=False)
                    try:
                        window.evaluate_js(f"handleMsg({safe})")
                    except Exception:
                        pass
            except Exception as e:
                print(f"[Poll] {e}")

            time.sleep(1)

    threading.Thread(target=_poll, daemon=True).start()


# ══════════════════════════════════════════
#  System Tray
# ══════════════════════════════════════════
_tray_icon = None


def start_tray(window):
    global _tray_icon
    try:
        import pystray
        from PIL import Image, ImageDraw

        # Simple music-note icon
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse([14, 36, 32, 54], fill="white")
        d.rectangle([30, 10, 34, 40], fill="white")
        d.ellipse([28, 6, 44, 16], fill="white")
        d.ellipse([30, 36, 48, 54], fill="white")
        d.rectangle([46, 14, 50, 40], fill="white")
        d.ellipse([44, 10, 60, 20], fill="white")

        def on_exit(icon, item):
            icon.stop()
            detach_from_desktop(WINDOW_TITLE)
            window.destroy()
            os._exit(0)

        menu = pystray.Menu(
            pystray.MenuItem("Apple Music Wallpaper", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", on_exit),
        )
        _tray_icon = pystray.Icon("amw", img, "Apple Music Wallpaper", menu)
        _tray_icon.run()
    except Exception as e:
        print(f"[Tray] {e}")


# ══════════════════════════════════════════
#  Main
# ══════════════════════════════════════════
WINDOW_TITLE = "AppleMusicWP_Desktop"


def main():
    w = user32.GetSystemMetrics(0)
    h = user32.GetSystemMetrics(1)

    html_path = resource_path(os.path.join("wallpaper", "index.html"))

    window = webview.create_window(
        WINDOW_TITLE,
        html_path,
        frameless=True,
        width=w,
        height=h,
        x=0,
        y=0,
    )

    def on_shown():
        # Small delay for WebView to initialize
        time.sleep(1)
        embed_into_desktop(WINDOW_TITLE)
        start_media_poll(window)

    def on_loaded():
        threading.Thread(target=on_shown, daemon=True).start()

    window.events.loaded += on_loaded

    # System tray in background thread
    threading.Thread(target=start_tray, args=(window,), daemon=True).start()

    webview.start()


if __name__ == "__main__":
    main()
