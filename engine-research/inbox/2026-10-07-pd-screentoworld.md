# 2026-10-07: ScreenToWorld needs the same correction, built OFF; how big the per-eye shadow error is

*Static reader helper for a live `/lm` session. The game was never launched or touched. Follows
`2026-10-07-pd-shadow-fix-rederived.md`.*

## 1. ScreenToWorld gets the same input `[measured 2026-10-07]`

All **33** ps_3_0 shaders in `GlobalShaderCache-PC-D3D-SM3.bin` that declare `ScreenToWorld` (28) or
`ScreenToWorldMatrix` (5) were disassembled.

- Every one multiplies the matrix in the same row (mad-chain) layout. The input is **u = (x·W, y·W, W, 1)**, the same
  packing as `ScreenToShadowMatrix`, and the shader keeps **xyz as a world position** (w is never used). The third
  row is multiplied by the depth W decoded from `MinZ_MaxZRatio` in all 33: 23 confirmed by an automatic check, 8 by
  hand (their 65504 clamp sits in a `.w` lane the check missed), and 2 from the same code shape in a longer listing.
- The 28 `ScreenToWorld` shaders are the light-falloff ones (they also declare `LightPosition`, `FalloffParameters`,
  `SpotDirection`) and all sit beside `ScreenToShadowMatrix`. They compute the distance from the pixel's world point to
  the light. The 5 `ScreenToWorldMatrix` shaders are depth of field / motion blur (`DofSphereInfo`; one also has
  `PrevViewProjMatrix`). They rebuild ndc from the texture coordinate through `ScreenPositionScaleBias` first, then
  apply the same packing.

So the correction is the same **K_u = inv(U(R_edited))·U(R_game)**, applied as `K_u·M`
`[verified-numerically 2026-10-07, n=2]`. In the host test at head offset 200, the rebuilt world point is wrong by
**200.0 units** with the fix off, **0.0087 units or less** with it on, and the old clip-space K does not fix it either.
The test covers a translated-world matrix and both depth conventions.

What it would look like unfixed `[hypothesis]`: light falloff and spot-cone edges computed for a point 200 units
away from the real one, so lit areas slide with the head offset, and the depth-of-field focus sphere slides too.

## 2. Built, OFF by default `[compile-verified 2026-10-07]`

In staging `alice-madness-returns-vr/proxy-d3d9`:

- `alice_s2w_at_draw()` in `device_state.inc.h` uses the same draw-time mechanism as the shadow fix: it remembers the
  game's upload and sends `K_u·M` just before a draw with such a shader bound, once per upload. It always uses the
  input-space K.
- Its own switch is **`g_s2wOn`** (0 by default; poke-able and re-read every draw). Its own marker file is
  **`alice_vr_screentoworld_on.txt`**. It is independent of `g_shadowOn`: the upload memory runs when either is on.
  The `otherview` log line now ends `s2wfix ON/off sent= refused=`.
- New checks in `shadow_space_test.c`: 45 checks, 0 failed. All other suites still pass.
- DLL `build-2026-10-07b-screentoworld/d3d9.dll` (local only, git-ignored), **SHA-256 prefix `5d3ce56be320`**. RVAs
  for `poke.py` in THIS build: `g_shadowOn` **0x4cb990** (moved from 0x4cb988), `g_shadowSpace` **0x4b008**,
  `g_s2wOn` **0x4cb994**.

Not verified: nothing ran in the game. One thing is not handled: the motion-blur shader also uses
`PrevViewProjMatrix`, which comes from the game's unedited previous camera, so correcting the world point alone may
not make its velocity right `[hypothesis]`.

## 3. Per-eye error in the 40 shaders that are not stereo-aware `[verified-numerically 2026-10-07, n=1]`

The two-eye path shears the vertex matrix (`x' = x + S·(w − C)`, `S = p00·dx/C`). A shader that does not un-shear
rebuilds its world point sideways by **dx·|W/C − 1|**. The test checked this against the shipped shear at 6 depths,
to within 1 %.

At 95 units/m and 64 mm eye spacing, dx = 3.04 units per eye. With the default convergence C = 300 units (about
3.2 m):

| depth | error per eye |
| --- | --- |
| 450 to 630 units (5 to 6.5 m) | 1.6 to 3.3 units (2 to 3.5 cm) |
| 1,200 units | 9 units |
| 1,900 units | 16 units |

What that means for the eye `[inferred-static]`: in each eye the shadow pattern lands at the un-sheared (middle)
screen position, so both eyes see it with the disparity of the convergence plane. **Shadows would appear to lie at
about 3.2 m, not on the surface.** The angular error between the eyes is ipd·|1/C − 1/W|: about 0.6° at 6 m, about
1.2° at 1.6 m, and up to 1.2° far away. That is far above stereo acuity, so it is **visible as shadows floating at the wrong
depth** in the headset. Each single eye's picture looks almost normal, a few pixels off. It shows only while the
two-eye shear is on, and it is independent of the head-offset fix.

Possible fix (not built): fold the eye's shear into the edited map for those 40 shaders only. In u-space the shear is
linear, `u.x' = u.x + S·u.z − S·C·u.w`, so `U_e' = U_e·Sh_u` and the same K_u formula covers it. It must NOT be applied
to the 16 stereo-aware shaders, which un-shear themselves.
