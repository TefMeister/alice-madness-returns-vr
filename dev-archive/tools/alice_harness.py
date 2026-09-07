#!/usr/bin/env python3
"""alice_harness.py - drive and observe Alice: Madness Returns from outside the game.

Written 2026-09-07 for the /lm lane. Nothing here is Alice-specific except the
window-title substring and the key table; the traps it works around are recorded
in ai-game-control-profiles/UNIVERSAL.md and were paid for in earlier sessions:

  * capture with BitBlt from the SCREEN DC (what ImageGrab.grab does on Windows),
    never PrintWindow - PrintWindow silently serves a stale DWM-cached frame the
    moment the game stops presenting (paused, in a menu, mid-load), with no error.
  * SendInput with SCANCODES, and arrow keys need KEYEVENTF_EXTENDEDKEY - without
    the flag scancode 0x50 is numpad-2, the menu ignores it, and nothing errors.
  * foreground the window before acting and re-check it; synthetic input follows
    focus and UE3 throttles unfocused.
  * the proxy polls hotkeys on a RISING EDGE once per Present, so a key must be
    held long enough for one Present to see it down (default 80 ms) and released
    long enough for the next to see it up (default 150 ms gap).

Usage:
  find                       report the window handle, title, client rect
  focus                      bring it to the foreground (and verify)
  key NAME [count]           send a key by name, count times
  shot PATH                  one capture of the client area
  burst PREFIX N [ms]        N captures as fast as possible (default 0 ms apart)
  shift A B                  horizontal displacement of B relative to A, in pixels
  cluster PREFIX             group a burst into displacement clusters (wiggle test)
"""
import ctypes
import ctypes.wintypes as wt
import glob
import os
import sys
import time

user32 = ctypes.WinDLL("user32", use_last_error=True)
TITLE_SUBSTR = "Alice"

# --- scancode table (DIK). ext=True keys are the grey navigation block; without
# --- the extended flag these collide with the numpad and are silently ignored.
KEYS = {
    "ENTER": (0x1C, False), "ESC": (0x01, False), "ESCAPE": (0x01, False),
    "UP": (0x48, True), "DOWN": (0x50, True), "LEFT": (0x4B, True), "RIGHT": (0x4D, True),
    "W": (0x11, False), "A": (0x1E, False), "S": (0x1F, False), "D": (0x20, False),
    "SPACE": (0x39, False),
    "F6": (0x40, False), "F7": (0x41, False), "F8": (0x42, False),
    "F9": (0x43, False), "F10": (0x44, False), "F11": (0x57, False), "F12": (0x58, False),
}

KEYEVENTF_EXTENDEDKEY, KEYEVENTF_KEYUP, KEYEVENTF_SCANCODE = 0x0001, 0x0002, 0x0008
INPUT_KEYBOARD = 1


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wt.WORD), ("wScan", wt.WORD), ("dwFlags", wt.DWORD),
                ("time", wt.DWORD), ("dwExtraInfo", ctypes.POINTER(wt.ULONG))]


class _IU(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("pad", ctypes.c_byte * 32)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wt.DWORD), ("u", _IU)]


def _send(scan, ext, up):
    flags = KEYEVENTF_SCANCODE
    if ext:
        flags |= KEYEVENTF_EXTENDEDKEY
    if up:
        flags |= KEYEVENTF_KEYUP
    inp = INPUT(type=INPUT_KEYBOARD, u=_IU(ki=KEYBDINPUT(0, scan, flags, 0, None)))
    if user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT)) != 1:
        raise OSError("SendInput failed: %d" % ctypes.get_last_error())


def find_window():
    out = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        n = user32.GetWindowTextLengthW(hwnd)
        if n:
            b = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, b, n + 1)
            t = b.value
            if TITLE_SUBSTR.lower() in t.lower() and "harness" not in t.lower():
                out.append((hwnd, t))
        return True

    user32.EnumWindows(cb, 0)
    return out


def need_window():
    w = find_window()
    if not w:
        sys.exit("NO WINDOW: nothing visible matching %r - is the game running?" % TITLE_SUBSTR)
    return w[0]


def client_rect(hwnd):
    r = wt.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(r))
    p = wt.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(p))
    return (p.x, p.y, p.x + r.right, p.y + r.bottom)


def focus(hwnd):
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.15)
    return user32.GetForegroundWindow() == hwnd


def press(name, count=1, hold=0.08, gap=0.15):
    hwnd, _ = need_window()
    if not focus(hwnd):
        print("WARN: could not foreground the window; input may go elsewhere")
    scan, ext = KEYS[name.upper()]
    for _ in range(count):
        _send(scan, ext, False)
        time.sleep(hold)
        _send(scan, ext, True)
        time.sleep(gap)


def grab(path):
    from PIL import ImageGrab
    hwnd, _ = need_window()
    focus(hwnd)
    img = ImageGrab.grab(bbox=client_rect(hwnd), all_screens=True)
    img.save(path)
    return img


def col_profile(img):
    import numpy as np
    a = np.asarray(img.convert("L"), dtype=np.float64)
    p = a.mean(axis=0)
    return p - p.mean()


def h_shift(a, b, max_px=160):
    """Horizontal displacement of b relative to a, by 1-D cross-correlation of
    column-mean profiles. A stereo shear is a COHERENT horizontal translation,
    which is what this measures; scene animation is not, and shows up as a flat,
    low-peak correlation instead."""
    import numpy as np
    pa, pb = col_profile(a), col_profile(b)
    best, bestv = 0, -1e30
    for d in range(-max_px, max_px + 1):
        if d < 0:
            x, y = pa[-d:], pb[:len(pb) + d]
        elif d > 0:
            x, y = pa[:len(pa) - d], pb[d:]
        else:
            x, y = pa, pb
        if len(x) < 64:
            continue
        den = (float(np.linalg.norm(x)) * float(np.linalg.norm(y))) or 1.0
        v = float(np.dot(x, y) / den)
        if v > bestv:
            best, bestv = d, v
    return best, bestv


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]

    if cmd == "find":
        w = find_window()
        for h, t in w:
            print("hwnd=0x%X  title=%r  client=%s" % (h, t, client_rect(h)))
        if not w:
            print("NO WINDOW matching %r" % TITLE_SUBSTR)

    elif cmd == "focus":
        h, t = need_window()
        print("focused" if focus(h) else "FAILED to focus", t)

    elif cmd == "key":
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        press(sys.argv[2], n)
        print("sent %s x%d" % (sys.argv[2], n))

    elif cmd == "shot":
        grab(sys.argv[2])
        print("saved", sys.argv[2])

    elif cmd == "burst":
        from PIL import ImageGrab
        prefix, n = sys.argv[2], int(sys.argv[3])
        iv = (float(sys.argv[4]) / 1000.0) if len(sys.argv) > 4 else 0.0
        hwnd, _ = need_window()
        focus(hwnd)
        box = client_rect(hwnd)
        for i in range(n):
            ImageGrab.grab(bbox=box, all_screens=True).save("%s%02d.png" % (prefix, i))
            if iv:
                time.sleep(iv)
        print("burst of %d -> %s*.png" % (n, prefix))

    elif cmd == "shift":
        from PIL import Image
        d, v = h_shift(Image.open(sys.argv[2]), Image.open(sys.argv[3]))
        print("dx=%+d px  peak_corr=%.4f" % (d, v))

    elif cmd == "cluster":
        from PIL import Image
        files = sorted(glob.glob(sys.argv[2] + "*.png"))
        if len(files) < 2:
            sys.exit("need >=2 frames")
        ref = Image.open(files[0])
        print("%-28s %8s %10s" % ("frame", "dx", "corr"))
        ds = []
        for f in files:
            d, v = h_shift(ref, Image.open(f))
            ds.append(d)
            print("%-28s %+8d %10.4f" % (os.path.basename(f), d, v))
        lo, hi = min(ds), max(ds)
        print("\nspread: %d px  (min %+d, max %+d, distinct %s)"
              % (hi - lo, lo, hi, sorted(set(ds))))

    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
