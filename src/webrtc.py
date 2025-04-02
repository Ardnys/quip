import json
import asyncio
import logging
import json

from pathlib import Path
from aiohttp import web
from aiortc import RTCSessionDescription, RTCPeerConnection
from aiortc.rtcrtpsender import RTCRtpSender

from capture import ScreenCaptureManager, CaptureStreamTrack
from visible_windows import get_visible_windows

logging.basicConfig(level=logging.DEBUG)

# assume we are in project dir
ROOT = Path.cwd()

pcs = set()

def force_codec(pc, sender, forced_codec):
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    transceiver.setCodecPreferences(
        [codec for codec in codecs if codec.mimeType == forced_codec]
    )

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])

    pc = RTCPeerConnection()
    pcs.add(pc)


    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # init window capture
    video = ScreenCaptureManager().video

    if video:
        video_sender = pc.addTrack(video)
        # here you force a codec
        force_codec(pc, video_sender, "video/H264")

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(content_type="application/json", text=json.dumps({
        "sdp": pc.localDescription.sdp, "type": pc.localDescription.type
    }))

async def index(request):
    return web.FileResponse(ROOT / "static" / "index.html")

async def visible_windows(request):
    vis_win = get_visible_windows()
    return web.Response(content_type="application/javascript", text=json.dumps({
        "visibleWindows": vis_win
    }))

async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

if __name__ == "__main__":
    app = web.Application()
    app.on_shutdown.append(on_shutdown)

    app.router.add_get("/", index)
    app.router.add_get("/visible_windows", visible_windows)
    app.router.add_static("/static/", ROOT / "static", name='static')
    app.router.add_post("/offer", offer)

    web.run_app(app, host="127.0.0.1", port=9119)
