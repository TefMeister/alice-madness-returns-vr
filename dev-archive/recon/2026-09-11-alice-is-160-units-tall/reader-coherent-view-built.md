# The pixel-shader VP copy and CameraPosition now follow the head — built, tested, NOT deployed, opt-in

From: `/lm` reader helper (dev PC), 2026-09-11. Static only: no launch, nothing deployed, no git.
Answers the board's `[PD]` row "TRANSLATE THE PIXEL-SHADER VP COPY, AND SET `CameraPosition` TO +d".

## The build `[compile-verified 2026-09-11]`

| | |
|---|---|
| file | `staging/alice-madness-returns-vr/proxy-d3d9/build-coherent-2026-09-11/d3d9.dll` |
| size | **730,624 B** (installed build `648a44e15b47` is 727,040 B) |
| SHA-256 | **`f205dffa5f39a917cba373d0c26e508d9c91bd3cd00f10e47339ddaf0e8f7ec5`** |
| reproducible | two builds into different folders are byte-identical |
| baseline | the unmodified source was first rebuilt and came out byte-identical to the install (`648a44e15b47…`), so the diff is exactly this change |
| warnings | none (`-Wall -Wextra`); exports unchanged (`Direct3DCreate9`, `D3DPERF_SetOptions`); imports still ADVAPI32 / KERNEL32 / USER32 + CRT |
| rebuild | `OUT=build-coherent-2026-09-11 ./build.sh` (`OUT` is new; the default is still `build/`) |

## ⚠️ OPT-IN — the default build behaves exactly like `648a44e15b47`

It changes what depth-fade, soft particles, refraction, specular and fog compute whenever the head
is away from rest, and none of that has been seen on screen — so it waits to be asked for:

- `alice_vr_coherent_on.txt` next to `AliceMadnessReturns.exe` → **ON**
- `alice_vr_coherent_off.txt` → OFF (wins over `_on`)
- neither → OFF (`ALICE_COHERENT_DEFAULT 0`; promoting it later is that one macro)

Read once at device creation and printed in the startup banner (`coherent view … is ON|OFF [reason]`),
so the `[FLAT]` A/B is two launches with no rebuild. A marker file because the keypad is full and the
proxy has no ini. With it OFF, every D3D call the proxy makes is the same as before: the pixel hook's
first line forwards, and nothing else is reached `[inferred-static 2026-09-11]`.

## What it does

**Pixel VP copy.** `SetPixelShaderConstantF` is now intercepted. Common case: one load + one compare
(`ring empty` → forward). When armed, each 4-register window of a write is tested for **bit-identity**
with a ViewProjection the vertex path just edited; on a hit the caller's range is forwarded untouched
and those four registers are overwritten with the edited matrix. Register number is never consulted,
so it works at c4 (4,086 shaders) and c11 (4), and cannot touch `UniformPixelVector_0` & co.
The matrix handed over is the one **after the head offset AND rotation, before the stereo shear** —
the pixel shaders apply the per-eye shift themselves from `NvStereoFixTexture`, so shearing their copy
would double it (the existing "stages agree" test pins that). Rotation is included because the
tracker is live on the home PC; the row predates head rotation and asked only for translation.

**CameraPosition.** vs c4 is re-sent as *the game's value + d* (d = the eye offset in the matrix's own
axes, the same vector `apply_eye_offset` moves the eye by); `w` untouched; added, not overwritten, so
it stays right if the game ever moves its origin. Rotation does not change it (the eye does not
move). Guarded by the **bound vertex shader's own table**: only when it declares `CameraPosition` at
c4 — the blur pass's 8-register `SampleOffsets` covers c0..c7, for one. `c5` untouched, as the row says.

**Disarming.** The ring (4 cameras) is cleared when the head returns to rest (offset 0, rotation
identity), so a still camera cannot keep receiving the last non-zero edit. A matrix that was merely
refused (not camera-shaped) clears nothing.

## Tests `[verified-numerically 2026-09-11, n=59]`

New `src/coherent_view_test.c` links the shipped `coherent_view.c` + `stereo_ue3.c`: **59 checks, 0
failures.** It pins: an exact copy matches only when armed; one flipped mantissa bit, or −0.0 for +0.0,
does not; a camera matrix planted at offset 7 of a 12-register material block is found at 7 and
nowhere else; a 3-register write never matches; a still camera noted 40× is one entry and the newest
edit wins; eviction keeps the newest four; CameraPosition = value + d with an odd `w` preserved; and
**coherence** over three offsets (including 149 units down and 150 forward) with a 25° head turn —
the eye read back out of the edited pixel matrix equals the new CameraPosition to 2e-3, and the depth
the pixel shader rebuilds from its copy equals the vertex stage's clip.w, while the UNFIXED copy is
off (by exactly 150 = d·forward in the translation-only case).

**Mutation-checked:** six mutants of the shipped file (sign of d, first-word-only compare, no replace,
window off by one, `w` forced to 1, `have_d` never set) — every one fails the suite (1 to 12 failures).

`shadermap.c` now also records `CameraPosition`; over the shipped cache it finds it at **vs c4 in
1,989 shaders — the dossier's independent 2026-09-09 count — and nowhere else, no pixel shader**
`[measured 2026-09-11]`. Every pre-existing suite is unchanged and green (63 + 23 + shadermap).

## What is NOT established

- Whether the defect it fixes is visible at all — still `[hypothesis]`, as the row says.
- Whether the pixel copy arrives AFTER the vertex write within a draw (UE3's usual order is vertex
  params then pixel params) `[hypothesis]`. If it arrives before, that draw keeps the old matrix for
  one frame; the log will say.
- Whether CameraPosition is uploaded while a shader that declares it is bound. If it is uploaded
  earlier, the guard skips it and nothing changes.

## The `[FLAT]` check this leaves

Drop `alice_vr_coherent_on.txt` beside the exe, deploy this build, step the head offset well away
from zero (e.g. forward +150), and read the new `coherent frame=…` log line (every 30 frames, only
when ON): `ps VP rewritten c4=` should climb with `armed=1`; `vs c4 CameraPosition fix=` should climb
with `skip=` small. `fix=0` with `skip>0` would mean the bound-shader guard is too strict. Then, by
eye, in a scene with water, fog or soft particles: with it OFF those effects should slide against the
geometry as the offset changes; with it ON they should stay put.

## Files touched in `staging/alice-madness-returns-vr/proxy-d3d9/`

New: `src/coherent_view.{h,c}`, `src/coherent_view_test.c`, `build-coherent-2026-09-11/`.
Edited: `src/device.cpp` (pixel hook, CameraPosition rewrite, pair recording, marker-file switch,
banner and log line), `src/shadermap.{h,c}` (`camera_position` field), `src/shadermap_test.c`
(the 1,989 check), `build.sh` (`OUT` + the new object), `build-stereo-test.sh` (the new suite).
The old one-line `SetPixelShaderConstantF` forwarder is gone. `build/` was not touched (it still
holds the stale `4b973e9e` build, not the installed one).
