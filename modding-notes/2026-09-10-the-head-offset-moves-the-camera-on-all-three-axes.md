# 2026-09-10 — the head offset moves the camera, on all three axes

`/lm` session, dev PC, two launches (the first died in the level load). Evidence:
`dev-archive/recon/2026-09-10-sendfix-verify/`.

---

## The headline

**The send fix works. The head offset now moves the rendered camera, with stereo
OFF, on all three axes, and every step reverses exactly.** Build `7a9dd234e9bc`
(718,336 B), rebuilt from `staging/` at the start of the session and hash-identical
to the installed file, so the thing tested is the thing in the tree.
`[verified-live 2026-09-10, n=1 launch, 3 axes]`

Same scene (Wonderland, third person, camera untouched), all captures by BitBlt:

| step | offset | picture |
|---|---|---|
| no-input control, 2 s apart | 0 | **0 px**, corr 0.9995 |
| NumPad+ ×20 | right = 100 | **−62 px**, corr 0.76 |
| NumPad− ×20 | right = 0 | **0 px**, corr 0.9992 |
| NumPad+ ×40 | right = 200 | −86 px, corr 0.49 (see below) |
| NumPad5, NumPad+ ×20 | up = 100 | **dy = −74 px**, dx = 0 |
| NumPad5 ×2, NumPad+ ×40 | forward = 200 | camera ends up behind Alice's head |

By eye the moves are unmistakable: at right=100 the whole scene slides left with
Alice (near) moving further than the tree tunnel (far) — a real translation with
parallax, not a shear. At forward=200 the camera sits at the back of Alice's head.
The 200-unit figure reads low and its correlation is poor because a single global
shift stops describing a frame whose layers move by different amounts; the
direction and the monotonic growth are what that row establishes, not a rate.

The proxy log agreed at every step: `head=100.0,0.0,0.0 applied=5800 refused=0`,
and each `HOTKEY NumPad±` line read back the value I believed I had set — the
2026-09-09g trap (a key name that fails silently) did not recur because every key
was read back.

## The working half is still working

The shear shares the upload path with the offset now, so it had to be re-measured.
Stereo ON, eye L, convergence 300, same scene: `[verified-live 2026-09-10, n=2 at
ipd 31.5]`

| ipd | slide |
|---|---|
| 6.5 → 16.5 (10 units) | −7 px, corr 0.94 |
| 6.5 → 31.5 (25 units) | −19 px, corr 0.91 (twice) |

Linear at ~0.75 px per unit of ipd. The `OPEN` row asked for "the same ~44 px",
but that figure was 24.5 ipd units in the **London** scene (2026-09-07), where the
dominant surface sat at z ≈ 171 with a 70° camera. Wonderland's third-person camera
is a 90° projection (`p00cam=1.0`) looking down a long tunnel, so the slope is
scene-dependent by design. The check that matters — non-zero, linear, and
opposite in sign to nothing — passes.

## Depth is correct, and convergence does what it should

A left/right pair (F10 swaps the eye) at ipd 20.5, tiled phase correlation
(`dev-archive/tools/tiled_disparity.py`, new this session; tile 320 to keep the
shift inside ±160 px — at tile 160 the far tiles wrapped to −62 and looked like a
sign flip). `[verified-numerically 2026-09-10, n=2 convergence settings]`

| region | conv 300 | conv 123 |
|---|---|---|
| far tree tunnel (top rows) | +28 … +39 px | +91 … +105 px |
| ground at mid distance | 0 … +10 | +59 … +77 |
| Alice (nearest) | −7 | ~+65 |

Nearer surfaces have smaller disparity than farther ones at both settings, and
dropping the convergence from 300 to 123 pushes the whole map positive by the
amount the shipped model predicts (far: `K/C` with `K ≈ 12,000 px·units` gives 40
vs 98; measured 36 vs 97). The 2026-09-08c "amplitude 380× wrong" worry is
confirmed dead a second way.

## What this closes, and what it opens

- **Closed:** verify the send fix; re-measure the shear; the depth-correctness check.
- **The `PreViewTranslation` at `c5` suspect is not needed** for the picture to move.
  Whether `c5` (and the pixel-shader `CameraPosition` consumers) must also be
  translated for lighting, fog and reflections to stay coherent at large offsets is
  a separate question — nothing looked wrong by eye at 200 units, but "looked fine
  in one frame" is `[hypothesis]`, not a measurement.
- **`pos=` is fixed, and it was a third launch.** The reader's diff moves the
  camera-position read above the offset apply (18 lines move, no logic change).
  Built as `4b973e9eb89b` (718,336 B, backup `d3d9.dll.bak-2026-09-10-pre-posfix`),
  deployed after a graceful quit, relaunched, and with `head=100` the line now reads
  `pos=0.0,0.0,0.0` while the picture moves the same −62 px `[verified-live
  2026-09-10, n=1; the offset itself is now n=2 launches]`. For this build the game's
  own value is the eye in its translated space, zero by construction, so the field is
  a canary for the game moving its origin — not a position readout.
- **The reader's other answer, folded into the dossier:** `c5` is subtracted, never
  added, in all 367 shaders that bind it; it hands materials the absolute world
  position and cannot cancel a translation. Do not edit it. What a coherent offset
  still wants is the pixel-shader copy of the view-projection at `ps c4` (4,090
  shaders, un-translated) and `CameraPosition` at `vs c4` set to the offset — a
  `[PD]` row now, visibility `[hypothesis]`.
- **Open:** the HUD/crosshair half of outcome 4 still needs a scene that shows a HUD.
- **A head-tracked camera is now one tracker away.** The three numbers the hotkeys
  step are exactly the three a tracker would supply per frame.

## The crash, seen a second time

Launch 1 died in the CONTINUE GAME level load: `AliceMadnessReturns.exe`,
`c0000005`, fault offset `0x00be0f63` — a *different* offset from 2026-09-09's
`0x00067d48`, same phase, faulting module the exe both times. The proxy had logged
nothing unusual and the head offset was 0. Launch 2 loaded cleanly. `[measured
2026-09-10, n=2 of ~7 launches]` The profile's "relaunch once" advice held.

## Automation — all five capabilities, this session

Launched the game myself (twice), drove title → copyright → profile → CONTINUE
GAME → gameplay with a screenshot check at each screen, issued proxy commands,
moved the camera on three axes, and closed it through its own menus.
`[verified-live 2026-09-10, n=1]` One small trap: the first Enter after launch is
swallowed if it lands before the title screen is interactive; a check at each
screen costs one capture and removes the guesswork.
