# The Duchess's-kitchen dumps are SH lighting, not a matrix — nothing to correct, no build

From: `/lm` reader helper (dev PC), 2026-09-11. Static only: the 8 dumps in
`dev-archive/recon/2026-09-11-alice-is-160-units-tall/log-5-duchess-kitchen-psdiag-dumps.txt`
(lines 2954–3041) and both shipped shader caches, read-only. No launch, no build, no staging edits, no git.

Supersedes: 2026-09-11-mod-reader-why-the-pixel-vp-never-matched.md §"The diagnostic", only in that
the diagnostic's `camera-shaped` counter is now known to admit false positives (see §4 below).

## 1. What the 7-register block at ps c4 is — `WorldIncidentLighting`

- **Measured** `[measured 2026-09-11]`: over both caches (`RefShaderCache` and
  `GlobalShaderCache`, SM3), the constants at ps c4 with **exactly 7 registers** are
  **`WorldIncidentLighting` in 4,130 shaders**, plus `SampleWeights` and `g_avSampleOffsets` once
  each (post-process). The dumps' uploads are `start=c4 count=7`.
- **It is not the shaders being missing from the map.** A shader missing from the map prints
  `(no map)`; these print `(none)` — mapped, with no parameter named ViewProjectionMatrix. Those are
  base-pass material shaders lit by spherical-harmonic incident lighting — the lighting a
  `DynamicLightEnvironment` gives a character or movable object (Alice has `MyLightEnvironment`).
- **The numbers fit SH lighting, not a projection** `[inferred-static]`. Register c4 reads
  `(0.716, 0.388, 0.227, 0)` in dump 1 and `(0.348, 0.208, 0.151, 0)` in dump 8: a positive leading
  term with a zero fourth value. The later registers carry signed values, as higher SH bands do, and
  the red leading term runs about 2–5× the value that would be green's under an R-then-G packing:
  warm, firelit light. That packing order is `[hypothesis]`; the name is measured.
  Dumps 1–7 are seven identical uploads in one frame: one lit object drawn in seven sections
  `[inferred-static]`.
- **Numerical check against the matrix reading** `[verified-numerically 2026-09-11, n=2 dumps]`.
  If the block were `A · VP⁻¹ · Q` with a camera-independent `Q` (a screen-to-light or
  screen-to-shadow matrix), stripping the camera out of dumps 1 and 8 with their own same-frame
  VPs would leave the same `Q`. It leaves two unrelated matrices (max difference 0.32 on entries
  of ~0.5; 57% relative after moving to absolute world). The candidate matrices at c4 were also
  ruled out on shape:
  - `ScreenToShadowMatrix` never spans exactly c4..c10 (its layouts are 5, 6 or 8 registers).
  - `ScreenToLight` (light functions) can span 7, but only 7 shaders carry it.
  - A screen-to-world matrix always outputs w = 1, which the dump's w lane does not.

## 2. Does it depend on the camera? No — no correction needed

Incident lighting is expressed in **world** axes. It says where the light arrives from, not where
it is seen from. Moving or turning the head changes neither `[inferred-static]`. So the
`M' = M · VP_old · VP_new⁻¹` style correction does not apply to this block.

For the record, the correction for a *real* screen-space matrix, should one ever turn up, is below
`[inferred-static]`; it is not needed here and nothing was built. With the pixel input
`(x·w, y·w, w, 1)`, `A` the projection's depth rows (from the VP here: M22 = 0.999, M32 = −9.99),
`VP_old` the game's matrix and `VP_new` the head-edited one, it is `M' = A · VP_new⁻¹ · VP_old · A⁻¹ · M`.
It would be applied in the pixel hook, keyed on the parameter name via the shader map.

## 3. Would the head-moved VP ever match here? No

This block is not a view-projection, so no tier can or should match it. The tolerant NEAR tier
requires all 16 floats within 1e-4 of a real camera matrix, which SH data cannot meet: the kitchen
line's `tier exact=0 origin=0 near=0` is correct behaviour, not a miss. `VP-shader-bound=0` in the
kitchen means that, again, no pixel shader that actually declares ViewProjectionMatrix at c4 was
bound during a full c4 write. The dynamic-light passes that use the real copy (3,580 with
`LightAttenuationTexture`) were not observed there.

## 4. A flaw in the diagnostic, for next time

`camera-shaped` uses the vertex path's classifier, whose `SCALED-PERSP` class accepts any four
vectors with lane 0 ⟂ lane 3 to 1% and a lane-3 length that is neither 0 nor 1. Arbitrary data
passes occasionally: 608 of ~357,000 full c4 windows here, all SH lighting. If it is ever rebuilt,
count only `CAMERA` (|lane 3| within 1% of 1), or require the window to match the frame's camera
p00/p11. Not changed now, per instructions.

## What stays open

Unchanged from the previous note: the real pixel VP copy must be observed in a scene with dynamic
lights (nearest: the TMaker piece of Chapter 1's first Wonderland world), and a split (under-4-
register) upload of it is still not excluded by the current counters.
