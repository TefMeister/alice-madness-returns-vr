# 2026-10-07: the shadow fix was built in the wrong space, re-derived from the shipped shaders

Supersedes: ENGINE-DOSSIER.md §6g ("Note the derivation never needed to know how the shader packs its screen input ... D is the same on both sides and cancels", also in staging `coherent_view.h`)

*Static reader helper for a live `/lm` session. The game was never launched or touched.*

## What the shadow pass really feeds the matrix `[measured 2026-10-07]`

All **56** `ps_3_0` shaders in `GlobalShaderCache-PC-D3D-SM3.bin` that declare `ScreenToShadowMatrix` were
disassembled (CTAB-located, same parser family as the 2026-09-03 recon). Every one, in two code shapes (20 and
36 shaders), does:

```
ndc = v0.xy / v0.w
W   = 1 / (sceneDepth * MinZ_MaxZRatio.z - MinZ_MaxZRatio.w)      (view depth, clamped at 65504)
s   = (ndc.x*W)*M[0] + (ndc.y*W)*M[1] + W*M[2] + M[3]             (mad chain: registers are ROWS)
shadow uv = s.xy / s.w ; compared depth = min(s.z, 0.999)
```

So the input vector is **u = (x·W, y·W, W, 1)**, not the clip vector (cx, cy, cz, cw), and the register layout is
the same row layout as the vertex `ViewProjectionMatrix` (no transpose problem). This matches the public UE lineage
the `/gr` topic of 2026-09-29 reported. The 16 stereo-aware ones (they declare `NvStereoEnabled`) also un-shear x
themselves from `NvStereoFixTexture` before the multiply.

## Why the 2026-09-29 build looked wrong `[verified-numerically 2026-10-07, n=2]`

The draw-time fix sent `K·M` with `K = inv(R_edited)·R_game`, a **clip-space** K. The 2026-09-13 derivation claimed
any repacking D of the input cancels; it does not: M = D⁻¹·inv(R)·W2S, so the right correction is D⁻¹·K·D, which
equals K only if D commutes with K. Fed the real input, the clip-space K treats W as clip-z and 1 as clip-w, so the
shadow lookup is divided by the wrong number at every pixel.

A host simulation of the shipped shader (two depth conventions, offset 200 plus a head turn) gives worst relative
lookup error: **fix off 3.4, old K 110 to 209, new K below 4e-6**. So the old fix made things much *worse* than no
fix, which fits "fix ON, ground goes mostly dark with a straight edge" (a straight edge is where the wrong divisor
crosses zero: a plane in the world, a line on the ground) `[hypothesis]` for the edge itself. "Fix OFF, bright
ground, no Alice shadow" fits a lookup displaced by about the offset (200 units, more than Alice's 160-unit height)
`[hypothesis]`.

## The correction, in the shader's own space `[verified-numerically 2026-10-07, n=2]`

The world → u map of a camera R is affine and needs no projection constants:

```
U(R) = [ column0(R), column1(R), column3(R), (0,0,0,1)ᵀ ]
K_u  = inv(U(R_edited)) · U(R_game)          M_correct = K_u · M_game
```

Check: (p·U_e)·K_u·M = p·U_g·M = p·WorldToShadow. The suite builds M the way UE3 does (with its own
`[1 0 0 0; 0 1 0 0; 0 0 P22 1; 0 0 P32 0]` fix-up in front of inv(ViewProj)) and confirms the two constructions agree,
so the new K is checked against an independent derivation, not against itself.

One assumption remains `[inferred-static]`: the depth W the shader decodes equals clip.w (UE3's perspective has
M[2][3] = 1 and MinZ_MaxZRatio is built from its depth terms). If W were s·clip.w, only the translation of K_u would
be off, by the factor s.

## Built `[compile-verified 2026-10-07]`

Staging, `alice-madness-returns-vr/proxy-d3d9`:

- `alice_shadow_correction_screenw()` + `alice_s2s_input_map()` in `coherent_view.c/.h`;
- new `src/shadow_space_test.c` (34 checks, 0 failed; the OLD K is pinned to FAIL there, plus swapped-matrix and
  wrong-side traps), run from `build-stereo-test.sh`; the existing suites still pass (169, 64 and the rest);
- the proxy picks the space at runtime: **`g_shadowSpace`** (int, **1 = new input-space K, the default**; 0 = the
  old clip-space K for A/B). Marker `alice_vr_shadowfix_clipspace.txt` starts it at 0. It is re-read every frame,
  so `poke.py` can flip it live like `g_shadowOn`. The `otherview` log line now prints `space=`.
- DLL built to `build-2026-10-07-shadowspace/d3d9.dll` (not committed, binaries are git-ignored):
  **SHA-256 prefix `91faf14b965c`**. RVAs for `poke.py`: `g_shadowOn` **0x4cb988**, `g_shadowSpace` **0x4b008**
  (llvm-nm, image base 0x10000000). `device.cpp` is 1,463 lines, still under the hard limit.

## NOT verified

- Nothing ran in the game. Whether the shadows now match offset 0 needs the same crisp-shadow spot, offset 200,
  fix ON, `space` 1 vs 0 vs fix OFF.
- The W = clip.w assumption above.
- That `g_lastVpOrig/Edited` (the last head-edited VP of the frame, and only recorded while the coherent view is on)
  is the camera the shadow pass's depth and screen positions were drawn with.
- Per-eye stereo shear: 40 of the 56 shaders are NOT stereo-aware, so with the two-eye shear active their screen x
  is sheared and nothing un-shears it. That would leave a per-eye shadow error even at head offset 0; not part of
  this fix `[inferred-static]`.
- **`ScreenToWorld` is declared by 28 of the same 56 shaders** (the light-falloff ones) and is built from the
  same unedited view; it probably needs the same K_u. Not checked how its input is built `[hypothesis]`.
