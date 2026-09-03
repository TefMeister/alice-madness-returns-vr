import re, struct, collections, sys
path = r"D:/Program Files (x86)/Steam/steamapps/common/Alice Madness Returns/AliceGame/CookedPC/RefShaderCache-PC-D3D-SM3.upk"
CLS={0:"SCALAR",1:"VECTOR",2:"MATRIX_ROWS",3:"MATRIX_COLUMNS",4:"OBJECT",5:"STRUCT"}
WANT={"ViewProjectionMatrix","PreViewTranslation","CameraPosition","LocalToWorld",
      "WorldToView","ViewMatrix","ProjMatrix","NvStereoEnabled","NvStereoFixTexture",
      "CameraWorldPos","TranslatedWorldToClip"}
def cstr(d,a):
    e=d.find(b"\0",a); return d[a:e].decode("latin-1","replace") if e>=0 else ""
d=open(path,"rb").read()
out=collections.Counter(); allnames=collections.Counter()
for m in re.finditer(b"CTAB", d):
    base=m.start()+4
    try: size,creator,ver,nconst,cinfo,flags,target=struct.unpack_from("<7I",d,base)
    except struct.error: continue
    if size!=0x1C or not (0<nconst<512): continue
    if base+cinfo+nconst*20>len(d): continue
    tgt=cstr(d,base+target) if base+target<len(d) else "?"
    if not re.match(r"^(vs|ps)_\d_\d$",tgt): continue
    for i in range(nconst):
        o=base+cinfo+i*20
        no,rs,ri,rc,_r,ti,_dv=struct.unpack_from("<IHHHHII",d,o)
        if base+no>=len(d): continue
        nm=cstr(d,base+no); allnames[nm]+=1
        if nm not in WANT: continue
        if base+ti+12>len(d): continue
        cl,ty,rows,cols,el,sm=struct.unpack_from("<6H",d,base+ti)
        out[(nm,tgt,ri,rc,CLS.get(cl,cl),rows,cols,el)]+=1
print("%-26s %-7s %-6s %-16s %-5s %-5s %-4s %s"%("constant","stage","reg","class","rows","cols","elem","shaders"))
for k,n in sorted(out.items(), key=lambda kv:(kv[0][0],-kv[1])):
    nm,tgt,ri,rc,cl,rows,cols,el=k
    print("%-26s %-7s c%-5d %-16s %-5d %-5d %-4d %d"%(nm,tgt,ri,cl,rows,cols,el,n))
print()
print("top constant names overall:", ", ".join("%s(%d)"%(k,v) for k,v in allnames.most_common(12)))
