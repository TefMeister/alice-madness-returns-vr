# 2026-10-07: the per-eye shear fold for the 40 shadow shaders that do not un-shear, built OFF

*Static reader helper for a live `/lm` session. The game was never launched or touched. Follows
`2026-10-07-pd-screentoworld.md`, which measured the error this removes.*

## What it fixes

40 of the 56 `ScreenToShadowMatrix` shaders do not declare `NvStereoEnabled`, so they never undo the two-eye shear
our vertex matrix carries (`x' = x + S·(w − C)`). Their rebuilt world point is off sideways by dx·|W/C − 1|, so in
the headset their shadows should appear to lie at the convergence depth (about 3.2 m), not on the surface
(`[verified-numerically 2026-10-07]` for the error; `[inferred-static]` for how it looks).

## The maths `[verified-numerically 2026-10-07, n=2]`

The shear changes only column 0 of the matrix (col0 += S·col3, row3.x −= S·C), so the shader-input map U() of the
matrix actually sent to the vertex stage is exact for these shaders. That form is equivalent to `U_e' = U_e·Sh_u`:

```
K = inv(U(sent)) · U(target)
target = the game's own matrix   when the head-offset fix (g_shadowOn) is also on: one K fixes both
target = the head-edited, pre-shear matrix   when it is off: the fold fixes the shear only
```

Host test (`shadow_space_test.c`, both eyes, head offset 0 and 200, 64 mm at 95 units/m, C = 300):

| case | worst world error |
| --- | --- |
| not-aware shader, no fold | 16.45 units (216 with the head offset) |
| not-aware shader, fold on | 0.009 units |
| aware shader, its unchanged path | 0.009 units |
| aware shader IF the fold were applied | 16.45 units (why the 16 are left alone) |

`alice_shadow_fold_k()` returns 0 and sends nothing for a stereo-aware shader. The test checks that too. With the
head fix off, the fold alone leaves exactly the head error (about the offset), so the two switches really are
separate. 71 checks, 0 failed; every other suite still passes.

## Built `[compile-verified 2026-10-07]`, on top of 5d3ce56be320

In staging, `alice-madness-returns-vr/proxy-d3d9`:

- **Capture.** Wherever the proxy shears a camera-shaped view-projection, it now keeps three matrices: the game's
  own, the pre-shear one and the one actually sent (`alice_fold_note`).
- **Draw.** `shadowAtDraw()` now runs when either `g_shadowOn` or `g_foldOn` is set. For a non-aware shader with the
  fold on and stereo enabled it sends the fold K. Otherwise it behaves exactly as before.
- **Switch.** **`g_foldOn`**, 0 by default, poke-able and re-read every draw. Marker file
  **`alice_vr_shearfold_on.txt`**. The fold is ignored while stereo is off.
- **Log.** The `otherview` line now ends `shearfold ON/off sent= aware-skipped= refused=`. A rising `aware-skipped`
  is the live proof that the 16 are being left alone.
- **DLL.** `build-2026-10-07c-shearfold/d3d9.dll` (local only, git-ignored), **SHA-256 prefix `ff91356a6beb`**.
  RVAs for `poke.py` in THIS build (they moved again):

| switch | RVA |
| --- | --- |
| `g_shadowOn` | 0x4cb998 |
| `g_shadowSpace` | 0x4b008 |
| `g_s2wOn` | 0x4cb99c |
| `g_foldOn` | 0x4cb9a8 |

- `device.cpp` is 1,473 lines, under the 1,500 hard limit but close. The next addition there should come with a
  move-only split.

## NOT verified

- Nothing ran in the game. A live check needs stereo on, a crisp shadow, and the headset or a two-eye capture,
  with `g_foldOn` 0 vs 1.
- That the last captured camera matrix is the one the shadow pass was drawn with (the same caveat as the head fix).
- **Not folded:** the 20 `ScreenToWorld` light-falloff shaders that are also not stereo-aware have the same per-eye
  error in their falloff. The same fold would apply to them; it is not built `[hypothesis]`.
