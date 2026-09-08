# The disparity *shape* is right. The amplitude is 380× wrong.

`/pd`, dev PC, 2026-09-08c. **The game was not launched. Nothing here has been run** — this is
arithmetic against code we own and numbers already measured.

Tool: `staging/alice-madness-returns-vr/proxy-d3d9/test/disparity_model.c`, which **links the
shipped `stereo_ue3.c`** and drives a point through the real `alice_stereo_apply_viewproj()`. It
runs on every `build-stereo-test.sh`.

## The derivation

Alice's shear is `clip.x' = clip.x + S·clip.w − S·C`, with `S = p00 · eye_dx / C` and
`eye_dx = ±ipd/2` (confirmed in `alice_state_eye_dx`). Dividing by `clip.w` and converting NDC to
pixels over a width `W`:

> **`disparity(z) = p00 · ipd · W / 2 · (1/C − 1/z)`**

**Checked against the shipped code, not assumed:** worst difference over 45 `(ipd, C, z)` points is
**6×10⁻⁸ px** `[verified-numerically 2026-09-08]`. A Far Cry 2 check once passed against a Python
transcription while the shipped C had a different bug, so the closed form is only used after it is
shown to reproduce the real function.

Two structural consequences, both asserted as tests:

- disparity is **exactly zero at `z = C`** — that is what convergence *means*;
- there is a **finite ceiling**: as `z → ∞`, disparity → `p00·ipd·W/(2C)`, and **that bound does not
  depend on depth at all.**

## ✅ The board's question, answered: the shape IS an off-axis frustum

The convergence sweep is the strongest evidence, and it needs **no depth estimate**. Alice — same
object, same scene, same ipd — was measured at three convergences: `98 → +78`, `300 → −1`,
`915 → +26`.

Fitting `K` and `z` to the first two points predicts the third:

| | predicted | measured |
| --- | --- | --- |
| conv 98 | +78.0 px | +78 |
| conv 915 | **−26.8 px** | 26 (sign unverified) |

**97% agreement on a point that was not fitted**, and the fitted depth comes out at **292 units** —
sitting on the convergence (300) that measured ~0, exactly as it must. The `1/C − 1/z` form
describes this field. `[verified-numerically 2026-09-08]`

⚠️ **It carries a testable prediction:** the model *requires* the conv-915 disparity to be
**negative** — the eyes reversed relative to conv 98. If a future capture shows conv 915 with the
same sign as conv 98, the form is wrong after all.

## ❌ But the amplitude cannot come from `p00 = 0.0022`

With the recovered `p00`, ipd 6.5, W 1280 and C 300, **the largest disparity this code can produce
at any depth is 0.0305 px.** The session measured +34 and +60.

**+60 px is 1,967× the ceiling, and no choice of depth closes that gap, because the ceiling does not
depend on depth.**

A second, independent measurement gives the same verdict and the same factor:

| | value |
| --- | --- |
| measured ipd slope | **1.7833 px per unit ipd** (R² 0.99948, n=4) |
| model's *maximum* slope at C=300 | **0.00469 px per unit ipd** |
| ratio | **380×** |

And the p00 that *would* fit is the most informative number in the whole analysis:

> to give 1.7833 px/ipd at C = 300, **`p00` must be 0.836** — which is `1/tan(hfov/2)` for a
> **horizontal FOV of 100°**.

That is an entirely ordinary projection scale for this game. **So `p00 = 0.0022` is almost certainly
not the projection x-scale it is documented as**, even though it is real and stable to four decimals
across 33,300 frames.

## What reconciles them — one hypothesis, and it is arithmetically exact

Per eye the NDC shift is `S(1 − C/w)`. When a point's `clip.w` is **small compared to the
convergence number**, the `C` cancels and the shift tends to `−p00·(ipd/2)/w`: the amplitude is then
set by `w` alone and the convergence value drops out.

Solving for the `w` that produces the measured 12 px at ipd 6.5 gives **w = 0.763**, and
**`C/w = 393`** — the same factor as the 380× scale gap, arrived at from a different measurement.
Feeding that `w` back through the **shipped** code reproduces the entire ipd sweep:

| ipd | shipped code | measured |
| --- | --- | --- |
| 6.5 | −12.0 px | 12 |
| 12.5 | −23.0 px | 22 |
| 24.5 | −45.1 px | 44 |

So: **`clip.w` and the `convergence` slider are plausibly not in the same units**, by a factor of
about 380. `[hypothesis]` — it is consistent with two independent measurements, and it is not proven.

## ⚠️ And a sign convention that is now load-bearing and is written down nowhere

Solving each measured population for its implied `w` at the session's settings:

| population | px | implied w | if the sign is flipped |
| --- | --- | --- | --- |
| Alice | −1 | 8.88 | −9.44 |
| world walls | +34 | **−0.269** | 0.269 |
| NPCs | +60 | **−0.153** | 0.153 |

The two positive populations have **no physical depth solution at all** — the implied `w` is
negative, which is not a depth. Reading them as magnitudes instead rescues those two and **breaks
Alice**, whose reading is already negative.

**No single sign convention makes all three physical**, so the discrepancy is *not* a sign artefact
— it is the amplitude. The tile matcher's convention should still be written down, because it
decides whether these populations sit in front of the convergence plane or behind it, but it cannot
rescue the scale.

## What is NOT established

- **Why `p00` recovers as 0.0022.** The unit-mismatch hypothesis fits two independent measurements
  and is the most economical explanation, but nothing here proves it. `[hypothesis]`
- That the conv-915 disparity is negative. The model **requires** it; no capture has confirmed it.
- Whether the shear that reached the screen used the documented `S` at all. The picture demonstrably
  moved, in proportion to ipd, at R² = 0.99948 — so *something* with the right functional form is
  driving it, and this analysis says it was not `p00 = 0.0022` acting as the code's comments
  describe.

## The one cheap thing that would settle it

**Log the full mathematical row 0 and row 3 of the ViewProjection once, alongside the recovered
`p00`** — sixteen floats, one line, on the existing F9 path. That decides between the two live
readings in a single launch:

| what the log shows | what it means |
| --- | --- |
| `\|row0.xyz\| ≈ 0.0022` **and** `row3.xyz` a unit-ish direction | the matrix really is world-to-clip and `p00` really is 0.0022 — then the amplitude that moved the screen did **not** come from our `S`, and the next question is what did |
| `row0.xyz` short because the whole matrix is scaled | the unit-mismatch hypothesis is confirmed, the convergence slider is not in world units, and the fix is a scale factor in one place |

Until then, treat the numbers on the convergence slider as **dimensionless knob positions, not
distances** — which is how they have actually been used.
