# /gr 2026-09-29: the ScreenToShadow input is probably (screen x·w, y·w, w, 1): build K in that space

For the board's `[PD]` row "the draw-time shadow fix fires but does not look right yet" and dossier §6g's one
`[inferred-static]` assumption (the shader's screen-input convention).

In the Unreal lineage (UE4 shadow projection, `[reported]` from a public copy not linked here) the lookup is
`mul(float4(ScreenPosition.xy * SceneW, SceneW, 1), ScreenToShadowMatrix)`: a SCREEN position times depth, with w in
the third slot and a fix-up folded into the matrix. If Alice (UE3) does the same `[hypothesis]`, a rigid view-space
K applied to M is in the wrong space, which would give exactly the "moves, but wrong" shadows seen live.

Suggested next step (static): disassemble one ScreenToShadow pixel shader from `GlobalShaderCache-PC-D3D-SM3.bin`
and read how the vector multiplied by `c8..c11` is built. Topic:
`external-research/topics/2026-09-29-screen-to-shadow-takes-screen-position-times-depth.md`.
