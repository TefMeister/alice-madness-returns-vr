# ScreenToShadowMatrix takes a SCREEN position times depth, not a camera-space point

*For the Fable job on the board: "the draw-time shadow fix fires but does not look right yet" (2026-09-29).*

## Why it matters here

The live test on 2026-09-29 moved the ScreenToShadow correction to draw time. It fires (7,401 corrections, 0
refused) and changes the shadows at a head offset of 200, but neither the corrected nor the uncorrected picture
matches offset 0. Dossier §6g derives the correction as `K · M`, with one assumption marked `[inferred-static]`:
**what the shader's input vector is.** That assumption now has a public lead.

## What the Unreal lineage does `[reported]`

In later Unreal (UE4) shadow projection shaders, the lookup is built as

    ShadowPosition = mul( float4(ScreenPosition.xy * SceneW, SceneW, 1), ScreenToShadowMatrix )

that is, the input is **(x·w, y·w, w, 1)** where x, y are the pixel's normalised SCREEN position and w is the scene
depth read back from the depth buffer. The third slot carries **w, not clip-space z**, so the engine builds the
matrix with a small fix-up in front of the inverse view-projection that turns that vector back into a clip-space
point before going to world and then shadow space. (Seen in a public copy of UE4's
`ShadowProjectionPixelShader.usf`; that copy is an unofficial mirror of Epic's licensed source, so it is not linked
or quoted here, and the claim stays `[reported]`.) UE3's shadow projection is the direct ancestor, so the same shape
in Alice (UE3, 2011) is likely `[hypothesis]`.

## What it would mean for the fix `[hypothesis]`

- The pixel position is where the pixel was drawn with **our edited camera**, and w comes from depth drawn with
  the edited camera; the matrix was built from the **game's** camera.
- A correction therefore has to live **in that same screen-times-depth space**: roughly
  `M' = F · inv(VP_edited) · VP_game · F⁻¹ · M` (row vectors), where F is the fix-up that maps (x·w, y·w, w, 1) to clip
  space. Applying a **view-space** (rigid) correction directly to M treats a screen-space input as a camera-space
  point, which would move shadows by a plausible but wrong amount: the symptom seen live.
- The exact order and where F sits depend on the row/column convention in Alice's compiled shader.

## The concrete next step

Static, no game needed: disassemble one of the 56 ScreenToShadow pixel shaders from Alice's own
`GlobalShaderCache-PC-D3D-SM3.bin` (the proxy's CTAB parser already locates them) and read how the input vector
for the `c8` multiply is assembled: is it `(xy·w, w, 1)`, `(xy, z, 1)`, or clip space? That settles the space K has
to be built in, from Alice's own bytes rather than a mirror.
