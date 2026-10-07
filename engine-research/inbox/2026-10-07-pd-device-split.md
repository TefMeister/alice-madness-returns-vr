# 2026-10-07: device.cpp split move-only (proved byte-identical), then the ScreenToWorld shear fold

*Static reader helper for a live `/lm` session. The game was never launched or touched. Follows
`2026-10-07-pd-shear-fold.md`.*

## 1. The split `[compile-verified 2026-10-07]`

In the staging repo, on **branch `alice-device-split-2026-10-07`**. ⚠️ **NOT merged to main.** Tag
**`pre-split-2026-10-07-alice`** marks main before the split (commit `ac72138`). The `-alice` suffix follows the
2026-09-29 tag, because the staging repo is shared by every game.

- `device.cpp` went from **1,473 to 1,036 lines**. Two whole blocks of `WrappedDevice` members moved unchanged into
  include files, included at the same place inside the class:
  - `device_otherview.inc.h` (264 lines): the other-view observers, the write-time shadow rewrite, partial VP
    assembly, and the pixel-copy diagnostic and capture.
  - `device_hotkeys.inc.h` (184 lines): `pressed()` and `pollHotkeys()`.
- **Proof that nothing changed:** the rebuilt `d3d9.dll` is **byte-identical** to the pre-split build (SHA-256
  `ff91356a6beb…`, same full hash; `cmp` finds no difference). `device.o` is byte-identical too. That covers exports,
  imports and every function's code bytes at once. Every host suite still passes. The code has no `__LINE__` or
  `__FILE__`, so moving lines could not change the binary. Commit `4e66ad2`.

## 2. The ScreenToWorld shear fold, a correction to the earlier drop

`2026-10-07-pd-shear-fold.md` said **20** ScreenToWorld shaders are not stereo-aware and would need the fold. The
disassembly says the right number is **all 28**. `[measured 2026-10-07]`: in all 8 ScreenToWorld shaders that declare
`NvStereoEnabled`, the un-sheared vector feeds only `ScreenToShadowMatrix`. The ScreenToWorld input is rebuilt
afterwards from the raw sheared `v0` (`rcp v0.w; mul v0.xy; mul W`). The 5 `ScreenToWorldMatrix` shaders (depth of
field) never un-shear at all. So the ScreenToWorld fold has **no stereo-aware gate**. The shadow fold keeps its gate,
which is right for ScreenToShadow.

Built on the branch (commit `1360b44`) `[compile-verified 2026-10-07]`:

- **Own switch `g_s2wFoldOn`**: 0 by default, poke-able, re-read every draw. **Marker file**
  `alice_vr_s2w_shearfold_on.txt`. It uses the same captured matrices as the shadow fold. The target is the game's
  own matrix when `g_s2wOn` is also on, otherwise the pre-shear one. It does nothing while stereo is off.
- **Log:** the `otherview` line now ends `s2wfold ON/off sent=`.
- **Test** `[verified-numerically 2026-10-07, n=8]` (both eyes × head 0 and 200 × head fix on and off):

| case | world error |
| --- | --- |
| unfolded | 16.45 units |
| folded | 0.0092 units |
| fold alone, head 200 | off by 200 ± 0.0012 (switches are independent) |

  `shadow_space_test.c`: 75 checks, 0 failed. All other suites pass.
- **DLL** `build-2026-10-07e-s2wfold/d3d9.dll` (local only, git-ignored), **SHA-256 prefix `080ed4a06f9f`**. Exports
  and imports are identical to `ff91356a6beb`. `device.cpp` is 1,037 lines.

**RVAs for `poke.py` in this build** (they moved again):

| switch | RVA |
| --- | --- |
| `g_shadowOn` | 0x4cb9a0 |
| `g_shadowSpace` | 0x4b008 |
| `g_s2wOn` | 0x4cb9a4 |
| `g_foldOn` | 0x4cb9b0 |
| `g_s2wFoldOn` | 0x4cb9c4 |

## NOT verified

- Nothing ran in the game. No build after `5d3ce56be320` has run.
- The depth-of-field shaders take their screen position from a texture coordinate (`v1`), not `v0`. I treated it as
  sheared like every other pixel position of that eye's image; that reading is `[inferred-static]`.
- The motion-blur shader's `PrevViewProjMatrix` is still uncorrected.
