from windows_capture import WindowsCapture, Frame, InternalCaptureControl
import cv2
import time
import win32gui

# TODO this gets a bit too much stuff like overlays and whatnot. I want to be exactly like OBS
def get_visible_windows():
    visible_windows = []

    def enum_windows(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd).strip()
            class_name = win32gui.GetClassName(hwnd)
            if title:
                visible_windows.append((title, class_name))

    win32gui.EnumWindows(enum_windows, None)
    return visible_windows

visible_windows = get_visible_windows()

# recording the screen to a video example code
class Cap:
    def __init__(self):
        self.capture = WindowsCapture(
            cursor_capture=True,
            draw_border=True,
            monitor_index=None,
            window_name=None,
        )

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        width, height = 1920, 1080
        self.video = cv2.VideoWriter(filename="capture.mp4", fourcc=fourcc, frameSize=(width, height), fps=24)
        self._start = None

        @self.capture.event
        def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
            print("New frame")
            elapsed = time.time() - self._start
            if elapsed > 2:
                capture_control.stop()
                self.stop()

            img = frame.convert_to_bgr().frame_buffer
            scaled_img = cv2.resize(img, dsize=(width, height), interpolation=cv2.INTER_CUBIC)
            self.video.write(scaled_img)

        @self.capture.event
        def on_closed():
            print("capture closed")

    def start(self):
        self._start = time.time()
        self.capture.start()

    def stop(self):
        # TODO: this is not available but i think i can do it via message queue
        self.video.release()
        pass

# cap = Cap()
# print(cap.start())
# cap.start()

