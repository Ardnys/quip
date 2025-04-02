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