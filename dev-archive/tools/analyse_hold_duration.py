import re, sys
p = r"D:\claude video game stuff\github-backups-pd\alice-madness-returns-vr\dev-archive\recon\2026-09-09-c0-census-camera-yaw-and-the-built-in-first-person-camera\log-run4-cumulative-yaw-and-fps.txt"
rows=[]
for line in open(p, encoding='latin-1'):
    m = re.search(r"\[(\d+):(\d+):(\d+)\.(\d+)\].*camtrace frame=(\d+) yaw=([-+0-9.]+) pitch=([-+0-9.]+) total=([-+0-9.]+) dmax=([0-9.]+)", line)
    if m:
        h,mi,s,ms = int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4))
        t = h*3600+mi*60+s+ms/1000.0
        rows.append((t, int(m.group(5)), float(m.group(6)), float(m.group(8)), float(m.group(9))))
print("camtrace samples:", len(rows))
# frame period between consecutive samples
per=[]
for i in range(1,len(rows)):
    dt = rows[i][0]-rows[i-1][0]; df = rows[i][1]-rows[i-1][1]
    if df>0 and 0 < dt < 30: per.append(dt/df*1000.0)
per.sort()
if per:
    print("frame period ms: min=%.1f median=%.1f p90=%.1f max=%.1f" % (per[0], per[len(per)//2], per[int(len(per)*0.9)], per[-1]))
    print("            fps: median=%.1f  slowest=%.1f" % (1000.0/per[len(per)//2], 1000.0/per[-1]))
# total changes between samples, where the camera actually moved
deltas=[abs(rows[i][3]-rows[i-1][3]) for i in range(1,len(rows))]
moved=[d for d in deltas if d>1.0]
moved.sort()
print("\nsamples where |total| moved >1 deg:", len(moved))
if moved:
    print("  moves:", ", ".join("%.1f"%d for d in moved[:24]))
# dmax when the camera moved
dm=[rows[i][4] for i in range(1,len(rows)) if abs(rows[i][3]-rows[i-1][3])>1.0]
dm.sort()
if dm: print("  dmax on those samples: min=%.1f median=%.1f max=%.1f" % (dm[0], dm[len(dm)//2], dm[-1]))
