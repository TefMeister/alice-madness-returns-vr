# 2026-09-04c (`/pd`, dev PC, static only) — the two-eye path is built, and the one-element lead turned out to be the second line of our own function

**The game was not launched, and nothing here has been run.** Both `[PD]` rows are closed, the
`/sr` inbox drop is settled with a numeric answer rather than an opinion, and the verdict has gone
back to the library that filed it.

---

## 1. The `/sr` lead: we already have it, and adopting it as written would remove something

`/sr` generalised `mad-max-vr`'s 2026-09-04 result — a per-eye camera offset is **one matrix
element**, not a rebuilt matrix — and correctly warned that on this build the element is the
transposed one, so it should be re-derived here rather than copied. It suggested switching to it.

Re-derived, and then checked against this project's own harness `[verified-numerically 2026-09-04]`:

- In Alice's column-major register layout the one-element edit is **`c3.x -= p00 · eye_dx`**.
- `alice_stereo_apply_viewproj()`'s second line is **`regs[3][0] -= S * C`**, and
  `S = p00 · eye_dx / C`, so `S · C == p00 · eye_dx` **identically**. The suite now asserts that.
- **So the one-element edit is already in the shipped function.** What the drop proposed adopting is
  a strict subset of what is there.

The first line, `regs[i][0] += S · regs[i][3]`, is the extra term. Measured across six vertices from
12 to 8,000 units of depth: the full shear and the one-element edit alone differ in NDC x by
**exactly `S`, a constant**, and are identical in `y` and in `clip.w`. So:

```
existing shear  =  one-element edit  +  a constant NDC shift of S
                =  a parallel eye translation  +  convergence re-centring
                =  off-axis (asymmetric-frustum) stereo
```

The suite also now proves the subset claim directly: the one-element edit alone reproduces a **true
parallel camera translation**, built as ground truth the other way round from the code under test.

**⇒ The lead is declined for this project, and the reason is not "ours is fine".** Two reasons, in
order of weight:

1. **The pixel stage cannot follow.** 28,017 shipped pixel shaders implement NVIDIA's two-parameter
   form themselves — `x + separation · (w − convergence)` — from bytecode we cannot change. The
   vertex stage must use the same formula or the two disagree by a constant, which the module's own
   header already flags as the coupling invariant. Switching the vertex stage to a pure translation
   would silently desynchronise every screen-space effect in the game.
2. **Nothing is gained.** The off-axis form contains the one-element form; the reverse is not true.
   Off-axis is also what the existing 54-configuration test verifies against ground truth.

That verdict is filed back to the cross-engine library's inbox so the technique page can carry the
caveat — the generalisation is right, and the "prefer it" advice needs a condition attached: *only
where nothing else downstream already implements the two-parameter form.*

⚠️ **What is NOT claimed:** that the drop was wrong. Its algebra reproduces here exactly; the
correction is about applicability on an engine with a second, unmodifiable stage.

## 2. The two-eye path

The mono shear was proven to reach the screen on 2026-09-04b, but it shifts **one** view — the state
struct has always had an `eye` field, and only a keypress (F10) ever changed it. So "both eyes" had
never actually been drawn.

**Built:** a `wiggle` mode that alternates the eye **at the frame boundary**, in `Present`.

- **Frame boundary, not mid-frame, and that is the whole design.** Within one frame the vertex shear
  and the pixel stage's fix texture must agree on which eye is being drawn, and both read
  `g_st.eye`. Flipping in `Present` means every frame is drawn entirely as one eye — exactly the
  single-eye path the 54 configurations verified — and the fix texture is re-uploaded once per
  frame, because `applyPixelStereo()` already caches on the eye.
- **F6 toggles it.** While it is on, F10 is refused with a log line saying wiggle owns the eye,
  rather than silently fighting it.
- A `wiggle flips` counter goes in the periodic log, so "the wiggle is not running" is
  distinguishable from "the wiggle is running and nothing moved" — two different bugs.

On a flat monitor this is wiggle stereo: the picture should rock left and right every frame, and the
rock should grow with ipd (F12). That is the cheapest honest evidence that **both** eyes are being
produced rather than one being shifted.

`[compile-verified 2026-09-04]`, clean at `-Wall -Wextra -Wpedantic -Wshadow -Wconversion`, imports
still system DLLs only, both exports intact. **Deployed** to
`Binaries\Win32\d3d9.dll` (702,976 B); the previous build is kept as
`d3d9.dll.bak-2026-09-04c-pre-twoeye` (701,440 B) and one copy reverts.

**NOT established:** that two eyes reach the screen. Every frame is a verified single-eye frame; the
new part is only that the eye alternates.

## 3. The logging hygiene row, which also removes the double-toggle dance

The second `[PD]` row asked to ungate `vp_writes` and log `have_p00` continuously. Done, and it
turned out to matter more than "hygiene":

- **Counting and `p00` recovery are no longer gated on `g_st.enabled`.** They are read-only —
  nothing is written back to the device unless the shear fires — but gating them meant `vp_writes`
  read 0 and `p00` read "NOT SEEN YET" until stereo had been on for a while. That is precisely why
  the 2026-09-04 morning launch was inconclusive and needed the F9 double-toggle dance.
- **The stats line is periodic, not one-shot.** The old line fired once, when 2,000 shaders had been
  seen — which on that launch was *before* stereo was ever enabled, so it reported zeros and the
  numbers that mattered were never printed again. It now prints at frame 120 and every 900 frames
  with the full state: enabled, wiggle, eye, ipd, convergence, `p00`, `S`, and the flip count.

**One launch now reads cleanly with stereo never enabled at all.**

## 4. What the next launch answers

Windowed (`AliceEngine.ini` `Fullscreen=False`). Reach gameplay, then read the log and the screen:

| step | outcome and meaning |
| --- | --- |
| before touching anything | the frame-120 line should already show `vp_writes` climbing and `p00=` a real number. **If `p00` still says NOT SEEN YET**, the c0 delivery finding is wrong for this scene, and nothing downstream is trustworthy |
| **F9** then **F6** | wiggle on. **The picture should rock left/right every frame**, and `wiggle flips` should climb in the log |
| **F12** a few times | the rock should grow with ipd. **Rock grows ⇒ both eyes are being produced.** No rock at all, with `wiggle flips` climbing ⇒ the eye is alternating but only one view reaches the screen — look at whether the fix texture is being re-uploaded (`draws_fixed`) |
| the outcome-4 question, unchanged | in a HUD/combat scene, does the HUD, crosshair, SSAO and decal layer move **with** the world or tear away? Tearing ⇒ the pixel-c4 concern is real and a per-eye build must cover the pixel stage too |

⚠️ F12 is also Steam's screenshot key — harmless, the proxy sees it either way.
