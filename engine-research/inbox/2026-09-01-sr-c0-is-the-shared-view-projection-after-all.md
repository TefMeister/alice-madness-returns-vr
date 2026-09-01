# §6's `c0` caution is superseded: UE3/D3D9 *does* have a shared view-projection, and it is at `c0`

Supersedes: engine-research/ENGINE-DOSSIER.md §6, the bullet beginning "Important correction from this portfolio's own sibling project: `c0` is probably NOT a simple shared view-projection register"
Filed by: `/sr`, 2026-09-01 (cross-project research sweep)

## Short version

Your §6 currently warns, on `enslaved-vr`'s evidence, that `c0` is probably **not** a clean shared
view-projection register, and tells the next session to expect the harder per-object-WVP
decomposition case. **That reading has since been corrected at the source.** `c0` *is* the shared
view-projection. The correction is already in the cross-engine library and is not yet reflected here.

## What changed, and why the original reading was wrong

The pessimistic conclusion came from a live capture: `c0` received **47 uploads per frame**, which
looked like per-draw traffic and therefore like no shared register.

`[inferred-static 2026-09-01, n=1 — read from a game's own shipped `Engine/Shaders/*.usf`]` Enslaved
ships its UE3 HLSL sources, and `Common.usf` reserves the engine registers explicitly, noting they
must agree with `EVertexShaderRegister` in `RHI.h`:

| Register | Contents |
| --- | --- |
| `c0`–`c3` | **`ViewProjectionMatrix`** — world space to projection space |
| `c4` | **`CameraPosition` / `ViewOrigin`** — the world-space camera position, handed over directly |
| `c5` | **`PreViewTranslation`** — the far-from-origin precision offset applied to `LocalToWorld` |

**UE3's D3D9 RHI re-applies the reserved view registers around bound-shader-state changes.** So the
47 uploads are 47 writes of *the same value*, not 47 different matrices. The count was real; the
inference from it was not. That is the
[counting events is not measuring content](https://github.com/TefMeister/flat-to-vr-cross-engine-research/blob/main/docs/techniques/README.md#counting-events-is-not-measuring-content)
failure mode, and it is now written up as such.

Worth noting for morale: **your dossier's own suggested test was the right one.** It says to "flag any
register whose 4×4 value is identical across every draw in the frame" — that test would have flagged
`c0` correctly. What misled the sibling project was reasoning from an upload *count* instead of
running that comparison.

## What this is worth to this project specifically

§6 is this project's crucial section and it currently points the next session at the harder of two
paths. The corrected picture gives you the easier one:

- **A clean single injection point.** `SetVertexShaderConstantF(StartRegister == 0,
  Vector4fCount == 4)` is where the view-projection arrives. One intercept, per eye.
- **The camera position comes free at `c4`** — no solving it out of a matrix.
- `LocalToWorld` / `PreviousLocalToWorld` live in the **vertex factories**, so they are
  compiler-allocated at whatever higher registers each shader happens to use. They are not your
  problem at `c0`.

**⚠️ And take the trap that comes with it.** `PreViewTranslation` (`c5`) means vertices arrive in
*translated* world space. A per-eye offset that ignores `c5` **looks correct near the origin and
drifts as you move away from it** — it passes its first test and fails later, far from where it was
written. Given Alice's large levels this is a real risk, not a footnote.

## Confidence, honestly stated

This is `[inferred-static 2026-09-01, n=1]` — read from **Enslaved's** shipped shader sources, not
measured on Alice's binary. Enslaved is UE3/D3D9 with Ninja Theory's NTEngine layer on top; Alice is
UE3/D3D9 from Spicy Horse. The reserved-register convention is a property of stock UE3's RHI, so it
should hold, but "should hold" is not "verified here". **Verify on Alice before building on it** —
and the verification is cheap: hook `SetVertexShaderConstantF`, filter `StartRegister == 0 &&
Vector4fCount == 4`, and check the value is constant across a frame and changes as the camera moves.

Your dossier's existing caution to *build the detection first* was good advice and stays good advice.
What changes is the expected answer, and therefore what you should plan for.

## Full write-up

[`docs/engines/unreal-1-3.md` § Camera delivery](https://github.com/TefMeister/flat-to-vr-cross-engine-research/blob/main/docs/engines/unreal-1-3.md)
— the family page also covers the UE2/D3D8 `SetTransform` route and its early-out hazard, for
context on how the family differs by generation.
