# M0 static recon — 2026-08-25

Pure file-based static analysis of `AliceMadnessReturns.exe` (`Binaries\Win32\`) — no process
was launched or attached to. Tools: `file`, `objdump`/`strings` (llvm-mingw, i686 target — 32-bit).

## PE header / sections
```
file format coff-i386
PE32 executable for MS Windows 5.00 (GUI), Intel i386, 9 sections

Idx Name          Size     VMA      Type
  0 .text         00c9f2fb 00401000 TEXT
  1 .textidx      0008ccba 010a1000 TEXT
  2 CONST         00000050 0112e000 TEXT
  3 .rdata        0026aabe 0112f000 DATA
  4 .data         0003e600 0139a000 DATA
  5 .shr          00000004 014fa000 DATA
  6 .rsrc         00006478 014fb000 DATA
  7 .reloc        0015ed68 01502000 DATA
  8 .bind         00030b18 01661000
```
`.textidx` is a known, benign Unreal Engine 3 toolchain section — not a red flag. No giant
opaque blob, no Denuvo/anti-tamper-shaped structure. 17.4 MB on disk.

## Import table (full DLL list)
```
NETAPI32.dll, DINPUT8.dll, XINPUT1_3.dll, d3d9.dll, X3DAudio1_7.dll, XAPOFX1_4.dll,
vorbisfile.dll, WSOCK32.dll, dbghelp.dll, COMCTL32.dll, WINMM.dll, KERNEL32.dll, USER32.dll,
GDI32.dll, COMDLG32.dll, ADVAPI32.dll, SHELL32.dll, ole32.dll, OLEAUT32.dll, WS2_32.dll,
MSVCR90.dll, binkw32.dll, PhysXExtensions.dll, ApexFramework_x86.dll, POWRPROF.dll,
IMM32.dll, faultrep.dll
```
Plus, from the `Binaries\Win32\` folder listing itself: `PhysXCore.dll`, `PhysXCooking.dll`,
`PhysXDevice.dll`, `NxCharacter.dll`, `APEX_Clothing_x86.dll`, `APEX_Clothing_Legacy_x86.dll`,
`APEX_Destructible_x86.dll`, `APEX_Destructible_Legacy_x86.dll`, `cudart.dll`,
`cudart32_30_9.dll`, `ogg.dll`, `vorbis.dll`, `vorbisenc.dll`.

## Renderer strings
```
Direct3DCreate9   <- present, matches the d3d9.dll import
```

## Engine / developer identification strings
```
unlimited.ky.SpicyHorse.Alice2...   <- likely a Steam stat/achievement key naming the developer
```
Standard `Binaries\Win32\` + `Core\` folder layout independently confirms Unreal Engine 3.

## DRM search — all negative
```
denuvo / securom / starforce / origin / link2ea / ubisoft connect / activation required / eaapp
  -> no DRM-related hits. The "Origin" string hits found ("uvOrigin.x", "originalRect",
     "textureUVOrigin", "SubConditionChance_Item_DoReturnOriginalPackage") are all unrelated
     UV/texture-coordinate or gameplay-condition terminology, not EA's Origin launcher.
```
Notable given this is an EA-published title (same publisher as Burnout Paradise, which needed
the EA App to launch at all) — this game evidently doesn't carry that requirement.

## What this means for the project

Same clean picture as Prince of Persia: D3D9 confirmed, no DRM found, standard UE3 structure.
Full synthesis in `ENGINE-DOSSIER.md`.

## Gap noted, not a finding
No `/game-research` external-research sweep has run for this project yet.
