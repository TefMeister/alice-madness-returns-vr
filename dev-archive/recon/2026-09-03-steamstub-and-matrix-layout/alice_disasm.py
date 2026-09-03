import os,re,struct,sys
src=open("aw_disasm.py").read().split('fn = sys.argv')[0]
g={}; exec(src,g)
ctab_at=g["ctab_at"]; disasm=g["disasm"]
path=r"D:/Program Files (x86)/Steam/steamapps/common/Alice Madness Returns/AliceGame/CookedPC/RefShaderCache-PC-D3D-SM3.upk"
d=open(path,"rb").read()
want=sys.argv[1] if len(sys.argv)>1 else "ViewProjectionMatrix"
stage=sys.argv[2] if len(sys.argv)>2 else "vs_3_0"
VT=b"\x00\x03\xfe\xff" if stage=="vs_3_0" else b"\x00\x03\xff\xff"
best=None
for mm in re.finditer(b"CTAB",d):
    r=ctab_at(d,mm.start())
    if not r: continue
    rows,tgt=r
    if tgt!=stage: continue
    if want not in {x[0] for x in rows}: continue
    vt=d.rfind(VT,max(0,mm.start()-32),mm.start())
    if vt<0: continue
    if best is None or len(rows)<best[0]: best=(len(rows),rows,vt)
if not best: print("none found"); sys.exit()
_,rows,vt=best
print("=== simplest %s carrying %s : %d constants ==="%(stage,want,len(rows)))
for nm,rs,ri,rc in sorted(rows,key=lambda x:x[2]):
    print("   %-28s %-8s c%-4d x%d%s"%(nm,"sampler" if rs==3 else "float4",ri,rc," <<<" if nm==want else ""))
print()
for line in disasm(d,vt,60): print(line)
