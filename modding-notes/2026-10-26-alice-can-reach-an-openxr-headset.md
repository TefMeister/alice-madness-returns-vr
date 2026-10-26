# 2026-10-26 — Alice can reach an OpenXR headset (built and tested without the game)

`/pd`, dev PC. **The game was not launched.** The new code ran only inside two tests: a numeric test, and a small
stand-in program that played coloured frames through the shipped code into the OpenXR Simulator.

## What was asked

Tefa, 2026-10-17: *"start the porting now on all games that use openvr so they could work with openxr, we will
finish the mod with openxr first, then figure out openvr"*. Until today Alice only **read** the head pose from
SteamVR (a background app) and showed nothing in the headset.

## What was built

- **Hard Reset's headset thread**, copied into `staging/.../proxy-d3d9/src/xr/` from commit `82b18ba` (the newest
  copy on the estate; Psychonauts' copy is older and lacks the named binding constants and the jitter log's
  wall clock). Only the settings-file name, app name and BeG0nE game name changed, and the Ghost Hand calls came
  out: Alice has no hand gestures.
- **`src/xr_bridge.c`**, the Alice side: it reads each finished picture back to memory one frame late (never
  waiting for the graphics card) and hands it to the headset thread with the head pose it was drawn with.
- **`vr_pose.c` takes a second pose source** (`alice_vr_pose_use_reader`). With OpenXR on, OpenVR is never loaded;
  the first valid OpenXR pose becomes the origin (an OpenXR headset can come up seconds after the game), and
  everything after the read (re-centre, scale, offset and turn in the camera's frame) is the code that already
  worked in the headset on 2026-09-10.
- **Switch:** `ALICE_OPENXR=1` in the environment, or `enable=1` in `alice_xr.ini` beside the exe. Off by default.
  `stereo=1` starts in two-eye mode, `drawn_fov=0` sends the headset's own angles. The in-process
  `DISABLE_HAND_FREEZE_LAYER=1` is set unless already set (Hand Freeze's 64-bit layer stops 32-bit OpenXR, per
  the Hard Reset README), so a Steam launch works too, not only a launcher.

## ⚠️ The one Alice-specific design point: one eye per frame

Alice's stereo is "wiggle" stereo: frame N is the left eye, frame N+1 the right (stereo_state.h). So one headset
picture is a **pair of game frames**. If the head pose were renewed every frame, the two halves of a pair would be
drawn from two different head poses, and the headset would be told one pose for both: under head movement the eyes
would disagree (double vision). So with OpenXR on and both eyes on, **the head pose is renewed only before a left
frame and held for the right one**. `[compile-verified 2026-10-26]` for the hold; the pairing itself is
`[verified-numerically 2026-10-26]` below.

The cost: each eye shows at half the game's frame rate, and the head pose is renewed at half the rate too. That is
the price of drawing one eye per frame, not of OpenXR. ⚠️ If Tefa ever calls this **jittery** in the headset, the
first suspect is this rate (a pose renewed every second frame), not maths; the BeG0nE camera log will show it as
camera lines at half the picture rate. A later fix would draw both eyes in one frame.

## The angles each picture is sent with

So the headset lays the picture 1:1 over the lens instead of stretching it: half-width `1/p00` (the camera's own
projection scale, logged since 2026-09-09), half-height that times `h/w` (square pixels assumed), and the eye's
window centre at tangent `-eye_dx / convergence` (left eye leans right, which is what puts the convergence depth at
zero disparity). `[inferred-static 2026-10-26]`: it matches the shear stereo_ue3.h describes, but whether the game
really draws with exactly these angles needs the game. If the picture looks too big or too small in the headset,
`drawn_fov=0` is the A/B.

## Tests

- `test/xr_bridge_test.c`, in `build-stereo-test.sh`: **35 checks, 0 failed** `[verified-numerically 2026-10-26]`.
  An OpenXR pose (quaternion + position) goes through the shipped `xr_bridge.c` and `vr_pose.c`: 10 cm right gives
  +right only, 10 cm forward (-z) gives +forward only, a 30° turn to the left gives the forward axis at
  (-0.5, 0, 0.866) in the origin's frame, a pure turn gives no offset, and the drawn angles match an independent
  Python calculation (my hand-worked numbers were off in the 4th decimal and were corrected, not the code).
- `build/xr_selftest.exe <runtime json>`: the shipped bridge and headset thread with a real Direct3D 9 device, no
  game. Left frames solid red, right frames solid blue, then mono green. On the dev PC's OpenXR Simulator:
  **session running, 151 pairs handed over in 6 s, every one red-left/blue-right, 0 wrong, 0 failed readbacks,
  1 pair dropped, 456 headset frames submitted, 457 with their own pose, 109 mono pictures**
  `[measured 2026-10-26, n=1 run]`. The loader printed one "does not support simultaneous XrInstances" line and the
  session ran anyway; not investigated.
- Hard Reset's own handover tests pass against Alice's copies (11 + 7 checks).

## What is NOT established

- Nothing has run inside the game. Whether Alice's back buffer is 8-bit BGRA (the handover takes only that), and
  whether a multisampled back buffer resolves correctly, are unknown until a launch. The log says so in one line if
  the format is wrong.
- Whether the drawn angles are right (see above).
- The Reset path: the bridge lets go of its one DEFAULT-pool surface before the game's Reset; not exercised.

## Deployed on the dev PC

`d3d9.dll` sha256 `a40fc4717099`, 799,744 B, plus `openxr_loader.dll` (32-bit, the one Hard Reset and Psychonauts
use, `fb1e06de9653`) and `alice_xr.ini` with `enable=0` and the simulator's runtime. Backup
`d3d9.dll.bak-2026-10-26-was-5d3ce56b`. `deployed.sh record` re-run. ⚠️ The compiler is now llvm-mingw 20261006,
so builds no longer match older hashes byte for byte (the unchanged source built `81522d17…`, not `080ed4a06f9f`).

## Next

`[FLAT]` on the dev PC: set `enable=1`, launch, and check the log for `xr: session running` and `XRBridge: ...
handed`, a simulator screenshot shows Alice in both eyes, and a simulated head turn (`set_head_pose`) turns her view.
Then the home PC and the real headset.
