# 2026-09-09e — the camera position is uploaded, not derived; and a pure rotation passes our camera test

`/pd` session, dev PC. **The game was not launched. Nothing here has been run
against it.** Two findings, and between them they explain both halves of
yesterday evening's puzzle.

Code: `staging/alice-madness-returns-vr/proxy-d3d9/`.

---

## 1. ⭐⭐ `pos=` was not wrong arithmetic — it was the wrong SPACE

The 2026-09-09d launch measured `pos=` sitting at **0,0,0** while the player
visibly walked, moving only with our own head offset, at magnitude exactly
`|head|`. It was recorded as *"`pos=` IS NOT the camera's position"*, which is a
correct observation — but the **cause** matters, and it is not a mistake in the
algebra.

**UE3 hands the vertex shader PRE-TRANSLATED world space.** Alice ships
`PreViewTranslation` at **vs c5**, in **486** of its 2,807 vertex shaders
`[measured 2026-09-09]`. The world is offset so the action sits near the origin,
which is what keeps large maps precise in float. The view-projection therefore
maps *from* that translated space — and **the eye is at its origin by
construction.**

So `alice_stereo_camera_position()` recovering ~0 is the **correct answer to the
question it actually asks**: where is the eye, in the space this matrix maps
from? What it does not do — and what the note claimed it did — is give the eye
in **world** space.

⚠️ **The claim in dossier §6d and in the 2026-09-09d note is hereby narrowed.**
"The camera's world position is recoverable from the ViewProjection alone" is
**wrong for UE3**. The derivation is sound; the space is not world.

### The real route, and it is a read rather than a derivation

**`CameraPosition` is uploaded to vs `c4`, in 1,989 of 2,807 shipped vertex
shaders (71%)** `[measured 2026-09-09]`. The engine hands it over every frame.
No matrix algebra is involved at all.

The proxy now captures it. The write may arrive as its own one-register upload
or inside a larger block, so the test is **range containment** (`start <= 4 <
start+count`), not `start == 4`.

⚠️ **Which space c4 is in is NOT established.** UE3 uses `CameraPosition`
against translated world positions in several material nodes, so it may itself
be translated. **One launch settles it and the log says which:**

| `c4=` in the log | meaning |
|---|---|
| tracks the player as they walk | world space — this is the camera position, done |
| also sits near 0 | it is translated too, and the world offset is `PreViewTranslation` at **c5** — read that next |

Both outcomes are useful and neither is assumed. `c4=` prints `NOT-SEEN` until a
write covering it arrives, so "no data" is distinguishable from "zero".

---

## 2. ⭐⭐ A PURE ROTATION passes `is_camera_vp` — and that is very likely Wonderland

The other half. The head offset reached **78,358 draws** with `refused=0` and the
picture did not move by a pixel. `p00 camera` read **exactly 1.000000** in
Wonderland against **1.428148** in Whitechapel.

**`alice_stereo_is_camera_vp()` cannot tell a projection from a rotation.** It
tests `|column_3| == 1` and `column_0 ⊥ column_3`. **Every column of a rotation
matrix is unit length and mutually perpendicular**, so a plain world-to-view
matrix — with no projection in it whatsoever — passes both tests. And a `p00` of
**exactly 1.000000** is precisely what that looks like.

That would explain the whole observation at once: we classify a view matrix as
camera-shaped, apply the offset to it faithfully (`refused=0`, `applied=78,358`),
and the game never draws with it.

### The separator, and it costs one division

A real projection has

```
    column_0 = p00 · right ,  p00 = 1 / (aspect · tan(fovY/2))
    column_1 = p11 · up    ,  p11 = 1 / tan(fovY/2)
```

so **`p11 / p00` IS the aspect ratio.** A rotation gives **1.0**. At 16:9 those
are 1.778 apart — not a knife edge.

The proxy now prints `p11=`, `ratio=` and the **backbuffer's own aspect** beside
each other in `camtrace`, and flags `<-- ASPECT MISMATCH: not the game's
projection` when they differ by more than 10%.

⚠️ **Compared against the backbuffer, never against a constant.** On a square
render target a *genuine* projection also reads 1.0, and a check hard-coded to
"1.0 means rotation" would false-positive there. There is a test for exactly
that case.

**Verified** `[verified-numerically 2026-09-09]` — and the load-bearing half is
the second assertion:

- a projection built with aspect 16:9 reads `p11/p00 = 1.7778`;
- **a pure rotation also passes `is_camera_vp`** — this is the gap, asserted
  rather than described — and reads `p00 = 1.000000`, `ratio = 1.0`;
- the two ratios differ by more than 10% of the aspect;
- and a square-aspect projection reads 1.0 too, so the caller must use the
  backbuffer.

⚠️ **Mutation-checked:** making `recover_p00` read column 1 instead of column 0
produces **90 failures**; restoring gives all-pass.

---

## What is NOT established

- **That Wonderland's matrix is a rotation.** It is the best explanation of
  `p00 = 1.000000` and it is now measurable, but it has not been measured. The
  next launch's `ratio=` decides:
  - `ratio ≈ 1.0` with a 16:9 backbuffer ⇒ **confirmed**, it is not a
    projection, and the search moves to which write *is*;
  - `ratio ≈ 1.778` ⇒ **the rotation theory is wrong**, it really is a 90°
    projection, and the reason the offset does not reach the screen is something
    else entirely.
- **Which space `c4` is in**, as above.
- **Nothing here explains the London/Wonderland split by itself.** If the
  rotation theory holds it *describes* the split at `c0` but does not say why the
  two levels differ. That question stays open.
- The three-way split (first-person camera, FOV reading, head offset) may still
  have one common cause; this narrows two of the three to the same mechanism but
  does not join them.

## Deployed

718,336 B, sha256 `5ba6312df40a…`, backup `d3d9.dll.bak-2026-09-09e-pre-c4`,
`deployed.sh record` re-run, exports unchanged at 2, full suite green.

## What the next flat run should do

Nothing to configure. Get into **Wonderland**, read one `camtrace` line:

| field | what it settles |
|---|---|
| `ratio=` vs `bb` | rotation or projection — the headline question |
| `c4=` | whether the camera position is simply available |

Then repeat in **Whitechapel** for the comparison, since that is where the shear
visibly worked on 2026-09-04.
