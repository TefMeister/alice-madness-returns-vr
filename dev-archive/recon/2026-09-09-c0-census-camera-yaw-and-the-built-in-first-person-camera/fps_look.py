import importlib.util, re, sys, time
HARNESS = r"D:\claude video game stuff\github-backups\alice-madness-returns-vr\dev-archive\tools\alice_harness.py"
LOG = r"D:\Program Files (x86)\Steam\steamapps\common\Alice Madness Returns\Binaries\Win32\alice_vr_proxy_log.txt"
spec = importlib.util.spec_from_file_location("ah", HARNESS)
ah = importlib.util.module_from_spec(spec); spec.loader.exec_module(ah)
LINE = re.compile(r"camtrace .*yaw=([-+0-9.]+) pitch=([-+0-9.]+) total=([-+0-9.]+) dmax=([0-9.]+).*p00cam=([0-9.]+)")

def trace():
    for ln in reversed(open(LOG, encoding="utf-8", errors="replace").readlines()):
        m = LINE.search(ln)
        if m:
            return tuple(float(x) for x in m.groups())
    return None

outdir = sys.argv[1]
hwnd, _ = ah.need_window(); ah.focus(hwnd)
print("%-18s %9s %8s %10s %7s %9s" % ("after", "yaw", "pitch", "total", "dmax", "p00cam"))

def show(label):
    time.sleep(2.5)
    print("%-18s %9.3f %8.3f %10.2f %7.2f %9.6f" % ((label,) + trace()))

show("in FPS, idle")
ah.press("NP8", 3); show("NP8 x3 (look up)")
ah.grab(outdir + "/h1_up.png")
ah.press("NP2", 6); show("NP2 x6 (look down)")
ah.grab(outdir + "/h2_down.png")
ah.press("NP6", 1); show("NP6 x1 (turn)")
ah.grab(outdir + "/h3_turn.png")
