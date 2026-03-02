import base64
import json
import sys
from io import BytesIO
from typing import Tuple

import cv2
import win32con
import win32gui
import win32process
from PIL import Image
from windows_capture import Frame, InternalCaptureControl, WindowsCapture

# Windows that are never useful to capture — same exclusion list OBS uses internally
_EXCLUDED_CLASSES = {
    "Progman",  # desktop
    "WorkerW",  # desktop wallpaper worker
    "Shell_TrayWnd",  # taskbar
    "Shell_SecondaryTrayWnd",
    "DV2ControlHost",  # start menu host
    "MsgrIMEWindowClass",
    "SysShadow",
    "Button",
    "Windows.UI.Core.CoreWindow",  # UWP shell chrome (not the app itself)
    "ApplicationFrameWindow",  # UWP frame — the real content is a child
    "MSCTFIME UI",
    "IME",
}

_EXCLUDED_TITLE_PREFIXES = (
    "Default IME",
    "MSCTFIME",
)


def _is_capturable(hwnd: int) -> bool:
    """Mirrors OBS's window filter logic."""
    if not win32gui.IsWindowVisible(hwnd):
        return False

    # Must have a non-empty title
    title = win32gui.GetWindowText(hwnd).strip()
    if not title:
        return False

    if any(title.startswith(p) for p in _EXCLUDED_TITLE_PREFIXES):
        return False

    class_name = win32gui.GetClassName(hwnd)
    if class_name in _EXCLUDED_CLASSES:
        return False

    # Must be a top-level window (no owner) — rules out tooltips, dropdowns, etc.
    if win32gui.GetWindow(hwnd, win32con.GW_OWNER):
        return False

    # Must have WS_EX_APPWINDOW or lack WS_EX_TOOLWINDOW to appear in the taskbar
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    is_tool = ex_style & win32con.WS_EX_TOOLWINDOW
    is_app = ex_style & win32con.WS_EX_APPWINDOW
    if is_tool and not is_app:
        return False

    # Must have non-zero area
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    if (right - left) <= 0 or (bottom - top) <= 0:
        return False

    return True


def _capture_thumbnail(window_name: str, size: Tuple[int, int]) -> str | None:
    capture = WindowsCapture(
        window_name=window_name,
        draw_border=False,
        cursor_capture=False,
        dirty_region=False,
    )

    img = None

    @capture.event
    def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
        nonlocal img
        buffer = frame.convert_to_bgr().frame_buffer
        rgb = cv2.cvtColor(buffer, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb, mode="RGB")

        capture_control.stop()

    @capture.event
    def on_closed():
        print("Capture closed")

    capture.start()

    if img:
        return _thumbnail_from_image(img, size)

    return None


def _thumbnail_from_image(img: Image.Image, thumb_size: Tuple[int, int]):
    img.thumbnail(size=thumb_size, resample=Image.Resampling.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=70, optimize=True)
    # convert to base64 string to put it in JSON
    return base64.b64encode(buf.getvalue()).decode()


def get_visible_windows(thumb_width: int = 640, thumb_height: int = 360) -> list[dict]:
    """
    Return capturable windows with metadata and a base64 JPEG thumbnail each.

    Each entry:
        {
            "hwnd":       int,
            "title":      str,
            "class_name": str,
            "pid":        int,
            "thumbnail":  str | None,   # base64 JPEG, None if window couldn't be captured
        }
    """
    results = []

    def _enum(hwnd, _):
        if not _is_capturable(hwnd):
            return

        title = win32gui.GetWindowText(hwnd).strip()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        thumbnail = _capture_thumbnail(title, (thumb_width, thumb_height))

        results.append(
            {
                "hwnd": hwnd,
                "title": title,
                "pid": pid,
                "thumbnail": thumbnail,
            }
        )

    win32gui.EnumWindows(_enum, None)
    return results


# there's a weird WinRT initialization error with calling windows-capture from
# aiohttp context. https://learn.microsoft.com/en-us/windows/win32/api/roapi/nf-roapi-roinitialize
# I don't think the fix is easily possible so instead I am giving windows-capture its own process.
if __name__ == "__main__":
    thumb_w = int(sys.argv[1]) if len(sys.argv) > 1 else 640
    thumb_h = int(sys.argv[2]) if len(sys.argv) > 2 else 360

    result = get_visible_windows(thumb_w, thumb_h)
    json.dump(result, sys.stdout)
