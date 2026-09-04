# The per-eye edit is ONE matrix element, not a rebuilt matrix — and on this build it is the *transposed* element

Filed by: `/sr`, 2026-09-04 (cross-engine sweep, generalised from `mad-max-vr`). Library write-up:
[techniques → the edit itself is one element](https://github.com/TefMeister/flat-to-vr-cross-engine-research/blob/main/docs/techniques/README.md#-and-then-the-edit-itself-is-one-element-not-a-rebuilt-matrix)

Congratulations on the 2026-09-04b result — this is offered because the shear now demonstrably reaches
the screen, so the next question is what to write into `c0`, and there is a cheaper answer than the
obvious one.

## The result `[verified-numerically 2026-09-04, n=33 Python cases + 26 C assertions, on mad-max-vr]`

For **row-vector** storage (`clip = pos · M`), a per-eye camera is `V_eye = V · T` with `T` a
translation of `d` along the view x axis, so

```
M_eye = W · V · T · P  =  M + W · (V·T − V) · P
```

`(V·T − V)` has exactly one non-zero entry, `[3][0] = d`. Any **affine** `W` preserves that shape, and
post-multiplying by `P` makes it "row 3 gains `d` × row 0 of `P`". Row 0 of a perspective projection is
`[w,0,0,0]` for symmetric **and** off-centre frusta, because an off-centre frustum carries its shift in
row 2. So the whole edit is one float:

```
M[3][0] += d * w        // w = the horizontal focal term, from the SHARED matrix
```

## ⚠️ On this build it is the TRANSPOSED element

Alice stores its matrices as **`D3DXPC_MATRIX_COLUMNS`** — established by this project on 2026-09-03
`[verified-numerically 2026-09-03, n=54 configurations]`, and the library's UE3 page records it as the
transpose of Alan Wake's and Prince of Persia's row storage. **So do not copy the index above.** Under
column storage the same argument lands on the transposed element, and the safe move is to re-derive it
once against your own 54-configuration harness rather than to try both indices live. Your existing
suite is exactly the instrument for that.

## Why it may be worth switching to, even though the current shear already works

- **It touches nothing depth-related.** No row 2, no near/far, no `Q`. Any per-eye scheme that rebuilds
  `V_eye · P` has to get the depth convention right; this one cannot be affected by it.
- **One float instead of sixteen** — no decompose/recompose, no transcription surface, and a much
  smaller diff to reason about when the picture is wrong.
- **It carries over unchanged to the per-object path** if you ever need one: where the matrix is
  `W · V · P` rather than `V · P`, it is the same element, the same `d`, the same `w`.
- It is a cleaner shape for the **two-eye** step you still have open than a convergence-plus-IPD pair
  applied to a whole matrix, because the single parameter `d` is literally the eye offset.

## ⚠️ The one trap, which this project is well placed to hit

**`w` must come from the SHARED matrix, never from a per-object one.** `|column 0|` of a per-object
matrix has the object's scale baked in — a 3×-scaled object reads 3.54 where the true `w` is 1.18 — so
taking `w` from the matrix you are editing silently scales that object's separation by its own size.
This is the same rule as the library's existing "on a fused matrix, `p00` cannot be recovered under
object scale"; the one-element form does not escape it, it just makes it the only thing to get right.
On this engine `c0` is the shared view-projection, which is the good case — assert it anyway.

## Not established

That it renders correctly. On `mad-max-vr` the algebra is proven and the write path is built and
self-tested, and **nothing has been run**. Your project is further along on exactly this question, so
if you adopt it, your run is the first live evidence either project will have.
