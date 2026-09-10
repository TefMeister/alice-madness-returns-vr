# 2026-09-10c — head tracking is wired in, and it needed no new keys

`/pd` session, dev PC. **The game was not launched and nothing here has been run
against it.** Everything below is compile-verified or checked numerically on the host.

---

## The headline

**The proxy now reads the headset's position from SteamVR and feeds it straight into the
head offset — the three numbers proved to move the rendered camera this morning.**
Build `ad093b5cc177`, 723,968 B, deployed, backup `d3d9.dll.bak-2026-09-10c-pre-tracker`.
`[compile-verified 2026-09-10]`

The feature is five lines in `Present`, because the hard part was already done:

```c
if (alice_vr_pose_start()) {
    float ruf[3];
    if (alice_vr_pose_offset(ruf)) { g_headR = ruf[0]; g_headU = ruf[1]; g_headF = ruf[2]; }
}
```

`g_headR/U/F` are a head offset in the camera's own basis, and they were shown to move the
camera on all three axes with two launches this morning `[verified-live 2026-09-10, n=2]`.
This session's work is entirely about filling them honestly from a tracker.

## It needed no new keys, which was the row's stated blocker

The `OPEN` row asked for a re-centre key, and the keypad is completely full. It turned out
not to matter: **once the head drives the offset, choosing an axis by hand and stepping it by
hand are both meaningless.** So the three head-offset keys change meaning when a tracker is
live, and nothing is displaced:

| key | no tracker | tracker live |
|---|---|---|
| NumPad5 | cycle axis right/up/forward | **re-centre** |
| NumPad+ | step the axis by +5 | **scale ×1.25** |
| NumPad− | step the axis by −5 | **scale ×0.8** |

Everything else is untouched, and on a machine with no headset the build behaves exactly as
`ade1d41d34b7` did.

## Why it is a pose reader and not the Far Cry 2 bridge

`far-cry-2-vr`'s `vr_bridge.c` was the model for the OpenVR plumbing — which exports to
resolve, where `openvr_api.dll` lives, the `FnTable:` interface string, the matrix layout —
and that saved most of the work. But it was **not** ported wholesale, and the two differences
are deliberate `[inferred-static 2026-09-10]`:

1. **It initialises as `VRApplication_Background`, not `_Scene`.** Background takes no scene
   ownership and will not start SteamVR: it fails cleanly with `Init_NoServerForBackgroundApp`
   when the runtime is not already up, which is exactly what a dev PC with no headset should
   do.
2. **It polls `IVRSystem::GetDeviceToAbsoluteTrackingPose`, not
   `IVRCompositor::WaitGetPoses`.** `WaitGetPoses` **blocks** the calling thread to pace it to
   the headset and is only legitimate for the scene application. Calling it from Alice's
   `Present` would throttle the whole game to the headset's cadence for no benefit, because
   Alice submits no frames. The pose call returns immediately.

Alice also needs none of the bridge's D3D11 device, backbuffer readback or compositor
submission, so none of it was taken. The result is 250 lines rather than 421, with no D3D11
dependency at all.

**Nothing is linked against OpenVR.** `openvr_capi.h` is Valve's header-only flat C API,
vendored under `third_party/openvr/` exactly as Far Cry 2 vendors it, and the runtime DLL is
resolved with `LoadLibrary`. The built proxy's imports are still system DLLs only — `ADVAPI32`
is the only addition, for the registry read that finds the SteamVR install
`[compile-verified 2026-09-10]`.

## The handedness trap, and why this conversion has almost no signs to get wrong

The row warned that handedness is where the silent sign error lives: OpenVR is right-handed,
Y-up, looking down −Z; UE3 is neither. The obvious approach — permute and negate components to
cross between the spaces — is three independent sign decisions, each invisible until someone is
wearing the headset.

**So it does not do that.** At re-centre it stores the head's position *and the basis the
player was facing*. Each frame it projects the world-space delta onto that basis:

```
d = pos − origin.pos
right   =  dot(d, origin.right) × scale
up      =  dot(d, origin.up)    × scale
forward = −dot(d, origin.back)  × scale
```

A dot product of two vectors in one consistent space is a plain number, so the three outputs
are handedness-free by construction. **Exactly one sign is chosen by hand — `forward = −back`
— and it has its own test.** Alice's own sign convention for the three outputs is already
known good from this morning: positive right slid the picture left, positive up moved it down,
positive forward walked the camera toward the character's head.

**33 numeric checks, 0 failures**, linking the shipped `vr_pose.c` rather than a transcription
`[verified-numerically 2026-09-10, n=33]`. They cover the matrix column layout (with an
asymmetric matrix, so a transposed read fails), the zero cases, each axis alone, both signs of
forward, a re-centre taken at 90° to the world axes, scale linearity, and the scale clamp.

## ⚠️ The scale is a guess, and here is how to measure it

`50.0` game units per metre is `[hypothesis]`, not a measurement. It is UE3's usual convention
(1 unit = 2 cm), and it fits the one soft observation available: a forward offset of 200 units
walked the camera from its resting third-person boom to the back of Alice's head, and 200 units
at 2 cm is 4 m, an ordinary boom length.

**The game's own `DefaultGravityZ=-750.0` does not settle it**, and it is worth saying why,
because it looks like it should. Gravity conflates the unit scale with how snappy the designers
wanted jumping to feel. At 2 cm per unit that is 15 m/s², a perfectly normal platformer
over-gravity. A scale calibrated to real gravity instead would give 76 units per metre. Both
fit, so gravity is not evidence `[measured 2026-09-10, but not decisive]`.

**The measurement, one live session:** enter first person with `T`, then step the head offset
down on the UP axis until the view sits at floor level. That distance *is* eye height in game
units, and a standing human eye is about 1.6 m, so units-per-metre = N ÷ 1.6. Until then the
scale is a knob, tunable with the headset on.

## What is NOT established

- **That any of this works.** Nothing has been launched, and no headset has been connected.
  Every claim here is compile-verified or host-numeric.
- **That a Quest 3 over Virtual Desktop presents as a normal SteamVR HMD to a background app.**
  Expected, but unproven here.
- **That the offset is comfortable.** Positional tracking without *rotational* tracking is a
  half-VR camera: the player's head turns will not move the view, only their leaning will. That
  is the correct next increment, not a defect, but it will feel odd and it is the reason the
  next row after this is orientation.
- **The diagnostic that would show the derivation is wrong rather than the scale merely
  untuned:** if leaning right moves the camera left, or leaning forward pulls it back, the
  fault is in the sign convention and not in the scale — and the 33 checks say it would have to
  be in Alice's basis, not in this conversion.
