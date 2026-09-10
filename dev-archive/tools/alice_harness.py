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

CAMERA CONTROL - FOUR ROUTES, CHEAPEST AND MOST PRECISE FIRST
  console CMD...             write the `exec` file and press the bound key   [route 1]
  bugit                      shorthand for `console BugIt` - prints pose     [route 1]
  bugitgo X Y Z P YA R       set location AND rotation absolutely            [route 1]
  mouse DX DY [steps]        relative mouse move via SendInput               [route 4]
  click [left|right] [n]     press a mouse BUTTON (Alice's attack is left)
  ballistics                 report/pin the pointer acceleration settings    [route 4 prereq]

  The order is not arbitrary. A /gr drop on 2026-09-07 established that the
  console is a full Python->game channel over ONE keypress, and that UE3's
  `BugItGo` sets location and rotation ABSOLUTELY while `BugIt` prints them
  back. That makes camera aim repeatable and SELF-VERIFYING - "did the camera
  move?" becomes a number rather than a screenshot judgement. Mouse injection is
  the least precise of the four and carries two documented hazards (see mouse()),
  so it is last, not first.

  !! NONE OF THE CAMERA ROUTES HAS BEEN RUN. They are written, not tested.
  `bugit` is the one command that decides the scope of all of them: it prints a
  location and rotation (route 1 is live, and everything else is optional), or it
  errors (the cheat manager is not exposed in this retail build).
"""
import ctypes
import ctypes.wintypes as wt
import glob
import os
import sys
import time

# The Windows console defaults to cp1252, which cannot encode every character a
# message might carry - and an UnencodableError here would kill the harness in the
# middle of a live session, after the input has already been sent. Measured
# 2026-09-08: a warning line containing a non-ASCII glyph did exactly that.
# Printed text below is kept ASCII anyway; this is the floor under that habit.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass

user32 = ctypes.WinDLL("user32", use_last_error=True)
TITLE_SUBSTR = "Alice"

# --- scancode table (DIK). ext=True keys are the grey navigation block; without
# --- the extended flag these collide with the numpad and are silently ignored.
KEYS = {
    "ENTER": (0x1C, False), "ESC": (0x01, False), "ESCAPE": (0x01, False),
    "UP": (0x48, True), "DOWN": (0x50, True), "LEFT": (0x4B, True), "RIGHT": (0x4D, True),
    "W": (0x11, False), "A": (0x1E, False), "S": (0x1F, False), "D": (0x20, False),
    "SPACE": (0x39, False),
    # T enters this game's BUILT-IN first-person camera (2026-09-09). It is not
    # a mod and needs no rebind: AliceControlLayout.ini ships
    #   KeyBindArray1=(Name="T",Command="EnterFPSByRS | OnRelease ToggleCloseFollowCamera")
    # and the same command sits on the pad's right-stick CLICK, which is why no
    # keyboard probe had ever found it. Verified live 2026-09-09 (n=1 launch):
    # one press and Alice leaves the frame.
    "T": (0x14, False),
    # NUMPAD. These share their scancodes with the arrow/nav cluster and are told
    # apart ONLY by the extended flag being ABSENT - which is the same trap the
    # toolkit records in the other direction (arrows NEED the flag). Sending an
    # arrow scancode without the flag is a numpad key, and nothing errors either way.
    "NP4": (0x4B, False), "NP6": (0x4D, False), "NP7": (0x47, False),
    # The head-offset hotkeys (2026-09-09). NumPad 5 / minus / plus are the
    # numpad keys AliceInput.ini does NOT bind - 2/4/6/7/8/9 are the camera
    # axes. Non-extended like the rest of the numpad; the extended flag would
    # make 0x4A/0x4E something else entirely.
    "NP5": (0x4C, False), "NPSUB": (0x4A, False), "NPADD": (0x4E, False),
    "NP9": (0x49, False), "NP8": (0x48, False), "NP2": (0x50, False),
    # The STEREO hotkeys, moved off the F-keys onto the numpad 2026-09-10.
    # These six were the only keys left that nothing binds: the game names no
    # numpad key anywhere (AliceControlLayout.ini has none at all, and the only
    # numpad rows in AliceInput.ini are the six camera axes we added ourselves).
    #   NP0 stereo on/off   NP1 eye mode (left/right/wiggle)
    #   NPDIV / NPMUL ipd -/+          NP3 / NPDEC convergence -/+
    # !! NPDIV IS EXTENDED and the other five are not. Numpad "/" is E0 35;
    # bare 0x35 is the main-row slash key. Getting it wrong is silent, exactly
    # like the numpad-vs-arrow trap above, only in the other direction.
    # !! NumLock must be ON for NP0/NP1/NP3/NPDEC to reach the proxy at all -
    # with it off those four deliver Insert/End/PageDown/Delete and the proxy
    # never sees them. NPDIV/NPMUL/NPADD/NPSUB are NumLock-independent. The
    # proxy reports NumLock state in its startup banner for exactly this reason.
    "NP0": (0x52, False), "NP1": (0x4F, False), "NP3": (0x51, False),
    "NPDEC": (0x53, False), "NPMUL": (0x37, False), "NPDIV": (0x35, True),
    "F1": (0x3B, False), "F2": (0x3C, False), "F3": (0x3D, False),
    "F4": (0x3E, False), "F5": (0x3F, False),
    "F6": (0x40, False), "F7": (0x41, False), "F8": (0x42, False),
    "F9": (0x43, False), "F10": (0x44, False), "F11": (0x57, False), "F12": (0x58, False),
}

KEYEVENTF_EXTENDEDKEY, KEYEVENTF_KEYUP, KEYEVENTF_SCANCODE = 0x0001, 0x0002, 0x0008
INPUT_KEYBOARD = 1

MOUSEEVENTF_MOVE = 0x0001
INPUT_MOUSE = 0

# SystemParametersInfo actions for pointer ballistics. Windows can multiply an
# injected relative delta by UP TO FOUR TIMES depending on these, so a `mouse`
# calibration measured on one machine is not portable to another unless they are
# pinned first. [reported 2026-09-07, Microsoft's own documentation]
SPI_GETMOUSE, SPI_SETMOUSE = 0x0003, 0x0004
SPI_GETMOUSESPEED, SPI_SETMOUSESPEED = 0x0070, 0x0071

# The key the game must have bound to `exec commands`.
#
# CORRECTED 2026-09-08. This said "F6..F12 ... are not used by Alice's default
# bindings" and picked F7. Both halves were wrong, and each failure is silent:
#
#   * Alice DOES bind F1-F9 by default, in AliceInput.ini -- F5 quicksave,
#     F6 quickload, F7/F8 toggle bUsePostProcessEffects, F9 shot. So F7 would have
#     toggled post-processing and never run `exec commands`.
#   * The d3d9 proxy polls VK_F6 THROUGH VK_F12 for its stereo hotkeys, so F7 ALSO
#     multiplies convergence by 0.8 on every press. A `bugit` would have silently
#     changed the stereo state it was sharing a session with.
#
# Between the two, EVERY F-key from F1 to F12 is claimed. The way out is to take
# one back deliberately: F1 (`viewmode wireframe`, harmless to lose) is rebound to
# `exec commands` in AliceInput.ini, and F1 is outside the proxy's F6..F12 range.
# If you change this key, check it against BOTH lists.
CONSOLE_EXEC_KEY = "F1"
EXEC_FILE = "commands"


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wt.WORD), ("wScan", wt.WORD), ("dwFlags", wt.DWORD),
                ("time", wt.DWORD), ("dwExtraInfo", ctypes.POINTER(wt.ULONG))]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wt.LONG), ("dy", wt.LONG), ("mouseData", wt.DWORD),
                ("dwFlags", wt.DWORD), ("time", wt.DWORD),
                ("dwExtraInfo", ctypes.POINTER(wt.ULONG))]


class _IU(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("pad", ctypes.c_byte * 32)]


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


PROCESS_NAME = "alicemadnessreturns.exe"
# Windows that matched the title but failed the process check on the last
# find_window() call, as (hwnd, title, owning-process) - see need_window().
LAST_REJECTED = []


def window_process_name(hwnd):
    """The lower-cased exe name that owns `hwnd`, or None.

    QueryFullProcessImageNameW rather than GetModuleFileNameEx: it needs only
    PROCESS_QUERY_LIMITED_INFORMATION, which a normal user holds for a normal
    process, where the module-based calls need PROCESS_VM_READ and fail."""
    k = ctypes.windll.kernel32
    pid = wt.DWORD(0)
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return None
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    h = k.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not h:
        return None
    try:
        size = wt.DWORD(32768)
        buf = ctypes.create_unicode_buffer(size.value)
        if not k.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
            return None
        return buf.value.rsplit("\\", 1)[-1].lower()
    finally:
        k.CloseHandle(h)


def find_window(require_process=True):
    """Find the game's window by TITLE **and** by the process that owns it.

    ⚠️ WHY THE PROCESS CHECK EXISTS, and it is not hypothetical: THIS harness is
    the one it happened to. On 2026-09-09 it returned the user's CHROME TAB,
    because they had googled Alice's first-person mode and the tab title
    contained "ALICE" while this function matched TITLE_SUBSTR as a substring of
    any visible window. The next calls in every session are focus() then press(),
    so menu keys would have gone into their browser - and the game would simply
    have read as "ignoring the keyboard", the same silent signature this file
    already warns about for other causes. It was caught only because the client
    rect came back at -32000, i.e. a minimised window.

    A title is USER DATA. A browser tab, an editor, a chat window, this session's
    own terminal can each contain a game's name, so a title match can only ever
    NARROW the search. The owning process is what VERIFIES it: a window whose
    process image is AliceMadnessReturns.exe is the game's, whatever its title.

    Ported from doom-2016-vr/dev-archive/tools/doomdrive.py via a /pd tandem
    inbox drop, 2026-09-09. Keep both checks; neither alone is enough.

    `require_process=False` exists only so the decoy self-test can demonstrate
    the old title-only behaviour. It is NOT a way to make a failing match pass.
    """
    found = []
    rejected = []

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
                proc = window_process_name(hwnd)
                if not require_process or proc == PROCESS_NAME:
                    found.append((hwnd, t))
                else:
                    rejected.append((hwnd, t, proc))
        return True

    user32.EnumWindows(cb, 0)
    # Record what was refused so need_window() can NAME it. A silent empty list
    # reads identically to "the game is not running", and the whole point is that
    # an impostor window is LOUD rather than invisible.
    global LAST_REJECTED
    LAST_REJECTED = rejected
    return found


def need_window():
    w = find_window()
    if not w:
        if LAST_REJECTED:
            lines = chr(10).join("    %r  owned by %s" % (t, pr or "<unknown>")
                                 for _, t, pr in LAST_REJECTED)
            msg = ("NO WINDOW: %d window(s) matched %r but are NOT owned by %s, "
                   "so they were refused:" % (len(LAST_REJECTED), TITLE_SUBSTR,
                                              PROCESS_NAME))
            sys.exit(msg + chr(10) + lines)
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


# ---------------------------------------------------------------------------
# ROUTE 1 - the console `exec` channel.
#
# UE3's console command `exec <file>` runs each line of an EXTENSIONLESS file as
# a console command. Bind one key to `exec commands`, rewrite the file from here
# between presses, and that single key becomes a complete Python->game channel.
#
# !! WHERE THE FILE GOES IS NOT SETTLED. The /gr drop said
# `Alice Madness Returns\Binaries`, but the exe actually lives in
# `Binaries\Win32`, which is its working directory, and UE3 builds have also been
# documented reading exec files from `<Game>\Config`. Rather than guess and get a
# silent no-op, this writes the SAME file to every candidate and says which ones
# it managed - so one launch tests all of them at once and the log says which
# path was live. Writing a few hundred bytes into four directories is cheap; a
# failed test that cannot distinguish "wrong path" from "no cheat manager" is
# not. [inferred-static 2026-09-08 - none of these has been confirmed live]
# ---------------------------------------------------------------------------

def _game_root():
    """The install root, from this file's own recorded location or an override."""
    env = os.environ.get("ALICE_ROOT")
    if env:
        return env
    for c in (r"D:\Program Files (x86)\Steam\steamapps\common\Alice Madness Returns",
              r"C:\Program Files (x86)\Steam\steamapps\common\Alice Madness Returns",
              r"D:\SteamLibrary\steamapps\common\Alice Madness Returns"):
        if os.path.isdir(c):
            return c
    return None


def _exec_targets(root):
    docs = os.path.join(os.path.expanduser("~"), "Documents", "My Games",
                        "Alice Madness Returns", "AliceGame", "Config")
    return [
        os.path.join(root, "Binaries", "Win32"),   # the exe's own directory (its CWD)
        os.path.join(root, "Binaries"),            # what the /gr drop named
        os.path.join(root, "AliceGame", "Config"),
        docs,
    ]


def write_exec(cmds):
    """Write the exec file to every candidate directory. Returns the list written."""
    root = _game_root()
    if not root:
        sys.exit("NO INSTALL: set ALICE_ROOT to the game folder")
    text = "\n".join(cmds) + "\n"
    written = []
    for d in _exec_targets(root):
        if not os.path.isdir(d):
            continue
        try:
            with open(os.path.join(d, EXEC_FILE), "w", encoding="ascii", newline="\n") as f:
                f.write(text)
            written.append(d)
        except OSError as e:
            print("  could not write %s: %s" % (d, e))
    if not written:
        sys.exit("NO TARGET: none of the candidate directories was writable")
    return written


def console(cmds):
    """Route 1: write the exec file, then press the key bound to `exec commands`."""
    written = write_exec(cmds)
    print("exec file (%d line(s)) written to %d location(s):" % (len(cmds), len(written)))
    for d in written:
        print("   ", d)
    print("pressing %s (must be bound to `exec %s`)" % (CONSOLE_EXEC_KEY, EXEC_FILE))
    press(CONSOLE_EXEC_KEY)
    print("PRE-FLIGHT, if nothing happens - all three are silent failures:")
    print("  1. launch flags -freeconsole -allowcheats")
    print("  2. %s bound to `exec %s` in AliceInput.ini" % (CONSOLE_EXEC_KEY, EXEC_FILE))
    print("  3. the console output is in the game window, not here - screenshot it")


# ---------------------------------------------------------------------------
# ROUTE 4 - relative mouse injection.
#
# Last of the four on purpose. Two documented hazards, both of which make a
# failure look like a fact about the game:
#
#   * POINTER BALLISTICS. Windows may multiply an injected relative delta by up
#     to 4x depending on pointer speed and two threshold values, so a calibration
#     is not portable between machines. `ballistics` reports them and can pin
#     them. [reported 2026-09-07]
#   * UIPI. If the game runs at a higher integrity level than this harness,
#     SendInput fails SILENTLY - neither the return value nor GetLastError says
#     so. The only symptom is nothing happening. [reported]
#
# !! Alice's mouse path looks like the Win32 cursor/window-message path rather
# than Raw Input [inferred-static 2026-09-07] - MadnessPatch hooks UpdateMouseLock
# (which calls ClipCursor) and ProcessDeferredMessage. A Raw-Input reader has no
# reason to clip the cursor. If that holds, injected moves should be seen; it is
# an inference from someone else's patch, not a measurement of ours.
# ---------------------------------------------------------------------------

def ballistics(pin=False):
    """Report the pointer acceleration settings, and optionally pin them off."""
    arr = (ctypes.c_int * 3)()
    if not user32.SystemParametersInfoW(SPI_GETMOUSE, 0, ctypes.byref(arr), 0):
        print("SPI_GETMOUSE failed: %d" % ctypes.get_last_error())
        return
    speed = ctypes.c_int(0)
    user32.SystemParametersInfoW(SPI_GETMOUSESPEED, 0, ctypes.byref(speed), 0)
    print("pointer thresholds = (%d, %d)  acceleration = %d  speed = %d/20"
          % (arr[0], arr[1], arr[2], speed.value))
    if arr[2] == 0:
        print("  acceleration is OFF - an injected delta is applied 1:1 and IS portable")
    else:
        print("  !! acceleration is ON - an injected delta may be scaled up to 4x, and any")
        print("     step size calibrated here will NOT reproduce on another machine.")
    if not pin:
        print("  (run `ballistics pin` to turn acceleration off for this session)")
        return
    off = (ctypes.c_int * 3)(0, 0, 0)
    if user32.SystemParametersInfoW(SPI_SETMOUSE, 0, ctypes.byref(off), 0):
        print("  pinned: acceleration off. !! THIS IS A SYSTEM-WIDE USER SETTING and this")
        print("     harness does not restore it - `ballistics` again to confirm, and set it")
        print("     back in Mouse Properties if you want it on.")
    else:
        print("  could not pin: %d" % ctypes.get_last_error())


MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP   = 0x0002, 0x0004
MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP = 0x0008, 0x0010


def click(button="left", count=1, hold=0.08, gap=0.15):
    """Press a mouse BUTTON, the way press() does keys.

    Added 2026-09-09. The harness was keyboard-only, which mattered because
    Alice's attack is LeftMouseButton and the whole "does first person survive
    combat?" question is unanswerable without it. Same hold/gap discipline as
    press(): the game samples input per frame, so a click has to be held long
    enough for one frame to see it down.
    """
    down, up = ((MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP) if button == "left"
                else (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP))
    hwnd, _ = need_window()
    focus(hwnd)
    for _ in range(count):
        for flag in (down, up):
            inp = INPUT(type=INPUT_MOUSE)
            inp.u.mi = MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=flag,
                                  time=0, dwExtraInfo=None)
            user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
            time.sleep(hold if flag in (down,) else gap)


def _send_mouse(dx, dy):
    inp = INPUT(type=INPUT_MOUSE,
                u=_IU(mi=MOUSEINPUT(int(dx), int(dy), 0, MOUSEEVENTF_MOVE, 0, None)))
    if user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT)) != 1:
        raise OSError("SendInput(mouse) failed: %d" % ctypes.get_last_error())


def mouse(dx, dy, steps=1, gap=0.016):
    """Route 4: relative mouse movement, split into `steps` deltas."""
    hwnd, _ = need_window()
    if not focus(hwnd):
        print("WARN: could not foreground the window; input may go elsewhere")
    arr = (ctypes.c_int * 3)()
    user32.SystemParametersInfoW(SPI_GETMOUSE, 0, ctypes.byref(arr), 0)
    if arr[2]:
        print("!! pointer acceleration is ON - this delta may be scaled. `ballistics pin` first.")
    per_x = dx // steps if steps else dx
    per_y = dy // steps if steps else dy
    for _ in range(steps):
        _send_mouse(per_x, per_y)
        time.sleep(gap)
    # Whatever is left after integer division, so the total is exactly (dx, dy).
    rx, ry = dx - per_x * steps, dy - per_y * steps
    if rx or ry:
        _send_mouse(rx, ry)
    print("sent %d step(s) totalling (%d, %d)" % (steps, dx, dy))
    print("!! SendInput reporting success does NOT mean the game saw it - UIPI failures are")
    print("   silent. Confirm with `bugit` (a number) rather than by eye (a judgement).")


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

    elif cmd == "console":
        if len(sys.argv) < 3:
            sys.exit("usage: console <command> [more words of the same command]")
        console([" ".join(sys.argv[2:])])

    elif cmd == "bugit":
        console(["BugIt"])

    elif cmd == "bugitgo":
        if len(sys.argv) != 8:
            sys.exit("usage: bugitgo X Y Z Pitch Yaw Roll  (six numbers, UE3 rotator units)")
        console(["BugItGo " + " ".join(sys.argv[2:8])])

    elif cmd == "ballistics":
        ballistics(pin=(len(sys.argv) > 2 and sys.argv[2] == "pin"))

    elif cmd == "click":
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        click(sys.argv[2] if len(sys.argv) > 2 else "left", n)
        print("clicked %s x%d" % (sys.argv[2] if len(sys.argv) > 2 else "left", n))

    elif cmd == "mouse":
        if len(sys.argv) < 4:
            sys.exit("usage: mouse DX DY [steps]")
        st = int(sys.argv[4]) if len(sys.argv) > 4 else 1
        mouse(int(sys.argv[2]), int(sys.argv[3]), max(1, st))

    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
