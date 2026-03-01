import asyncio
import json
import logging
import sys
from pathlib import Path

import sounddevice as sd
from aiohttp import web
from aiortc import (
    RTCConfiguration,
    RTCIceServer,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.rtcrtpsender import RTCRtpSender

from capture import ScreenCaptureManager

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

# assume we are in project dir
ROOT = Path.cwd()

VISIBLE_WINDOWS_SCRIPT = Path(__file__).parent / "visible_windows.py"

pcs = set()


def force_codec(pc, sender, forced_codec):
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    transceiver.setCodecPreferences(
        [codec for codec in codecs if codec.mimeType == forced_codec]
    )


"""
{
    sdp: pc.localDescription.sdp,
    type: pc.localDescription.type,
    // window identity — backend WILL EVENTUALLY hwnd; but for now title
    hwnd: payload.hwnd,
    windowTitle: payload.windowTitle,
    audioDevice: payload.audioDevice,
    videoCodec: payload.videoCodec,
    audioCodec: payload.audioCodec,
    captureCursor: payload.captureCursor,
    drawBorder: payload.drawBorder,
    randomlyFart: payload.randomlyFart,
}
"""


# TODO: pydantic probs?
async def offer(request):
    params = await request.json()

    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection(
        configuration=RTCConfiguration(
            iceServers=[RTCIceServer(urls="stun:stun.l.google.com:19302")]
        )
    )
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"Connection state is {pc.connectionState}")
        # TODO: also handle closed i think
        if pc.connectionState in ("failed", "closed"):
            await pc.close()
            pcs.discard(pc)

    # init window capture
    _hwnd = params["hwnd"]  # TODO: use this when windows_capture is updated
    window_title = params["windowTitle"]
    cursor_capture = params["captureCursor"]  # lol
    draw_border = params["drawBorder"]
    audio_device = params["audioDevice"]

    capture_manager = ScreenCaptureManager(
        window_name=window_title,
        audio_device=audio_device,
        cursor_capture=cursor_capture,
        draw_border=draw_border,
        audio_channels=16,
    )
    video = capture_manager.video
    audio = capture_manager.audio

    if video:
        video_sender = pc.addTrack(video)
        # here you force a codec
        force_codec(pc, video_sender, "video/AV1")

    if audio:
        audio_sender = pc.addTrack(audio)
        force_codec(pc, audio_sender, "audio/opus")

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


async def index(request):
    return web.FileResponse(ROOT / "static" / "index.html")


async def visible_windows(request):
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        str(VISIBLE_WINDOWS_SCRIPT),
        "640",
        "360",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        logger.error("visible_windows subprocess failed: %s", stderr.decode())
        return web.Response(status=500, text="Failed to enumerate windows")

    return web.Response(
        content_type="application/json",
        body=b'{"windows":' + stdout + b"}",
    )


async def get_audio_devices(request):
    devices = sd.query_devices()
    print(devices)
    return web.Response(content_type="application/javascript", text=json.dumps(devices))


async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


if __name__ == "__main__":
    app = web.Application()
    app.on_shutdown.append(on_shutdown)

    app.router.add_get("/", index)
    app.router.add_get("/windows", visible_windows)
    app.router.add_get("/audio_devices", get_audio_devices)
    app.router.add_static("/static/", ROOT / "static", name="static")
    app.router.add_post("/offer", offer)

    web.run_app(app, host="127.0.0.1", port=9119)
