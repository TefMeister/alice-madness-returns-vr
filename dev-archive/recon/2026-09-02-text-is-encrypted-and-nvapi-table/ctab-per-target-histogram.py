import sys, struct, re, collections
sys.path.insert(0, "D:/claude video game stuff/github-backups-pd/flat-to-vr-RE-toolkit/tools")
import importlib.util
spec = importlib.util.spec_from_file_location("ctab", "D:/claude video game stuff/github-backups-pd/flat-to-vr-RE-toolkit/tools/d3d9-ctab.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
data = open(sys.argv[1], 'rb').read()
INTEREST = re.compile(r'viewproj|camerapos|preview|nvstereo|localtoworld|localtoview|screenposition|minz|projection|invview|worldtoview|translatedworld', re.I)
per = collections.defaultdict(lambda: collections.Counter())   # (name,target,regset) -> Counter(reg,count)
tgt_tot = collections.Counter()
ntab = 0
for mo in re.finditer(b'CTAB', data):
    r = m.parse_ctab(data, mo.start())
    if not r: continue
    rows, tgt = (r if isinstance(r, tuple) else (r, "?"))
    ntab += 1; tgt_tot[tgt] += 1
    for name, regset, regidx, regcount in rows:
        if INTEREST.search(name):
            per[(name, tgt, regset)][(regidx, regcount)] += 1
print("tables parsed:", ntab, dict(tgt_tot))
print()
print("%-32s %-8s %-8s %8s   register histogram" % ("constant","target","regset","shaders"))
rowsout=[]
for (name, tgt, regset), c in sorted(per.items(), key=lambda kv: (-sum(kv[1].values()), kv[0])):
    tot = sum(c.values())
    hist = ", ".join("%s%d x%d (%d)" % ('s' if regset==3 else 'c', ri, rc, n) for (ri, rc), n in c.most_common(6))
    print("%-32s %-8s %-8s %8d   %s" % (name, tgt, m.REGSET.get(regset,'?'), tot, hist))
    rowsout.append((name,tgt,m.REGSET.get(regset,'?'),tot,hist))
open(sys.argv[2],"w").write("constant\ttarget\tregset\tshaders\thistogram\n"+"\n".join("\t".join(map(str,r)) for r in rowsout)+"\n")
