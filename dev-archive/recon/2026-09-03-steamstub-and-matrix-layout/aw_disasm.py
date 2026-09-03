"""Minimal D3D9 SM3 vertex-shader disassembler - just enough to see how the
camera matrix registers are actually consumed."""
import os, re, struct, sys

OPS = {0x00:"nop",0x01:"mov",0x02:"add",0x03:"sub",0x04:"mad",0x05:"mul",0x06:"rcp",
       0x07:"rsq",0x08:"dp3",0x09:"dp4",0x0A:"min",0x0B:"max",0x0C:"slt",0x0D:"sge",
       0x0E:"exp",0x0F:"log",0x10:"lit",0x11:"dst",0x12:"lrp",0x13:"frc",
       0x14:"m4x4",0x15:"m4x3",0x16:"m3x4",0x17:"m3x3",0x18:"m3x2",
       0x19:"call",0x1A:"callnz",0x1B:"loop",0x1C:"ret",0x1D:"endloop",0x1E:"label",
       0x1F:"dcl",0x20:"pow",0x21:"crs",0x22:"sgn",0x23:"abs",0x24:"nrm",0x25:"sincos",
       0x26:"rep",0x27:"endrep",0x28:"if",0x29:"ifc",0x2A:"else",0x2B:"endif",
       0x2C:"break",0x2D:"breakc",0x2E:"mova",0x2F:"defb",0x30:"defi",
       0x51:"def",0x5F:"texldl"}
RT = {0:"r",1:"v",2:"c",3:"a",4:"oPos",5:"oD",6:"o",7:"i",8:"oC",9:"oDepth",
      10:"s",11:"c",12:"c",13:"c",14:"b",15:"aL",16:"rh",17:"misc",18:"label",19:"p"}
SW = "xyzw"

def regtype(t): return ((t & 0x70000000) >> 28) | ((t & 0x00001800) >> 8)
def regnum(t):  return t & 0x7FF

def src_str(t):
    rt, n = regtype(t), regnum(t)
    sw = (t >> 16) & 0xFF
    c = [(sw >> (2*i)) & 3 for i in range(4)]
    s = "" if c == [0,1,2,3] else "." + "".join(SW[x] for x in c)
    if len(set(c)) == 1 and c != [0,1,2,3]: s = "." + SW[c[0]]
    mod = (t >> 24) & 0xF
    pre = "-" if mod == 1 else ""
    return "%s%s%d%s" % (pre, RT.get(rt,"?%d"%rt), n, s)

def dst_str(t):
    rt, n = regtype(t), regnum(t)
    wm = (t >> 16) & 0xF
    m = "" if wm == 0xF else "." + "".join(SW[i] for i in range(4) if wm & (1<<i))
    return "%s%d%s" % (RT.get(rt,"?%d"%rt), n, m)

def disasm(d, off, limit=400):
    """off points at the version token. Yields text lines."""
    ver = struct.unpack_from("<I", d, off)[0]
    out = ["  ; version 0x%08X" % ver]
    p = off + 4
    n = 0
    while p + 4 <= len(d) and n < limit:
        tok = struct.unpack_from("<I", d, p)[0]
        if tok == 0x0000FFFF: out.append("  end"); break
        op = tok & 0xFFFF
        if op == 0xFFFE:
            ln = (tok >> 16) & 0x7FFF
            p += 4 + ln*4
            continue
        ln = (tok >> 24) & 0x0F
        name = OPS.get(op, "op_%02X" % op)
        params = []
        for i in range(ln):
            q = p + 4 + i*4
            if q + 4 > len(d): break
            params.append(struct.unpack_from("<I", d, q)[0])
        if op == 0x1F and len(params) >= 2:      # dcl
            out.append("  dcl %s" % dst_str(params[1]))
        elif op == 0x51 and len(params) >= 5:    # def
            f = struct.unpack_from("<4f", d, p+8)
            out.append("  def %s, %g, %g, %g, %g" % (dst_str(params[0]), *f))
        elif params:
            out.append("  %-6s %s" % (name, ", ".join(
                [dst_str(params[0])] + [src_str(x) for x in params[1:]])))
        else:
            out.append("  %s" % name)
        p += 4 + ln*4
        n += 1
    return out

def cstr(d,a):
    e=d.find(b"\0",a); return d[a:e].decode("latin-1","replace") if e>=0 else ""

def ctab_at(d, ct):
    base = ct+4
    try: size,creator,ver,nconst,cinfo,flags,target = struct.unpack_from("<7I",d,base)
    except struct.error: return None
    if size!=0x1C or not (0<nconst<512): return None
    if base+cinfo+nconst*20 > len(d): return None
    tgt = cstr(d, base+target)
    if not re.match(r"^(vs|ps)_\d_\d$", tgt): return None
    rows=[]
    for i in range(nconst):
        o=base+cinfo+i*20
        no,rs,ri,rc,_r,ti,_dv = struct.unpack_from("<IHHHHII",d,o)
        rows.append((cstr(d,base+no),rs,ri,rc))
    return rows,tgt

fn = sys.argv[1] if len(sys.argv)>1 else "Terrain.obj"
root = r"D:/Program Files (x86)/Steam/steamapps/common/Alan Wake/shaders/build/pc"
d = open(os.path.join(root,fn),"rb").read()

shown = 0
for m in re.finditer(b"CTAB", d):
    r = ctab_at(d, m.start())
    if not r: continue
    rows,tgt = r
    if tgt != "vs_3_0": continue
    names = {x[0]:x for x in rows}
    if "g_mViewToClip" not in names or "g_mLocalToView" not in names: continue
    if "GPU_skinning_matrices" in names: continue
    # find the version token: search backwards for 0xFFFE0300 near this CTAB
    vt = d.rfind(b"\x00\x03\xfe\xff", max(0,m.start()-64), m.start())
    if vt < 0: continue
    print("=== %s : vs_3_0, %d constants ===" % (fn, len(rows)))
    for nm,rs,ri,rc in sorted(rows,key=lambda x:x[2]):
        if rs==2: print("   %-28s c%-4d x%d" % (nm,ri,rc))
    print()
    for line in disasm(d, vt, 60): print(line)
    shown += 1
    if shown >= 1: break
