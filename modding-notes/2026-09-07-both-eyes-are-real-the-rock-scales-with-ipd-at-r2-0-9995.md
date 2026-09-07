# 2026-09-07 — Both eyes are real: the rock scales with ipd at R² = 0.99948

*Session: `/lm alice`, dev PC, ONE FLAT LAUNCH, fully autonomous after the launch (Tefa at work —
launched the game and touched nothing else). Game closed gracefully through its own menu at 11:23.*

The board's starred row asked one launch to answer three things. **(a) passes, (b) passes
decisively, (c) is still walled** — and the wall is not a technical one, it is that this save is at
0% completion and Alice has no HUD or combat until Wonderland.

---

## (a) The instrumentation is honest now `[verified-live 2026-09-07]`

The 2026-09-04c hygiene fix did what it was meant to.

| frame | `vp_writes` | `p00` |
| --- | --- | --- |
| 120 | 0 | `NOT SEEN YET` (still in the menu — correct) |
| 900 | 4,662 | **0.0022** |
| 1,800 | 24,462 | 0.0022 |
| 2,700 | 44,262 | 0.0022 |
| 33,300 (quit) | 1,146,811 | 0.0022 |

`vp_writes` climbs at ≈22 writes/frame and `p00` is recovered and **stable to four decimals over
33,300 frames**. The very first `F9` press already logged `p00=known` — so **the F9 double-toggle
dance is retired**, exactly as the row predicted.

`p00 = 0.0022` is small, which is why the default ipd/convergence shift was described as
"sub-visible" on 2026-09-04. It is not sub-visible — see (b). It was the *measurement* that was
sub-visible before.

---

## (b) ⭐ BOTH EYES ARE BEING PRODUCED `[verified-numerically 2026-09-07, n=4 ipd settings, 60 frames]`

`F9` then `F6`, then bursts of screen captures analysed by 1-D cross-correlation of column-mean
profiles (a stereo shear is a *coherent horizontal translation*, which is precisely what that
measures; scene animation is not).

**The control matters as much as the result.** With stereo OFF, 16 consecutive captures of the
animated scene gave **spread = 0 px, every frame dx = +0**, correlation 0.984–1.000. Whitechapel
has walking NPCs, drifting fog and idle animation, and none of it produces a horizontal
displacement. So the noise floor is not "small", it is **zero**, and anything non-zero is signal.

With wiggle ON the frames split into **exactly two clusters** — never three, never a continuum —
because each capture lands on either a left-eye or a right-eye frame:

| ipd | cluster separation | px per ipd unit |
| --- | --- | --- |
| 6.5 (default) | 12 px | 1.846 |
| 12.5 | 22 px | 1.760 |
| 18.5 | 33 px | 1.784 |
| 24.5 | 44 px | 1.796 |

Least squares over the four points:

```
separation = 1.7833 * ipd + 0.108 px
residuals  = [+0.3, -0.4, -0.1, +0.2]   max |resid| = 0.40 px
R^2        = 0.99948
```

**Proportional, through the origin, sub-pixel residuals.** That is what a stereo baseline must do
and what a mono image being shoved sideways cannot. Evidence:
`dev-archive/recon/2026-09-07-two-eye-wiggle-test/ANAGLYPH_ipd245.jpg` (red/cyan, the separation is
obvious by eye) and `ARCH_ANAGLYPH.jpg`.

⚠️ **The measurement tool was validated before it was trusted.** `alice_harness.py` recovered
**7/7 synthetic offsets exactly** (−40…+40 px, corr 1.0000) with a different-scene control at corr
0.4556. The 2026-09-04 morning session reported a working lever as "no effect" using mean-luma
differencing; this is the fix for that class of error, and it is why the numbers above are trusted.

---

## The disparity is depth-dependent, not a uniform slide `[measured 2026-09-07]`

Block-matched disparity over a 31×17 grid (trust filter: peak > 0.55 **and** peak/second > 1.12),
at ipd 24.5 / conv 300, standing under the Whitechapel arch — **416 of 527 tiles trustworthy,
range −5 … +63 px**. Three clearly separated populations:

| region | dx | peak | ratio |
| --- | --- | --- | --- |
| **Alice (player character)** | **−1** | 0.907 | 2.11 |
| world, left brick wall | +34 | 0.820 | 1.18 |
| world, right brick wall | +34 | 0.884 | 1.25 |
| NPCs under the arch | +60 | 0.812 | 1.48 |

A uniform slide would give one number everywhere. It does not.

### Alice reads ≈ 0 because she sits at the convergence distance — she IS sheared `[verified-live 2026-09-07, n=1 scene]`

In the anaglyph Alice shows almost no fringing while everything around her doubles, which looks
alarming — a flat cardboard character in a stereo world is exactly the failure that would ruin this
in a headset. It is not that. Holding ipd at 12.5 and sweeping convergence:

| convergence | ALICE | world wall | NPCs |
| --- | --- | --- | --- |
| 98.3 | **+78** | +96 | +109 |
| 300.0 (default) | **−1** | +17 | +17 |
| 915.5 | **+26** | +8 | −5 |

**Alice's disparity moves, and moves a long way.** So the character path is *not* being skipped;
her near-zero disparity at default settings is the convergence plane sitting near the third-person
camera distance. The alternative hypothesis — "skinned characters are not sheared" — is
**`[disproved 2026-09-07]`**, and the NPCs (also skinned, also sheared, +60) independently agree.

Per-region ipd proportionality holds too: the same wall reads **+9 px at ipd 6.5** and **+17 px at
ipd 12.5**, against 17.3 predicted from the ×1.92 ipd ratio `[verified-numerically 2026-09-07, n=2]`.

### ⚠️ What is NOT established

Whether the disparity *field* matches an ideal off-axis frustum quantitatively. The convergence
sweep does **not** fit a simple "convergence = one uniform constant added to every depth" model, but
that is a limit of the test, not a finding about the code: at conv 98 the disparity saturated the
±90 px search window, and the NPC region walks between bursts, so two of the four rows are unsound.
This needs a **static scene with a long, well-lit sightline** — Whitechapel's far field is too dark
to block-match (far probes came back at peak 0.19–0.43, i.e. no measurement at all, not "zero
disparity"). Tagged `[hypothesis]` until then.

---

## (c) Half answered, and the other half is walled by the save

**Decals move WITH the world `[verified-live 2026-09-07, n=1 scene]`** — the paper posters on the
right-hand brick wall read **+34 px**, identical to the bare brick beside them (+34) and below them
(+34), all at peak 0.98–0.99. No tearing.

**HUD, crosshair and SSAO are still unjudged.** Whitechapel at 0% completion has no HUD and no
combat, which is the same wall 2026-09-04 hit. `EXTRA CONTENT` was checked and is galleries only —
CHARACTERS / TROUBLING VISIONS / THEATRICALS / PAST MATTERS / CREDITS, **no playable level**
`[verified-live 2026-09-07]` — so there is no menu shortcut to a combat scene.

### The pause menu's world does not shear `[verified-live 2026-09-07, n=1]`

Worth recording because the test could have produced a positive and didn't. Paused with stereo and
wiggle ON: the 3D world is plainly visible behind the stats book, **frames kept advancing**
(24,300 → 25,200) and **`wiggle flips` kept climbing one per frame**, so the eye really was
alternating — and the capture spread was **0 px**. The visible menu-time world is not receiving the
c0 vertex shear.

⚠️ **Do not read `draws_fixed` as corroboration here.** It counts *pixel*-shader fix-texture
bindings (`applyPixelStereo`), not vertex-sheared draws — it says nothing about the c0 path. Its
rate is a separate curiosity: ≈5/frame in gameplay, ≈1/frame in menus. **Why** the menu world is
unsheared is `[hypothesis]`; only the observation is verified.

---

## Automation (§5a), scored by name

1. **Menu → gameplay ✅** — title → copyright → PROFILE SELECT → CONTINUE GAME → Whitechapel, driven
   cold and unassisted.
2. **Commands ✅** — F6/F7/F8/F9/F11/F12 all exercised live this session. Previously only F9 was.
3. **Character movement ✅ NEWLY PROVEN** — `W` scancode 0x11 walks Alice; 12 taps moved her from in
   front of the arch to under it (`m00_before_move.jpg` → `m01_after_W.jpg`). The profile had this
   as never exercised. **Camera control still NOT exercised** (needs mouse injection; the harness is
   keyboard-only).
4. **Self-close ✅** — quit gracefully through MAIN MENU → EXIT GAME → yes; proxy logged a clean
   `unloading`. Never killed the process.

### Two profile route corrections, both caught by verify-before-commit

- The pause menu opens on **MEMORIES**, so MAIN MENU is **Down×3**. The profile said Down×2, which
  lands on **RESTART**.
- After backing out of a submenu the main menu resets its highlight to **CONTINUE GAME**, so
  EXIT GAME is **Down×5** from there, not Down×3 from where you were.

Neither was destructive here, but both are exactly the miscount that overwrites a save on a menu
with a `DELETE` on it.

---

## ⚠️ The board's `AliceEngine.ini` correction is machine-specific, and inverted on this PC

The `OPEN` row carries, as `[verified-numerically 2026-09-05]`, *"The ini is NOT called
`AliceEngine.ini` … no file named `AliceEngine.ini` exists anywhere."* That is true on the **home
PC**. On the **dev PC it is false** — both config trees exist:

| tree | `Fullscreen` | last written | verdict |
| --- | --- | --- | --- |
| `My Games\Alice Madness Returns\AliceGame\Config\AliceEngine.ini` | `False`, 1280×720 | Sep 4 **16:19** — rewritten by the game on exit | **the live one here** |
| `My Games\UnrealEngine3\MonkeyGame\Config\MonkeyEngine.ini` | `True`, 1920×1080 | Sep 3 13:41 — untouched by the Sep 4 runs | inert on this machine |

The launch settled it: the game came up **windowed 1280×720**, which only `AliceGame\Config` asks
for `[verified-live 2026-09-07, n=1]`. A dev-PC session following that row literally would have
edited `MonkeyEngine.ini`, seen nothing change, and concluded the windowed fix had failed.

**The durable claim is not "which filename".** It is: *this game has two config trees and which one
is live differs per machine — check mtimes, and let the game tell you by rewriting one on exit.*

---

## Tools

`dev-archive/tools/alice_harness.py` — new, and committed this time. No harness script survived
2026-09-04, only its outputs, so it was rebuilt from scratch. BitBlt (never `PrintWindow`),
scancodes with `KEYEVENTF_EXTENDEDKEY` on the arrow block, 80 ms holds for the once-per-`Present`
rising-edge hotkey poll, plus `burst` / `shift` / `cluster` for the displacement analysis.
