# The 505.8× scale factor is a phantom — two different matrices share register c0

**2026-09-09, dev PC, `/pd`, NO LAUNCH.** The game was not launched and nothing here has been run.
This is arithmetic against code we own, plus a re-reading of a log we already had.

**Supersedes:** `modding-notes/2026-09-08c-the-disparity-shape-is-right-and-the-amplitude-is-380x-wrong.md`
§"But the amplitude cannot come from `p00 = 0.0022`" and §"What reconciles them"; and
`engine-research/ENGINE-DOSSIER.md` §6's reading of the 2026-09-08d diagnostic.

---

## The headline

The project's top task was **"apply the measured 505.8× scale factor"**, and everything stereo was
waiting on it. **There is no scale factor to apply.** Applying it would have multiplied the eye
separation by ~506 and produced an unusable picture, and the failure would have looked like a tuning
problem rather than a wrong premise.

The whole factor comes from one substitution: **a number recovered from one matrix was used in a
model of a different matrix.**

## What actually happened

The 2026-09-08 launch logged two numbers, both real, twenty seconds apart:

| where | value | what it is |
| --- | --- | --- |
| `VP DIAGNOSTIC (first perspective VP)` | `\|row0.xyz\| = 1.112762`, `\|row3.xyz\| = 1.000000` | the **camera's** matrix — an ordinary 83.9° projection over a rigid view |
| every periodic report, 24,300 frames | `p00 = 0.0022` | whatever wrote `c0..c3` **last** in the frame |

They are not the same matrix. `c0..c3` is not written by the camera alone, and the periodic report
sampled the last writer, which is consistently something else. Both readings were stable and
correct; only the label was wrong.

The 09-08c derivation then compared the measured disparity against `0.0022` as though it were the
camera's projection scale, found the measurement 380× too large for it, and proposed that `clip.w`
and `convergence` were in different units. `[disproved 2026-09-09]`

## Why the model was never using 0.0022 for the camera anyway

`device.cpp` recovers `p00` from a write and applies the shear **to that same write**, in that
order. A previous write cannot contaminate it. That was readable in the source but only assertable,
so the sequence is now one shipped function, `alice_state_observe_vp()`, and the ordering is
**tested**: camera → other → camera returns the camera's shear both times.
`[verified-numerically 2026-09-09]`

**And it has been that way since the first version.** This matters, because if the old code had used
a *stale* `p00` the 380× gap could have been real for the measurements it was derived from. Commit
`6f16757` (2026-09-03), the original interception, has the same two lines in the same order —
`recover_p00` → cache → `alice_state_shear` — and the only change since (`06ed7f1`, 2026-09-04) was
ungating the recovery from `g_st.enabled`, which moved nothing. `[inferred-static 2026-09-09]` — it
is a read of our own git history, not a live measurement.

So the scene geometry was always sheared with `p00 ≈ 1.11`. The gap was in the analysis, not in the
renderer.

## The numbers, all against the shipped code

`test/disparity_model.c` links the real `stereo_ue3.c`, so these are properties of the shipped
shear, not of a transcription. **23 checks, 0 failures.**

- **The measured ipd slope is inside range.** Model cap at C=300 is `p00·W/2C` = **2.374 px/unit ipd**;
  measured was **1.7833**. It fits at **z = 171.3 units**, in front of the convergence plane — which
  is also why the measured separations were negative. `[verified-numerically 2026-09-09]`
- **The whole ipd sweep is reproduced at that single depth**: −11.59 / −22.29 / −43.69 px against
  measured 12 / 22 / 44. `[verified-numerically 2026-09-09]`
- **The 09-08c note's own "the p00 that would fit is 0.836" is a LOWER BOUND**, because it assumes
  `z ≫ C`. The camera's measured **1.112762 is 1.33× that minimum**, so the requirement was already
  satisfied. This is the single cheapest way to see the error.
- **Section 3's "ceiling" objection only ever applied behind the convergence plane.** In front of it
  disparity is unbounded; the shipped shear passes 60 px unaided at z = 20.

## What this does NOT establish

Separating the load-bearing claim from the one that came with it:

- **Load-bearing and verified:** the camera's matrix is unscaled (`|row3.xyz| = 1.000000`),
  `convergence` **is** in its `clip.w` units, no scale factor is needed, and the shear has always
  used each matrix's own `p00`.
- **Still a hypothesis:** what the `0.0022` matrix actually *is*. A post-process or 2D pass is the
  obvious guess and is **not established**. It matters, because the proxy **currently shears it too**
  — any perspective write at `c0` gets a shear. That may be harmless or may be a real defect; no
  evidence either way. `[hypothesis]`
- **Still a hypothesis:** the 2026-09-07 `−1 / +34 / +60 px` populations. At the camera's `p00` all
  three become physical at ordinary depths (321 / 94 / 61 units) **under the flipped sign
  convention** — where at `p00 = 0.0022` no convention worked at all. That removes the paradox but
  does not prove the convention, which is still recorded nowhere. Alice's −1 px sits within noise of
  the convergence plane and discriminates nothing. `[hypothesis]`

## The diagnostic that told us the opposite, and why

The 09-08d diagnostic branched on the **ratio** and printed, for `|row3.xyz| = 1.0`:

> *"The matrix is uniformly scaled by ~1x, p00_cached is NOT the projection scale … the unit-mismatch
> hypothesis is CONFIRMED"*

That sentence contradicts itself — "scaled by ~1×" **is** "not scaled" — and the conclusion was
wrong. "Is this matrix scaled?" is answered by `|row3.xyz|` **alone**, so the branch now tests
`r3`, and for `r3 ≈ 1` it says plainly that no scale factor is needed and that a different `p00` in
a periodic report means **a different matrix**, not a misreading.

**The general trap, worth carrying:** a diagnostic that prints a number *and* its interpretation is
much more useful than one that prints only the number — and much more dangerous, because the
interpretation is read and the number is not. This one was believed for a day.

## What changed in the code

- `alice_stereo_is_camera_vp()` — is this matrix `P·V` with a symmetric projection and a **rigid**
  view? Tests `|row3.xyz| == 1` and `row0.xyz ⊥ row3.xyz`. A **uniformly scaled** camera matrix
  fails deliberately: that is the case a scale factor would genuinely fix, and it must stay visible.
  ⚠️ **Known limit, found by a test that first got it wrong:** a matrix with a tiny `p00` but a
  perfect shape is a valid narrow-FOV camera and **is accepted**. The classifier narrows the
  question; the reported **range** is what settles it.
- `alice_state_observe_vp()` — the per-write sequence, in one shipped function, so the ordering is
  host-testable instead of buried in a COM method.
- **The c0 census.** The periodic line now reports `p00 camera=… last=… range=[min .. max]` and a
  count of camera-shaped writes, instead of one field that silently meant "last writer". Two
  camera-shaped matrices three orders of magnitude apart cannot both be the camera, and one launch
  now makes that visible.

Cost: four float compares and a `sqrtf` pair on a path that already does the same work.

## Build and deploy

Deployed `d3d9.dll` md5 `1d534f20…`, 706,560 B; backup `d3d9.dll.bak-2026-09-09` (previous
`37293f99…`). `deployed.sh record` re-run for both DLLs. **Reproducibility re-verified:** two builds
of identical source hashed identically, so the `-Wl,--no-insert-timestamp` fix from 09-08d still
holds. Host suite: `stereo_ue3_test.exe` all checks passed, `disparity_model.exe` 23/0.

## The one thing to run next time the game is up

Launch, reach gameplay, **touch nothing** — stereo can stay off, the census is ungated — and read
the periodic line:

| what the line shows | what it means |
| --- | --- |
| `p00 camera=1.112762` and `range` spanning ~0.002 to ~1.11 | **confirmed**: two matrices share `c0`, the camera's is the ~1.11 one, and the next question is what the other one is and whether shearing it is a defect |
| `range` narrow around ~1.11, `camera-shaped` ≈ `vp_writes` | only one matrix arrives; the 0.0022 reading came from somewhere else and needs re-explaining |
| `p00 camera=NOT SEEN YET` with `vp_writes` climbing | nothing at `c0` is camera-shaped — the classifier's tolerances are wrong, or the camera reaches the shader another way |
