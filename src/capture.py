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


class CaptureStreamTrack(MediaStreamTrack):
    def __init__(self, player, kind):
        super().__init__()
        self.kind = kind
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

        return data

    def stop(self):
        super().stop()
        if self._player is not None:
            self._player._stop(self)
            self._player = None


class ScreenCaptureManager:
    def __init__(
        self,
        cursor_capture=True,
        draw_border=True,
        monitor_index=None,
        window_name=None,
        decode=True,
        pid=None,
    ):
        self.__window_capture = WindowsCapture(
            cursor_capture=cursor_capture,
            draw_border=draw_border,
            monitor_index=monitor_index,
            window_name=window_name,
        )

        self.__video_thread: Optional[threading.Thread] = None
        self.__audio_thread: Optional[threading.Thread] = None
        # TODO: clean up the thread quitting stuff
        self.__thread_quit: Optional[threading.Event] = None
        self.__audio_thread_quit: Optional[threading.Event] = None

        # examine streams
        self.__started: Set[CaptureStreamTrack] = set()
        self.__decode = decode
        # TODO: make these properties
        self.audio: Optional[CaptureStreamTrack] = CaptureStreamTrack(self, "audio")
        self.video: Optional[CaptureStreamTrack] = CaptureStreamTrack(self, "video")
        self.__start_time = None
        self.__last_frame_time = None
        self.__frame_interval = 1.0 / 24

        # Audio state — must persist across callbacks
        self.__audio_queue: queue.SimpleQueue = queue.SimpleQueue()
        self.__audio_samples = 0
        # TODO: Fix the rate
        self.__audio_resampler = AudioResampler(
            format="s16",
            layout="stereo",
            rate=48000,
            frame_size=int(48000 * AUDIO_PTIME),  # 960
        )

        callback = self._audio_stream_callback_wrapper()
        # TODO: choose the device from UI somehow
        # TODO: can i use my bindings? I worked so hard for that
        self.__audio_stream = sd.InputStream(
            callback=callback,
            device=2,
            dtype="int16",
            channels=16,
            samplerate=48000,  # pin the rate explicitly
            blocksize=960,  # match frame_size so resampler outputs clean frames
        )

        # hopefully sets up the handler
        # self._capture_worker(self.video, asyncio.get_event_loop(), self.__thread_quit)

    # TODO: honestly they should be different for Audio and Video
    def _start(self, track: CaptureStreamTrack):
        self.__log_debug("_start called")
        self.__start_time = time.time()
        self.__started.add(track)

        if self.__video_thread is None:
            self.__log_debug("Starting capture worker thread")
            self.__thread_quit = threading.Event()
            self.__video_thread = threading.Thread(
                name="video-player",
                target=self._capture_worker,
                args=(self.video, asyncio.get_event_loop(), self.__thread_quit),
            )
            self.__video_thread.start()

        if self.__audio_thread is None:
            self.__log_debug("Starting audio capture worker thread")
            self.__audio_thread_quit = threading.Event()
            self.__audio_thread = threading.Thread(
                name="audio-player",
                target=self._audio_worker,
                args=(self.audio, asyncio.get_event_loop(), self.__audio_thread_quit),
            )
            self.__audio_thread.start()

    def _audio_stream_callback_wrapper(self):
        def callback(indata, frame_count, time_info, status):
            if status:
                self.__log_debug(f"InputStream status: {status}")
            self.__audio_queue.put_nowait(indata[:, :2])

        return callback

    def _audio_worker(self, audio_track, event_loop, quit_event):
        if self.__audio_stream is None:
            self.__log_debug("No active audio stream")
            return

        audio_time_base = Fraction(1, 48000)

        self.__log_debug("Starting audio stream")
        with self.__audio_stream:
            while not quit_event.is_set():
                try:
                    # Block with timeout so we can check quit_event
                    raw = self.__audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                self.__log_debug("got new audio")
                # All the heavy lifting happens here, in the worker thread
                planar = np.ascontiguousarray(raw.T)
                aframe = AudioFrame.from_ndarray(planar, format="s16p", layout="stereo")
                aframe.sample_rate = 48000

                for frame in self.__audio_resampler.resample(aframe):
                    frame.pts = self.__audio_samples
                    frame.time_base = audio_time_base
                    self.__audio_samples += frame.samples  # monotonically increasing
                    asyncio.run_coroutine_threadsafe(
                        audio_track._queue.put(frame), event_loop
                    )

        # Signal downstream that the stream is done
        asyncio.run_coroutine_threadsafe(audio_track._queue.put(None), event_loop)

    def _capture_worker(self, video_track, event_loop, quit_event):
        if self.__window_capture is None:
            self.__log_debug("There is no active capture")
            return

        @self.__window_capture.event
        def on_frame_arrived(
            frame: CaptureFrame, capture_control: InternalCaptureControl
        ):
            self.__log_debug("New window frame")
            # TODO: is this needed?
            # now = time.time()
            # if self.__last_frame_time is None:
            #     self.__last_frame_time = now

            # if now - self.__last_frame_time < self.__frame_interval:
            #     # skip frame
            #     return

            if quit_event.is_set():
                capture_control.stop()
                self._stop(video_track)
                return

            decoded_frame = self._decode_frame(frame)
            asyncio.run_coroutine_threadsafe(
                video_track._queue.put(decoded_frame), event_loop
            )

        @self.__window_capture.event
        def on_closed():
            # this event does not seem to work so i would not rely on this
            self.__log_debug("Capture closed")

        if self.__start_time is not None:
            self.__window_capture.start()

    def _decode_frame(self, frame: CaptureFrame) -> VideoFrame:
        fbuffer = frame.convert_to_bgr().frame_buffer
        # i down scaled it to make it fast for now
        # scaled_buffer = cv2.resize(
        #     fbuffer, dsize=(1920, 1080), interpolation=cv2.INTER_AREA
        # )
        # still works even if i don't use the resized image???

        vframe = VideoFrame.from_ndarray(fbuffer, format="bgr24")
        vframe.pts = frame.timespan
        vframe.time_base = Fraction(1, 10_000_000)

        return vframe

    # TODO: this stop isn't functioning properly. It should be graceful
    # There are all sorts of red flags:
    # DEBUG:aiortc.rtcdtlstransport:RTCDtlsTransport(client) - DTLS shutdown by remote party
    # DEBUG:aiortc.rtcdtlstransport:RTCDtlsTransport(client) - State.CONNECTED -> State.CLOSED
    # DEBUG:aioice.ice:Connection(2) protocol(5) error_received([WinError 10054] An existing connection was forcibly closed by the remote host)
    # DEBUG:capture:CapturePlayer Called _stop
    # DEBUG:aiortc.rtcrtpsender:RTCRtpSender(video) - RTP finished
    # DEBUG:aiortc.rtcrtpsender:RTCRtpSender(video) > RtcpByePacket(sources=[256257065])
    # DEBUG:aiortc.rtcrtpsender:RTCRtpSender(video) - RTCP finished
    # DEBUG:capture:CapturePlayer Called _stop
    # DEBUG:capture:CapturePlayer Stopping capture worker thread
    # DEBUG:capture:CapturePlayer got new audio
    # DEBUG:capture:CapturePlayer New window frame
    # DEBUG:capture:CapturePlayer Called _stop
    # DEBUG:capture:CapturePlayer Stopping capture worker thread
    # DEBUG:capture:CapturePlayer got new audio
    # Exception in thread video-player: (at line 210)
    # DEBUG:capture:CapturePlayer got new audio
    def _stop(self, track: CaptureStreamTrack):
        self.__log_debug("Called _stop")
        self.__started.discard(track)

        if not self.__started and self.__video_thread is not None:
            self.__log_debug("Stopping capture worker thread")
            self.__thread_quit.set()
            self.__video_thread.join()
            self.__video_thread = None

        if not self.__started and self.__audio_thread is not None:
            self.__log_debug("stopping audio worker thread")
            self.__audio_thread_quit.set()
            self.__audio_thread.join()
            self.__audio_thread = None

        if not self.__started and self.__window_capture is not None:
            self.__window_capture = None

        if not self.__started and self.__audio_stream is not None:
            self.__audio_stream = None

    def __log_debug(self, msg: str, *args) -> None:
        logger.debug(f"CapturePlayer {msg}", *args)
