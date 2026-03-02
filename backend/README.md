# quip — backend

Python/aiohttp backend for quip. Captures a target application window and its audio, then streams both to the browser over WebRTC.

**Windows only.** Relies on the Windows Graphics Capture API via [windows-capture](https://github.com/NiiightmareXD/windows-capture) for both window thumbnails and the live stream, and [sounddevice](https://python-sounddevice.readthedocs.io) for audio input.

## Modules

- **`src/capture.py`** — `ScreenCaptureManager`: manages the video capture thread, audio input stream, and feeds encoded frames into the aiortc pipeline.
- **`src/webrtc.py`** — aiohttp route handlers for `/api/offer`, `/api/windows`, `/api/audio_devices`, and static file serving.
- **`src/visible_windows.py`** — standalone script invoked as a subprocess to enumerate capturable windows and capture their thumbnails; runs in its own process to avoid WinRT apartment conflicts with the aiohttp event loop.

## Development

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run main.py
```

The frontend dev server (Vite) must also be running separately. See the frontend README.

## Contributing

Contributions are welcome. Known rough edges worth tackling: video/audio sync, occasional audio buffering, hard-coded virtual audio device channels, and hwnd-based window targeting (currently title-based).
