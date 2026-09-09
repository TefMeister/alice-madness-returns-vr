# 2026-09-09d — the eye point was in the matrix all along, and first person is now a knob

`/pd` session, dev PC. **The game was not launched. Nothing here has been run
against it.** The board's ⭐ `[PD]` row is closed: the eye-point translation is
designed, implemented, numerically verified, wired in and deployed.

Evidence: `dev-archive/recon/2026-09-09d-the-eye-point-is-in-the-matrix/`.
Code: `staging/alice-madness-returns-vr/proxy-d3d9/`.

---

## 1. ⭐⭐ The camera's world position is recoverable from the ViewProjection

The row asked where the head offset comes from *"given no pose dump is
reachable"*. The 2026-09-09 retraction had removed the `BugIt` route, and with it
the only known way to measure camera position and eye height.

**It was never needed.** The position is already in the matrix — three dot
products out of register 3.

Using this file's own accessors (`clip = c0·x + c1·y + c2·z + c3`, with
`column_j` meaning `(regs[0][j], regs[1][j], regs[2][j])`), for `VP = V·P` with a
symmetric projection over a rigid view:

```
    column_3   = forward           (unit - this is what row3_len reads as 1)
    column_0   = p00 * right       (its length is what recover_p00 returns)
    column_1   = p11 * up
    regs[3][j] = -(eye . column_j)
```

so

```
    eye.right   = -regs[3][0] / p00
    eye.up      = -regs[3][1] / p11
    eye.forward = -regs[3][3]
    eye         = eye.right*right + eye.up*up + eye.forward*forward
```

Every quantity on the right is one this project already reads for the shear or
for the yaw/pitch trace. Nothing new is measured; it was sitting in bytes we
were already looking at.

⚠️ **Gated on `alice_stereo_is_camera_vp()`, and that gate is load-bearing
rather than tidy.** The last line is only valid for an **orthonormal** basis,
which is precisely what that function's two tests establish. It also means a
matrix **we have already sheared is refused** — the shear adds `S·column_3` into
`column_0` and destroys the perpendicularity. There is a test for exactly that.

## 2. Moving the eye point

Translating the eye by a world offset `d` is exactly translating the world by
`-d`, and since `clip[j] = Σᵢ regs[i][j]·vᵢ + regs[3][j]`:

```
    regs[3][j] -= dot(d, column_j)      for j = 0..3
```

Four dot products, exact, no decomposition — and correct for **any** offset,
including one with a forward component, which a shear cannot express at all.
`alice_stereo_apply_eye_offset(regs, dx, dy, dz)` takes the offset in the
camera's own right/up/forward axes.

### ⚠️⚠️ The hazard this had to be designed around: do NOT put the IPD here

**The per-eye eye separation is already inside `alice_stereo_apply_viewproj()`.**
The dossier records that its one-element part *"alone reproduces a parallel
(on-axis) eye translation"*, with the extra `column_0 += S·column_3` term making
it off-axis. Passing an eye separation as `dx` as well would translate the eye
**twice** and be wrong by exactly one IPD — a mistake that looks perfectly fine
in a static test and shows up only as doubled separation in a headset.

This is pinned by test rather than left as a warning: **a pure eye translation
touches register 3 only, while the shear also rewrites column 0.** The two are
distinguishable in the matrix itself, so neither can be mistaken for the other.

**The IPD stays in the shear. The head/body offset stays in the new function.**

## 3. Verification — and a mutation check, because a passing test proves nothing on its own

The suite builds a VP from an explicit pose — a deliberately awkward one, no axis
world-aligned, the eye at `(1234.5, −678.25, 90.125)`, and an aspect ≠ 1 so `p00`
and `p11` differ — then requires the shipped code to read that pose back.
**Ground truth is constructed the other way round** from the recovery: the
builder writes columns from `(eye, right, up, forward)`, the reader takes them
apart. So agreement is not one formula checking itself.

Checks added `[verified-numerically 2026-09-09]`:

- the basis comes back (all nine components);
- **the eye position comes back**;
- an offset of (10 right, 20 up, 30 forward) lands **exactly** where asked;
- the inverse offset returns to the original — it must be reversible, because it
  is re-derived every frame and must not accumulate;
- a **zero** offset is **bit-identical**, not merely close — it runs every frame
  when the head offset is off;
- an already-sheared matrix is **refused** by both the reader and the writer;
- and the shear/translation signature check above.

⚠️ **The tests were then checked against themselves.** Flipping one sign in the
position recovery (`er = -regs[3][0]/p00` → `+`) produces **63 failures**;
restoring it gives ALL CHECKS PASSED. A suite that cannot fail is not evidence,
and this one demonstrably can.

## 4. Wired in and deployed

`device.cpp` applies the head offset **before** `alice_state_observe_vp()`.

⚠️ **That ordering is load-bearing and its failure mode is silent:** the offset
needs the orthonormal basis that the shear destroys, so applied afterwards it
would be refused every single frame — the camera would simply never move, with
nothing in the log saying why. The refusal is counted and printed
(`refused=`) precisely so that failure cannot be silent if the order is ever
disturbed.

The camera position is read on the same path, while the matrix is still
unsheared, and now rides in the `camtrace` line:

```
camtrace frame=... yaw=... pitch=... | pos=1234.5,-678.2,90.1
         head=0.0,0.0,0.0 applied=0 refused=0
```

**Tuning is by hotkey**, because this proxy has no ini at all — everything in it
is a hotkey, and inventing a config file would have broken that idiom (and
Enslaved has already shown what inventing config can cost):

| key | effect |
|---|---|
| **F3** | select axis — right → up → forward |
| **F4 / F5** | −5 / +5 units on the selected axis |

⚠️ F1–F5 were the only F-keys this proxy was not already using. **The game may
bind some of them itself**, so if F4 also does something in-game, that is the
collision and not a fault here. Every press logs the resulting triple.

**All three axes default to 0**, so this build takes the same path as the
previous one until a key is pressed. `[compile-verified 2026-09-09]`, exports
unchanged (2, matching the deployed build), full suite still green. Deployed:
717,824 B, sha256 `df862ab544c0…`, backup `d3d9.dll.bak-2026-09-09d-pre-headoffset`.

---

## What is NOT established

- **None of this has run.** Every claim is `[verified-numerically]` against
  matrices built in the test, or `[compile-verified]`. That the recovered
  position is *Alice's actual camera* in world units is `[inferred-static]` — it
  follows from the derivation, but no launch has confirmed the numbers are
  sensible for this game.
- **The diagnostic that would show the derivation is wrong** rather than a knob
  needing tuning: `pos=` in `camtrace` reading as a constant while the camera
  demonstrably moves, or jumping discontinuously when the view rotates. Either
  would mean the basis is not what the derivation assumes. A merely *wrong-scaled*
  position — moving correctly but by the wrong amount — is a units question, not
  a derivation error.
- **Where the head offset should actually sit is unknown and is a human
  judgement**, which is the honest answer to the row's second half. There is no
  head tracker in this loop yet and nothing in the game reports where a head
  would be, so for now it is three numbers dialled by eye. Later the same three
  numbers arrive from an HMD pose and the function does not change.
- **F1–F5 collision with the game is untested.**

## What the next flat run should do

Launch, get into gameplay, and read one `camtrace` line for `pos=`. Then press
**F3/F4/F5** and watch the view move.

| what you see | meaning |
|---|---|
| `pos=` changes smoothly as you walk, and F4/F5 visibly move the viewpoint | ⭐ the whole thing works; the remaining question is only where a head belongs |
| `pos=` never changes, or reads `NOT-READ` | the matrix is not being classified as camera-shaped on this path — check `camera-shaped` in the periodic line |
| `refused=` climbing | the offset is being applied after something destroyed the basis; the ordering has been disturbed |
| the view moves **twice** as far as asked | the IPD has leaked into the head offset — see §2 |
