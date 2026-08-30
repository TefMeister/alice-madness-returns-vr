# 2026-08-25 — First live test: a real bug, fixed fast, then a genuinely exciting find

## The bug

First deploy of the proxy DLL made the game fail outright — it showed as "running" on Steam
for about two seconds, then just stopped. No crash dialog, no log output at all from our
proxy, which was the key clue: our code never even got a chance to run.

The cause: `AliceMadnessReturns.exe` needs **two** functions from `d3d9.dll`, not just the one
(`Direct3DCreate9`) our proxy exported — it also statically needs `D3DPERF_SetOptions` (a real
D3D9 performance-marker function). When a DLL is missing an export another program's already
built expecting, Windows can't even finish loading that program — it never runs a single line
of code. That's exactly what "ran for 2 seconds then stopped" was: the OS trying and failing to
start the game.

Confirmed the theory with a clean test: removed our DLL entirely, game launched fine on its
own. Added the missing export, redeployed, tried again — worked immediately, five minutes of
real play with no issues.

## Why this matters for later

This project uses the exact same "direct d3d9.dll proxy" approach as Prince of Persia (2008),
but Prince of Persia's exe only needed one function from d3d9.dll. Alice needed two. Lesson
recorded for any future D3D9 proxy work: check exactly which functions an exe imports from a
DLL before assuming a single entry point covers it.

## The genuinely exciting part

Two research findings landed right as we fixed this, and together they might mean the hardest
part of this whole project — figuring out how the camera/projection math works — is either
already solved by the original developers, or at least has a real head start:

1. **This game may ship its own working stereoscopic-3D mode.** A community fix from 2012
   describes itself as only needing to fix the flat 2D user-interface overlay in 3D — meaning
   the actual 3D camera/world rendering was *already correct* before that fix touched it. If
   true, the developers' own code already contains a working per-eye camera override — we just
   need to find and understand it, not invent it from nothing.
2. **Unreal Engine 3's camera system is publicly documented**, unlike every other engine in
   this portfolio (which are all closed, proprietary, and undocumented). We now know roughly
   where to look: a function called `UpdateViewTarget` on the gameplay side, and a specific
   shader slot (constant register `c0`) on the rendering side, both from Epic's own public
   documentation. Still needs confirming against this actual game's code, but it's a real
   starting point instead of a blank page.

Neither is confirmed working on this specific installed build yet — that's the next thing to
check, live, before assuming either shortcut pays off.

Full technical detail: `alice-madness-returns-vr-engine-research`, `ENGINE-DOSSIER.md` §4/§6.
