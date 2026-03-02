import asyncio
import logging
import webbrowser
from pathlib import Path

from aiohttp import web

from src.webrtc import get_audio_devices, offer, on_shutdown, visible_windows

ROOT = Path(__file__).parent

STATIC_APP = ROOT / "static" / "app"
IS_PRODUCTION = STATIC_APP.exists()


async def serve_index(request):
    index = STATIC_APP / "index.html"
    if not index.exists():
        return web.Response(status=404, text="Frontend not built. Run: uv run build.py")
    return web.FileResponse(index)


def open_browser_when_ready(host: str, port: int, delay: float = 1.5):
    """Open the browser after a short delay to let the server start."""

    async def _open(app):
        await asyncio.sleep(delay)
        url = f"http://{host}:{port}"
        print(f"  Opening {url}")
        webbrowser.open(url)

    return _open


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    HOST = "127.0.0.1"
    PORT = 9119

    app = web.Application()

    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/api/windows", visible_windows)
    app.router.add_get("/api/audio_devices", get_audio_devices)
    app.router.add_post("/api/offer", offer)

    mode = "production" if IS_PRODUCTION else "development"
    print(f"\nquip starting in {mode} mode")
    print(f"  http://{HOST}:{PORT}\n")

    if IS_PRODUCTION:
        # only start up browser on production
        app.on_startup.append(open_browser_when_ready(HOST, PORT))
        app.router.add_get("/", serve_index)
        app.router.add_static("/", STATIC_APP)
        app.router.add_static("/assets", STATIC_APP / "assets")
        open_browser_when_ready(HOST, PORT)

    web.run_app(app, host=HOST, port=PORT, print=lambda *a, **k: None)
