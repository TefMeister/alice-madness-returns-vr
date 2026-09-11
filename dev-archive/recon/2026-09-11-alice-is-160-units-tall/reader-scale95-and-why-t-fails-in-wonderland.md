# Scale 95 is in the build, and why T gives no first person in Wonderland

Supersedes: 2026-09-11-mod-reader-coherent-view-built.md §"The build" (the `build-coherent-2026-09-11`
folder and hash `f205dffa…` are replaced by the build below, which contains the same coherent-view
change plus the scale change).

From: `/lm` reader helper (dev PC), 2026-09-11. Static only: no launch, nothing deployed, no git.

## 1. The head-tracking scale default is now 95.0 units per metre

- **Where:** `staging/alice-madness-returns-vr/proxy-d3d9/src/vr_pose.c` **line 33**,
  `static float g_scale = 95.0f;` (was `50.0f`). The comment under it now records both routes to the
  number; the old 50.0 reasoning is kept below it. The "HEAD TRACKING IS LIVE" log line no longer
  says "NOT measured". NumPad+ / NumPad− with a tracker live are unchanged (×1.25 / ×0.8, clamped 1…1000).
- **Why 95:** live, Alice is ~160 units crown to sole (159.0 and 160.9) `[verified-live 2026-09-11, n=2]`
  (the main session's measurement); statically, cylinder 158 and eye bones 152.6 `[measured 2026-09-11]`.
  A ~1.65–1.70 m woman at ~160 units is 94–97 units/m `[inferred-static]`.
- **Test:** `vr_pose_test.c` gains `shipped default is 95 uu/m`, read before any setter runs:
  **64 checks, 0 failures** (was 63). Coherent view 59/59, stereo, disparity 23/23 and the shadermap
  corpus check (incl. CameraPosition 1,989) all still pass `[verified-numerically 2026-09-11]`.

**The build** `[compile-verified 2026-09-11]`:

| | |
|---|---|
| file | `staging/alice-madness-returns-vr/proxy-d3d9/build-2026-09-11-scale95/d3d9.dll` |
| size | 730,624 B |
| SHA-256 | **`380329e876bc8aaee04dd8c066f89d7fc690ac617b0cbdd082c18b8094ee98ad`** |
| reproducible | two builds in different folders byte-identical; no warnings; exports and imports unchanged |
| contains | scale 95 (active by default whenever a headset is live) + the coherent view (OFF unless `alice_vr_coherent_on.txt` sits next to the exe) |
| rebuild | `OUT=build-2026-09-11-scale95 ./build.sh` |

On a machine with no headset this build behaves exactly like the installed `648a44e15b47`: the scale
is only read by the tracker, and the coherent view is off `[inferred-static]`.

## 2. Why `T` does not give first person in Wonderland — it is not a first-person key there

Read from `AlicePlayerController`'s own bytecode in `AliceGame.u` (a scratch lister; nothing copied)
`[measured 2026-09-11]` for the code, `[inferred-static]` for what it means in play.

`T` → `EnterFPSByRS` → `EnterFPS`:

```
EnterFPSByRS:  if bCinematicMode: return;  LockOnModeDeactivated();  EnterFPS()
EnterFPS:
  if (!Pawn.bInLondon) {                       // anywhere that is not London
      if (!IsAnyAvailableRangeWeapon()) return;       // needs a WeaponForAliceRange in the inventory
      if (Pawn.IsInShadowMode()) { SwitchCameraZoom(); return; }
      if (!CanFire() || Pawn.bInGiantMode) return;
  }
  if (!bFirstPersonViewActive) ActivateFirstPersonView(); else QuitFPS();
ActivateFirstPersonView:
  Wonderland: if (!CanFirstPersonView()) return;  ... aiming pitch limits, GotoState('FirstPersonView'),
              crosshair + reticule, lock-on UI
  London:     GotoState('FirstPersonView'); Pawn.EnableForceTranslucency(true, 0, 0.5, 1000, false)
```

`CanFirstPersonView` also needs `bCanCombat && bCanAiming`, no cinematic input lock, not talking /
on a jump pad / turning / in special moves 41, 52, 66, state `PlayerWalking` with walking physics,
not lock-on targeting, and not a non-gameplay camera.

**So in Wonderland, `T` is the RANGED-WEAPON AIM mode.** With no ranged weapon (Pepper Grinder /
Teapot Cannon, class `WeaponForAliceRange`) it returns at the first test; only the key's second half,
`OnRelease ToggleCloseFollowCamera`, fires — the camera pull-in seen on 2026-09-09c. The Wonderland
archetype also starts with `bCanAiming = false` (London too; the class default is true), so something
at runtime has to enable aiming as well.

**And even with a ranged weapon it would not be first person.** Wonderland's `FPSCamera` is an
over-the-shoulder aim camera: `Distance 100` (max 125), `Offset (−50, 70, 0)`, FOV 75, pitched about
−5°. London's is `Distance 0`, FOV 65, and London additionally makes Alice's mesh translucent — the
only true first person in the game. `bInLondon` is in no archetype; it is set at runtime
(`ChangeAliceEnvironment(bInLondon)`).

This explains the dossier's 2026-09-09c "gated by the level" result, and supports the conclusion there:
the game's own first person cannot carry the VR mod. First person has to come from the matrices, as
planned.

**For measurements:** anything that needs the game's first person must be done in London.
