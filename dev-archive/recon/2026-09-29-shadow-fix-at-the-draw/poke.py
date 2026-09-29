"""Read (and optionally write) an int32 inside our d3d9.dll in the running Alice process.
usage: poke.py RVA [RVA ...] [--set RVA=VALUE]"""
import ctypes, ctypes.wintypes as w, subprocess, sys

k32, psapi = ctypes.windll.kernel32, ctypes.windll.psapi
out = subprocess.check_output(["tasklist", "/FI", "IMAGENAME eq AliceMadnessReturns.exe", "/FO", "CSV", "/NH"], text=True)
pid = int(out.strip().split(",")[1].strip('"'))
k32.OpenProcess.restype = w.HANDLE
h = k32.OpenProcess(0x0010 | 0x0020 | 0x0008 | 0x0400, False, pid)  # VM_READ|VM_WRITE|VM_OPERATION|QUERY
mods = (w.HMODULE * 1024)()
need = w.DWORD()
psapi.EnumProcessModulesEx(h, mods, ctypes.sizeof(mods), ctypes.byref(need), 0x01)  # 32-bit list
base = None
for m in mods[: need.value // ctypes.sizeof(w.HMODULE)]:
    name = ctypes.create_unicode_buffer(260)
    psapi.GetModuleFileNameExW(h, m, name, 260)
    if name.value.lower().endswith("binaries\\win32\\d3d9.dll"):
        base = m
print("pid", pid, "d3d9 base", hex(base or 0))


def rd(rva):
    v = ctypes.c_int32()
    k32.ReadProcessMemory(h, ctypes.c_void_p(base + rva), ctypes.byref(v), 4, None)
    return v.value


for a in sys.argv[1:]:
    if a.startswith("--set"):
        continue
    if "=" in a:
        rva, val = a.split("=")
        v = ctypes.c_int32(int(val))
        ok = k32.WriteProcessMemory(h, ctypes.c_void_p(base + int(rva, 16)), ctypes.byref(v), 4, None)
        print("wrote", rva, "=", val, "ok" if ok else "FAILED", "now", rd(int(rva, 16)))
    else:
        print(a, "=", rd(int(a, 16)))
