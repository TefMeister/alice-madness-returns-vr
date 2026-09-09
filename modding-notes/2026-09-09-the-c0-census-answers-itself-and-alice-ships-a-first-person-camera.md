# 2026-09-09 — the `c0` census answers itself, the camera's heading is readable, and Alice ships a first-person camera

*Session: `/lm alice-madness-returns-vr`, dev PC, four launches, fully autonomous including every
launch, relaunch and close. Evidence:
`dev-archive/recon/2026-09-09-c0-census-camera-yaw-and-the-built-in-first-person-camera/`.*

Three board rows were open on this project and two of them were `[FLAT]` stars. Both are answered,
and a third thing turned up that is larger than either.

---

## 1. The `c0` census — ANSWERED, and the first outcome is the one that happened

The row asked for one free read: launch, reach gameplay, touch nothing, and read the periodic
line's `p00 camera=… last=… range=[…]`.

```
frame 5400 | vp_writes=142388 (camera-shaped 137954) | p00 camera=1.428148 last=0.002210
            range=[0.002210 .. 2.747477]
```

**The range spans three orders of magnitude, so more than one matrix arrives at `c0`.**
`[measured 2026-09-09, n=1 launch, 5400 frames]` That is the row's first branch, and it settles in
the affirmative the question the 2026-09-09 `/pd` correction left open.

Two further things fell out of the same line, neither of which the row asked for:

**The camera's `p00` is scene-dependent, and the classifier follows it.** 2.747477 in the menus
(hfov ≈ 39.9°), 1.428148 in Whitechapel gameplay (hfov ≈ 70.0°), 1.569685 in first person
(hfov ≈ 65.1°). The 1.112762 that the first-perspective-VP diagnostic reports (hfov ≈ 83.9°) is a
*fourth* value — it is whatever camera happens to be up when the first perspective matrix is seen,
not a constant of the game. `[measured 2026-09-09]`

**The 0.0022 matrix is written EXACTLY ONCE PER FRAME, and it is the LAST write of the frame.**
Non-camera-shaped writes rise by exactly 900 across each 900-frame reporting interval, on three
consecutive intervals — one per frame, no remainder. Camera-shaped writes rise by about 38 per
frame over the same intervals. `[verified-numerically 2026-09-09, n=3 intervals]`

That is the complete mechanical explanation of the 2026-09-08 reading. A report holding one `p00`
field showed the last writer; the last writer is this matrix; it is not the camera's. Nothing about
it was mysterious and nothing about it was a mis-read.

**And the classifier's known limit does not bite here.** The host test records that a tiny-`p00`
matrix of the right *shape* would be accepted as camera-shaped. Alice's actual 0.0022 matrix is
**rejected** — it is the one non-camera write per frame. So on this game the classifier does
separate the two. `[measured 2026-09-09, n=1 launch]` The limit stays in the test, because it is a
limit of the function, not of this game.

---

## 2. Camera yaw — built, tested, deployed, and then actually used

`alice_stereo_camera_angles()` reads the heading out of the matrix the shear already reads. Row 3 of
a camera-shaped VP produces `clip.w`, its `xyz` has length exactly 1, so it **is** the camera's
forward axis in world space; UE3 is X-forward, Y-right, Z-up, so `yaw = atan2(row3.y, row3.x)` and
`pitch = asin(row3.z)`. Nothing is calibrated and no convention is guessed.

Nine host checks cover it, including a round-trip through five known (yaw, pitch) pairs and a
refusal on a non-camera-shaped matrix. `[compile-verified 2026-09-09]`

The proxy now writes a `camtrace` line every 30 frames (about one second):

```
camtrace frame=2700 yaw=+0.000 pitch=+0.000 total=-124.50 dmax=0.00 spread=0.000 n=38 p00cam=1.428148
```

`spread` is the largest wrapped disagreement between the ~38 camera-shaped writes **within one
frame**. It reads **0.000 in every line of two launches**: they all carry one heading, so "the
camera's matrix" is a well-defined thing to talk about. `[measured 2026-09-09, n=2 launches]`

### The turn rate, which is what the row existed for

The first build reported only the wrapped yaw, and that was **not enough** — a press turns this
camera so far that consecutive readings pass 180° and wrap, which reads as a small delta in the
wrong direction. So `total` was added: the per-frame wrapped delta accumulated, which is
unambiguous for any turn as long as no single frame turns more than 180° (`dmax` reports the largest
single-frame step, so a reader can check that rather than trust it).

With that, the measurement is clean. One press is the harness default, an 80 ms hold:

| presses | turn measured | per press |
| --- | --- | --- |
| 1 | −94.20° | −94.20° |
| 1 | −94.17° | −94.17° |
| 2 | −188.33° | −94.17° |
| 4 | −380.57° | −95.14° |

**One press turns the third-person camera by about −94°, and presses compose linearly.**
`[verified-numerically 2026-09-09, n=4 measurements, spread ~1%]` Confirmed by eye as well: one
press swings the camera roughly a quarter-turn around Alice (`turn-01` against `turn-02`).

**That is why 2026-09-08b could not measure this from screenshots.** Its 10-to-100-press sweep was
2.6 to 26 full revolutions. There was never a return-to-start to find, and no amount of image
analysis would have produced one.

**Hold duration is NOT a usable dial.** 20 ms → −5.31°, 40 ms → −168.69°, 80 ms → −94.20°,
160 ms → +75.39°. Not monotonic, not proportional, and 80 ms is repeatable while its neighbours are
not. `[measured 2026-09-09, n=1 per duration]` Why is **not established**; the bind is
`Axis aTurn Speed=+200.0 AbsoluteAxis=100`, and `AbsoluteAxis` combined with frame-rate sampling is
the obvious suspect, but nothing here tests it. `[hypothesis]`

**Pitch is exactly 0.000 in third person, in every line.** The follow camera is level.

---

## 3. ⭐⭐ THE HEADLINE: Alice ships a first-person camera, and it is already on a key

The user said, mid-session, that Alice has a first-person view. They are right, and it is better
than that: **it needs no mod, no rebind and no console.** The shipped
`AliceGame/Config/AliceControlLayout.ini` contains

```
KeyBindArray1=(Name="T",Command="EnterFPSByRS | OnRelease ToggleCloseFollowCamera")
KeyBindArray1=(Name="XboxTypeS_RightThumbstick",Command="ToggleGhost | OnRelease ToggleCloseFollowCamera |EnterFPS")
```

**Press `T`. Alice leaves the frame and the camera drops to eye level.**
`[verified-live 2026-09-09, n=1 launch]` — `fps-01` (third person) against `fps-02` (first person),
one keypress apart.

This is the toolkit's standing rule playing out exactly: the feature was reachable by a **controller
chord** (right-stick click), which is why pressing keys had never found it — except that here it is
*also* on `T`, and nobody had read the layout file. `AliceInput.ini` even carries
`LookRightScaleForFP=500` and `LookUpScaleForFP=-350`, dedicated first-person look scales, in a file
this project has opened several times.

### What first person is like, measured

- **The camera moves in much smaller steps than in third person, but the step is NOT a constant.**
  One press is roughly **20° of yaw** against 94° in third person — so the control is far finer — but
  repeats of the same burst gave −21.13°, −21.16°, +5.78° (÷2) and −12.44° (÷4).
  `[measured 2026-09-09, n=4 bursts]` **Pitch moves, and clamps at about ±90°** — straight up and
  straight down — after which further presses do nothing `[measured 2026-09-09, n=4 bursts]`.
  ⚠️ The first readings of this session (2.9° yaw, 10–15° pitch) were single samples of a quantity
  that is not stable, and should not be quoted as rates. **The only per-press figure on this game
  that repeats is the third-person yaw, −94.2°.**
- **hfov ≈ 65.1°** (`p00cam` 1.569685) against 70.0° in third person. `[measured 2026-09-09]`
- **It survives walking.** Twelve forward taps and the view was still first person.
  `[verified-live 2026-09-09, n=1]` What *does* leave it is readable in the same ini: `QuitFPS` is
  attached to attacking, weapon switching and most context actions. `[inferred-static 2026-09-09]`

### The sign convention, recorded at last

The board has wanted this written down since 2026-09-07. First person is what made it checkable,
because third person never pitches at all.

**Positive pitch is looking UP.** Verified by eye at two angles: pitch −30.15° is the cobbles
(`fps-03`), pitch +60.27° is the sky (`fps-04`). `[verified-live 2026-09-09, n=2 angles]`

⚠️ And a trap worth carrying: **`aLookUp` with a POSITIVE `Speed` pitches the view DOWN.** The bind
named `NumPadEight … Axis aLookUp Speed=+25.0` produces negative pitch. The axis name and its sign
disagree, and nothing errors.

### The rest of the vocabulary this file exposes

`AliceControlLayout.ini` names a whole set of camera and debug actions reachable by rebinding a key,
with no console and no proxy: `EnterFPS` / `EnterFPSByRS` / `QuitFPS`, `ChangeCameraMode`,
`ToggleCloseFollowCamera`, `TogglePOI`, `ToggleGhost`, `togglephysicsmode`,
`BugItForGameController`, `StatUnitAndStatFPS`. **None of these has been tried except
`EnterFPSByRS`.** `BugItForGameController` is worth a look first — 2026-09-08 established the
console is not exposed in this retail build, and this is a second route to the same `BugIt` pose
dump that does not go through a console at all. `[reported 2026-09-09, from the shipped ini]`

---

## 4. One crash, not reproduced

The first launch of the session died with an access violation during the level load
(`AliceMadnessReturns.exe` + `0x00067d48`, `c0000005`; the faulting module is the exe, not
`d3d9.dll`). Three further launches — the same build, then two newer proxy builds — all loaded the
same save cleanly. `n=1`, cause **not established**, recorded so a second occurrence is recognised
rather than investigated from scratch. `[measured 2026-09-09, n=1]`

---

## 5. What this session did NOT establish

- **Why hold duration behaves erratically.** Measured, not explained.
- **What the once-per-frame 0.0022 matrix IS.** The census proves it is not the camera and counts it
  exactly; it does not name it. The proxy still shears it, and whether that is a defect still has no
  evidence either way.
- **Whether the first-person camera is usable for the VR work.** It exists, it aims, and it survives
  walking. Comfort, head height, weapon handling and what happens in combat are all untested, and
  the first two need a person in a headset rather than a measurement.
- **Anything about the other camera commands.** They are read out of a shipped ini, which is a lead
  and not evidence — the standing rule.
