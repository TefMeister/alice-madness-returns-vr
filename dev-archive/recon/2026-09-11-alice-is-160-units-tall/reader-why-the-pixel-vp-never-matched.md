# Why the pixel VP copy never matched — the likeliest cause, a fix for it, and a diagnostic that settles it

From: `/lm` reader helper (dev PC), 2026-09-11. Static only, plus a read of the live proxy log.
No launch, nothing deployed, no git.

Answers the live result on build `380329e8` (Wonderland, stereo OFF, head up 50 / forward 50):
`vs c4 CameraPosition fix=8908 skip=11645` but `ps VP rewritten c4=0 c11=0 other=0 (of 10275 armed
scans)` `[verified-live 2026-09-11, n=1]`.

## What the evidence says

**1. The pixel copy is in the SAME space as vs c0 — "it's the absolute-world matrix" is unlikely**
`[inferred-static 2026-09-11]`. Over the shipped `RefShaderCache` (38,979 distinct pixel / 2,164
vertex shaders), the pixel shaders multiply their VP copy by interpolator `texcoord7` in 4,053 of
4,090 (`texcoord5` in 37). The 744 vertex shaders that write a world position into `texcoord7` build
it from `LocalToWorld` alone — the translated space vs c0 maps from. The 250 that also touch c5 are
the wind-sway shaders, which subtract c5 and add it straight back. So the bits should agree unless
the engine computes the copy separately.

**2. Most of the pixel copy's users are dynamic-light passes, not depth-fade.** 3,933 of the 4,090
also bind `LightColorAndFalloffExponent`, 3,580 `LightAttenuationTexture`: they use the copy to find
the screen position for the light-attenuation (shadow) lookup `[measured 2026-09-11]`. With the head
moved and the copy not, **shadows and light masks would slide against geometry** — probably the
most visible symptom of this defect `[hypothesis]`.

**3. The live log shows the 4-slot ring was FULL with the camera standing still** `[measured
2026-09-11, from alice_vr_proxy_log.txt 18:59-19:00]`: `armed=4` on every line while camtrace read
`dmax=0.00 spread=0.000` at one fixed yaw. So the vertex path is handed **at least four different
camera-shaped matrices every frame** with one heading — variants of one view, e.g. differing in the
depth column per depth group or depth bias `[inferred-static]`. With more variants than slots,
round-robin eviction can drop the one a pixel copy belongs to before it arrives. That alone could
produce zero matches.

## The fix, in build `84eca4ff`

- **Ring 4 → 16**, plus an `inserts=` counter (new originals stored). With a still camera it stops
  climbing once every variant is in; if it keeps climbing, the ring still thrashes and the log says so.
- **Tiered matching**, each tier still a guard no material constant can pass, each counted separately:
  - `EXACT` — all 16 floats bit-identical → the edited matrix (unchanged behaviour)
  - `ORIGIN` — registers 0..2 (rotation + projection, 12 floats) bit-identical, register 3 differs
    by a pure translation that also fits the depth lane → `T(t) · edited`, exact
  - `NEAR` — all 16 floats within 1e-4 relative → `edited + (W − orig)`: exact for the translation
    part, within the tolerance otherwise. A camera turned by 1° does NOT match.
- The coherent line now reads `… armed=N inserts=N … (of N armed scans; tier exact=N origin=N near=N)`.
- **CameraPosition skips are now split by reason**: `no-VS` / `unmapped` / `VS-has-no-CameraPosition`
  / `declared-elsewhere`. The first run's 385k skips are harmless if they are "VS has no
  CameraPosition" (that shader never reads c4). If they are "no VS" or "unmapped", CameraPosition is
  being uploaded before its shader is bound, and those draws keep the old value.

## The diagnostic (opt-in, independent of the coherent view)

`alice_vr_psdiag_on.txt` next to the exe → banner `pixel-copy diagnostic is ON`. Read-only.

- Every camtrace line: `psdiag frame=… ps writes=N | c4: touch a/b/c/d/e/f full=N VP-shader-bound=N
  camera-shaped=N | c11: …`. `touch` counts writes covering the register by count 1/2/3/4/5–8/9+:
  a matrix split into single-register writes would show under 1–3, which the matcher skips.
  `VP-shader-bound` = arrived while a pixel shader declaring ViewProjectionMatrix there was bound.
  `camera-shaped` = the window passes the vertex path's own camera classifier, a register-free "is
  this a view-projection at all" test.
- Up to 8 dumps: the pixel window's 16 floats beside the last camera VP at vs c0 (with how many
  frames old), then bit-equal lanes, max abs / rel difference, **per-register** difference and
  difference against the **transpose**, the closest of the stored originals, the tier the matcher
  gives it, and vs c5 PreViewTranslation.

**Reading the next run** `[inferred-static]`:

| what the log shows | meaning |
|---|---|
| `tier origin`/`near` climbing, `ps VP rewritten` > 0 | fixed; the tier says why exact failed |
| `inserts` climbing with a still camera | still more variants than 16 slots |
| `VP-shader-bound` = 0 and `camera-shaped` = 0 | the copy is not uploaded in this scene (no dynamically lit / depth-fade materials drawn) — retest where there are dynamic lights |
| dumps: only register c3 differs | another origin; the ORIGIN tier should have caught it — if not, send the dump |
| dumps: `transposed` ≈ 0 | uploaded transposed; a one-line tier to add |
| dumps: registers 0–2 differ by more than 1e-4 | a genuinely different matrix (other projection, previous frame); the dump shows which |

## Build `[compile-verified 2026-09-11]`

| | |
|---|---|
| file | `staging/alice-madness-returns-vr/proxy-d3d9/build-2026-09-11b-psdiag/d3d9.dll` |
| size | 738,304 B |
| SHA-256 | **`84eca4ff7a98cbd4322ee45961c76754596390fa43376c5b2c689a1c5d139ac5`** |
| reproducible | two builds in different folders byte-identical; no warnings; exports/imports unchanged |
| on top of | `380329e8` (scale 95 + coherent view); `build-2026-09-11-scale95/` still holds that deployed build, but the current source no longer reproduces it |
| rebuild | `OUT=build-2026-09-11b-psdiag ./build.sh` |
| default behaviour | with neither marker file, identical D3D traffic to `380329e8` / `648a44e1` on a headset-less PC: the pixel hook's first test is the diag flag, then `ring empty` → forward `[inferred-static]` |

**Tests** `[verified-numerically 2026-09-11]`: `coherent_view_test` **89 checks, 0 failures**, up from 59.
New checks cover ORIGIN (a shifted-origin copy lands where the edited view puts the translated point,
to 2e-3, and a register 3 that is not a translation is refused), NEAR, the 1°-turned camera and
material junk refused at every tier, a NEAR copy found at offset 2 of a 10-register write, the
comparison helper (self, transpose, register-3-only change), and the live case: **six variants
cycled 10× → six entries, six inserts, all found**. **13 mutants, all caught** (7 new: depth-lane
check removed, sign of t, ORIGIN keeping the unedited rows, NEAR tolerance ×1000, NEAR off,
transpose index, per-register index). vr_pose 64/64, stereo, disparity 23/23 and the shadermap
corpus check all unchanged and green.

## Suggested next run

Deploy `84eca4ff`, keep `alice_vr_coherent_on.txt`, **add `alice_vr_psdiag_on.txt`**, same head
offset. Stand somewhere with visible shadows or dynamic lights. Read one `coherent` and one `psdiag`
line after ~30 s, plus the first dump.
