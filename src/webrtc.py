import json
import asyncio
import logging

from pathlib import Path
from aiohttp import web
from aiortc import RTCSessionDescription, RTCPeerConnection
from aiortc.rtcrtpsender import RTCRtpSender
from capture import ScreenCaptureManager, CaptureStreamTrack

logging.basicConfig(level=logging.DEBUG)

# assume we are in project dir
ROOT = Path.cwd()

pcs = set()

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
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(content_type="application/json", text=json.dumps({
        "sdp": pc.localDescription.sdp, "type": pc.localDescription.type
    }))

async def index(request):
    with open(ROOT / 'index.html') as f:
        content = f.read()
        return web.Response(content_type="text/html", text=content)

async def javascript(request):
    with open(ROOT / 'client.js') as f:
        content = f.read()
        return web.Response(content_type="application/javascript", text=content)

async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

if __name__ == "__main__":
    app = web.Application()
    app.on_shutdown.append(on_shutdown)

    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)

    web.run_app(app, host="127.0.0.1", port=9119)
