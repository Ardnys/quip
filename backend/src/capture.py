import asyncio
import logging
import queue
import threading
import time
from fractions import Fraction
from typing import Optional, Set

import numpy as np
import sounddevice as sd
from aiortc.mediastreams import AUDIO_PTIME, MediaStreamError, MediaStreamTrack
from av import AudioFrame, VideoFrame
from av.audio.resampler import AudioResampler
from av.frame import Frame
from windows_capture import Frame as CaptureFrame
from windows_capture import InternalCaptureControl, WindowsCapture

logger = logging.getLogger(__name__)

VIDEO_CLOCK_RATE = 90000  # standard RTP video clock
# TODO: fix type hints and errors


class CaptureStreamTrack(MediaStreamTrack):
    def __init__(self, player, kind):
        super().__init__()
        self.kind = kind
        self._player = player
        self._queue: asyncio.Queue[Frame | None] = asyncio.Queue()
        self._started = False

    async def recv(self) -> Frame:
        if self.readyState != "live":
            raise MediaStreamError

        if not self._started:
            self._player._start(self)
            self._started = True

        data = await self._queue.get()
        if data is None:
            self.stop()
            raise MediaStreamError

        return data

    def stop(self):
        super().stop()
        if self._player is not None:
            self._player._stop(self)
            self._player = None


class ScreenCaptureManager:
    def __init__(
        self,
        cursor_capture: bool = True,
        draw_border: bool = False,
        monitor_index: Optional[int] = None,
        window_name: Optional[str] = None,
        audio_device: int = 0,
        audio_channels: int = 2,
        audio_samplerate: int = 48000,
    ):
        # ── Video capture ──────────────────────────────────────────────────
        self.__window_capture = WindowsCapture(
            cursor_capture=cursor_capture,
            draw_border=draw_border,
            monitor_index=monitor_index,
            window_name=window_name,
        )

        # ── Audio config ───────────────────────────────────────────────────
        self.__audio_device = audio_device
        self.__audio_channels = audio_channels
        self.__audio_samplerate = audio_samplerate
        self.__audio_queue: queue.SimpleQueue = queue.SimpleQueue()
        self.__audio_samples: int = 0
        self.__audio_resampler = AudioResampler(
            format="s16",
            layout="stereo",
            rate=audio_samplerate,
            frame_size=int(audio_samplerate * AUDIO_PTIME),
        )
        self.__audio_stream: Optional[sd.InputStream] = None

        # ── Tracks ────────────────────────────────────────────────────────
        self.audio: CaptureStreamTrack = CaptureStreamTrack(self, "audio")
        self.video: CaptureStreamTrack = CaptureStreamTrack(self, "video")

        # ── Thread management ─────────────────────────────────────────────
        # Lock protects __started and the thread handles
        self.__lock = threading.Lock()
        self.__started: Set[CaptureStreamTrack] = set()

        self.__video_quit = threading.Event()
        self.__audio_quit = threading.Event()

        self.__video_thread: Optional[threading.Thread] = None
        self.__audio_thread: Optional[threading.Thread] = None

        self.__start_time: Optional[float] = None
        self.__video_start_time: Optional[float] = None
        self.__video_pts: int = 0

    # ── Public entry point (called by CaptureStreamTrack.recv) ───────────────

    def _start(self, track: CaptureStreamTrack):
        with self.__lock:
            already_started = bool(self.__started)
            self.__started.add(track)

        if already_started:
            # Both tracks have now called _start; workers are already running
            return

        # First track to call _start kicks everything off
        self.__start_time = time.time()
        self.__start_video(asyncio.get_event_loop())
        self.__start_audio(asyncio.get_event_loop())

    # ── Video ─────────────────────────────────────────────────────────────────

    def __start_video(self, event_loop: asyncio.AbstractEventLoop):
        self.__video_quit.clear()
        self.__video_thread = threading.Thread(
            name="capture-video",
            target=self.__video_worker,
            args=(event_loop,),
        )
        self.__video_thread.start()

    def __video_worker(self, event_loop: asyncio.AbstractEventLoop):
        @self.__window_capture.event
        def on_frame_arrived(
            frame: CaptureFrame, capture_control: InternalCaptureControl
        ):
            # TODO: throttling
            if self.__video_quit.is_set():
                capture_control.stop()
                return

            vframe = self.__decode_frame(frame)
            asyncio.run_coroutine_threadsafe(self.video._queue.put(vframe), event_loop)

        @self.__window_capture.event
        def on_closed():
            self.__log_debug("Window capture closed")
            # Signal the audio side to stop too
            asyncio.run_coroutine_threadsafe(self.audio._queue.put(None), event_loop)

        self.__window_capture.start()  # blocks until capture_control.stop() is called
        self.__log_debug("Video worker exited")

    def __decode_frame(self, frame: CaptureFrame) -> VideoFrame:
        now = time.monotonic()
        if self.__video_start_time is None:
            self.__video_start_time = now

        # Convert elapsed wall time to 90kHz RTP clock ticks
        elapsed = now - self.__video_start_time
        pts = int(elapsed * VIDEO_CLOCK_RATE)

        fbuffer = frame.convert_to_bgr().frame_buffer
        vframe = VideoFrame.from_ndarray(fbuffer, format="bgr24")
        vframe.pts = pts
        vframe.time_base = Fraction(1, VIDEO_CLOCK_RATE)
        return vframe

    # ── Audio ─────────────────────────────────────────────────────────────────

    def __start_audio(self, event_loop: asyncio.AbstractEventLoop):
        self.__audio_quit.clear()
        self.__audio_stream = sd.InputStream(
            callback=self.__audio_callback,
            device=self.__audio_device,
            dtype="int16",
            channels=self.__audio_channels,
            samplerate=self.__audio_samplerate,
            blocksize=int(self.__audio_samplerate * AUDIO_PTIME),
        )
        self.__audio_thread = threading.Thread(
            name="capture-audio",
            target=self.__audio_worker,
            args=(event_loop,),
        )
        self.__audio_thread.start()

    def __audio_callback(self, indata, frame_count, time_info, status):
        if status:
            self.__log_debug(
                f"Audio status: {status}, frame_count={frame_count}, "
                f"expected={int(self.__audio_samplerate * AUDIO_PTIME)}"
            )
        if self.__audio_quit.is_set():
            raise sd.CallbackStop
        self.__audio_queue.put_nowait(
            indata[:, :2].copy()
        )  # not convinced about copy but oh well

    def __audio_worker(self, event_loop: asyncio.AbstractEventLoop):
        audio_time_base = Fraction(1, self.__audio_samplerate)
        self.__log_debug("Audio worker started")

        with self.__audio_stream:
            while not self.__audio_quit.is_set():
                try:
                    # TODO: still input overflows
                    raw = self.__audio_queue.get(timeout=0.1)
                except queue.Empty:
                    self.__log_debug("Empty audio queue")
                    continue

                planar = np.ascontiguousarray(raw.T)
                aframe = AudioFrame.from_ndarray(planar, format="s16p", layout="stereo")
                aframe.sample_rate = self.__audio_samplerate

                for frame in self.__audio_resampler.resample(aframe):
                    frame.pts = self.__audio_samples
                    frame.time_base = audio_time_base
                    self.__audio_samples += frame.samples
                    asyncio.run_coroutine_threadsafe(
                        self.audio._queue.put(frame), event_loop
                    )

        asyncio.run_coroutine_threadsafe(self.audio._queue.put(None), event_loop)
        self.__log_debug("Audio worker exited")

    # ── Stop ─────────────────────────────────────────────────────────────────

    def _stop(self, track: CaptureStreamTrack):
        """Called by CaptureStreamTrack.stop(). May be called from any thread."""
        with self.__lock:
            self.__started.discard(track)
            remaining = len(self.__started)

        self.__log_debug(f"_stop called for {track.kind}, {remaining} tracks remaining")

        if remaining > 0:
            return  # other track still active

        self.__shutdown()

    def __shutdown(self):
        """Signal both workers to stop. Does NOT join — avoids deadlock."""
        self.__log_debug("Shutting down capture")
        self.__video_quit.set()
        self.__audio_quit.set()
        # The workers are daemon threads — they will be reaped by the OS
        # when the process exits. If you need a clean join, call shutdown_sync()
        # from a non-worker thread (e.g. the aiohttp request handler).

    def shutdown_sync(self, timeout: float = 5.0):
        """
        Graceful blocking shutdown. Call this from the aiohttp peer-connection
        cleanup path (a non-capture thread) when you need to ensure workers
        have fully stopped before releasing resources.
        """
        self.__shutdown()
        for thread, name in [
            (self.__video_thread, "video"),
            (self.__audio_thread, "audio"),
        ]:
            if thread and thread.is_alive():
                thread.join(timeout=timeout)
                if thread.is_alive():
                    self.__log_debug(f"{name} worker did not stop within {timeout}s")

    def __log_debug(self, msg: str, *args) -> None:
        logger.debug(f"ScreenCaptureManager {msg}", *args)
