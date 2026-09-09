"""Turn rate against HOLD TIME, read off the UNWRAPPED cumulative heading.

The wrapped yaw could not answer this: one press turns ~90 deg, several presses
pass 180, and a before/after pair then reads as a small delta in the wrong
direction. `total` accumulates per frame, so a turn of any size reads directly.
`dmax` is printed alongside - it is the largest single-frame step, and the
accumulation is only trustworthy while it stays well under 180.
"""
import importlib.util, re, time

HARNESS = r"D:\claude video game stuff\github-backups\alice-madness-returns-vr\dev-archive\tools\alice_harness.py"
LOG = r"D:\Program Files (x86)\Steam\steamapps\common\Alice Madness Returns\Binaries\Win32\alice_vr_proxy_log.txt"

spec = importlib.util.spec_from_file_location("ah", HARNESS)
ah = importlib.util.module_from_spec(spec); spec.loader.exec_module(ah)

LINE = re.compile(r"camtrace .*total=([-+0-9.]+) dmax=([0-9.]+)")

def trace():
    with open(LOG, "r", encoding="utf-8", errors="replace") as f:
        for ln in reversed(f.readlines()):
            m = LINE.search(ln)
            if m:
                return float(m.group(1)), float(m.group(2))
    return None, None

hwnd, _ = ah.need_window(); ah.focus(hwnd)
print("%8s %6s %11s %11s %11s %8s" % ("hold_ms", "presses", "total_before", "total_after", "turn_deg", "dmax"))
plan = [(20,1),(40,1),(80,1),(160,1),(80,1),(80,2),(80,4)]
for hold_ms, n in plan:
    time.sleep(2.5)
    before, _ = trace()
    ah.press("NP6", n, hold=hold_ms/1000.0, gap=0.15)
    time.sleep(3.0)
    after, dmax = trace()
    if before is None or after is None:
        print("%8d %6d  NO TRACE" % (hold_ms, n)); continue
    print("%8d %6d %11.2f %11.2f %11.2f %8.2f"
          % (hold_ms, n, before, after, after-before, dmax))
