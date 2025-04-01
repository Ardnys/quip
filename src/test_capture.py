import asyncio
import logging
from capture import ScreenCaptureManager

logging.basicConfig(level=logging.DEBUG)

async def test_capture():

    player = ScreenCaptureManager(cursor_capture=True, draw_border=False)
    video = player.video

    try:
        # kinda blows up BUT it works
        while True:
            print("Asking for frames")
            frame = await video.recv()
            print(f"Received frame - with dimensions ({frame.width}, {frame.height})")

    except Exception as e:
        print(f"Error during capture: {e}")

    return player

if __name__ == "__main__":
    asyncio.run(test_capture())
