import threading
import asyncio
import time
import logging
import cv2

from typing import Optional, Set
from aiortc.mediastreams import MediaStreamError, MediaStreamTrack
from windows_capture import WindowsCapture, Frame, InternalCaptureControl
from av import VideoFrame
from fractions import Fraction

logger = logging.getLogger(__name__)

class CaptureStreamTrack(MediaStreamTrack):
    def __init__(self, player):
        super().__init__()
        self.kind = "video"
        self._player = player
        self._queue: asyncio.Queue[Frame] = asyncio.Queue()
        self._start: Optional[float] = None
        self._started = False

    async def recv(self) -> Frame:
        # "ended" or "live"
        if self.readyState != "live":
            raise MediaStreamError

        if not self._started:
            self._player._start(self)
            self._started = True

        data = await self._queue.get()
        if data is None:
            self.stop()
            raise MediaStreamError

        # TODO: throttling

        print("bai bai frame")

        fbuf = data.frame_buffer
        vframe = VideoFrame.from_ndarray(fbuf, format="bgr24")
        vframe.pts = data.timespan
        vframe.time_base = Fraction(10, -9)

        return vframe

    def stop(self):
        super().stop()
        if self._player is not None:
            self._player._stop(self)
            self._player = None

# TODO add audio
class ScreenCaptureManager:
    def __init__(self, cursor_capture=True, draw_border=True, monitor_index=None, window_name=None, decode=True):
        self.__capture = WindowsCapture(
            cursor_capture=cursor_capture,
            draw_border=draw_border,
            monitor_index=monitor_index,
            window_name=window_name,
        )
        self.__thread: Optional[threading.Thread] = None
        self.__thread_quit: Optional[threading.Event] = None

        # examine streams
        self.__started: Set[CaptureStreamTrack] = set()
        self.__decode = decode
        self.__audio: Optional[CaptureStreamTrack] = None
        self.video: Optional[CaptureStreamTrack] = CaptureStreamTrack(self)
        self.__start_time = None
        self.__last_frame_time = None
        self.__frame_interval = 1.0 / 24

        # hopefully sets up the handler
        # self._capture_worker(self.video, asyncio.get_event_loop(), self.__thread_quit)

    def _start(self, track: CaptureStreamTrack):
        self.__log_debug("_start called")
        self.__start_time = time.time()
        self.__started.add(track)

        if self.__thread is None:
            self.__log_debug("Starting capture worker thread")
            self.__thread_quit = threading.Event()
            self.__thread = threading.Thread(
                name="media-player",
                target=self._capture_worker,
                args=(self.video, asyncio.get_event_loop(), self.__thread_quit)
            )
            self.__thread.start()


    def _capture_worker(self, video_track, event_loop, quit_event):
        if self.__capture is None:
            self.__log_debug("There is no active capture")
            return

        @self.__capture.event
        def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
            self.__log_debug("New frame")
            now = time.time()
            if self.__last_frame_time is None:
                self.__last_frame_time = now

            if now - self.__last_frame_time < self.__frame_interval:
                # skip frame
                return

            if quit_event.is_set():
                capture_control.stop()
                self._stop(video_track)
                return

            decoded_frame = self._decode_frame(frame)
            asyncio.run_coroutine_threadsafe(video_track._queue.put(decoded_frame), event_loop)

        @self.__capture.event
        def on_closed():
            # this event does not seem to work so i would not rely on this
            self.__log_debug("Capture closed")

        if self.__start_time is not None:
            self.__capture.start()


    def _decode_frame(self, frame: Frame) -> Frame:
        fbuffer = frame.convert_to_bgr().frame_buffer
        # i down scaled it to make it fast for now
        scaled_buffer = cv2.resize(fbuffer, dsize=(1920, 1080), interpolation=cv2.INTER_AREA)
        # still works even if i don't use the resized image???
        return Frame(frame_buffer=scaled_buffer, width=1920, height=1080, timespan=frame.timespan)


    def _stop(self, track: CaptureStreamTrack):
        self.__log_debug("Called _stop")
        self.__started.discard(track)

        if not self.__started and self.__thread is not None:
            self.__log_debug("Stopping capture worker thread")
            self.__thread_quit.set()
            self.__thread.join()
            self.__thread = None

        if not self.__started and self.__capture is not None:
            self.__capture = None
    
    def __log_debug(self, msg: str, *args) -> None:
        logger.debug(f"CapturePlayer {msg}", *args)
