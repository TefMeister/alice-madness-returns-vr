# 2026-09-10e — the first headset run: head tracking is live, position and rotation

Home PC `RTX`, headset on (Quest 3 over Virtual Desktop, SteamVR), Tefa driving, one launch.
Build `648a44e15b47` (727,040 B), rebuilt on this machine from `staging/` earlier the same
evening and byte-identical to the dev PC's.

## What Tefa saw

> *"it was like looking around in vr, like roomscale movement was there as well"*

Both halves at once: leaning moved the camera, turning the head turned the view, and neither
was mirrored. `[verified-live 2026-09-10, n=1]`

## What the log says (`alice_vr_proxy_log.txt`, 21:52–21:57)

| time | line |
| --- | --- |
| 21:52:36.360 | `vr: openvr_api.dll loaded from the SteamVR install` — nothing was copied into the game folder; the registry route works |
| 21:52:39.584 | `vr: HEAD TRACKING IS LIVE (IVRSystem_026, background app, standing origin)` — 3.2 s after the device wrap |
| 21:52:39.585 | `vr: RE-CENTRED on the head's current position (origin 0.073,0.834,-0.135 m)` |
| 21:56:15–18 | `NumPad+` ×4 (scale 50 → 62.5 → 78.1 → 97.7 → 122.1), then `NumPad-` ×4 back to 50.0 |
| 21:57:08 | last camtrace: `headrot=on applied=201427 refused=0` |

`refused=0` over ~200k frames means the rotation built from the two orthonormal triples was
never rejected by the orthonormality check — the handedness worry in 2026-09-10d stays a
non-event in practice, not just on paper.

Stereo stayed OFF for this run. This was the tracking test the row asked for, nothing more.

## What it changes on the board

- The ⭐⭐⭐ `[VR]` row is closed.
- The `[PD]` "make position and rotation separately switchable — only if the first headset
  session needs it" row is closed: it did not.
- The unit-scale row stays open. Tefa left the scale on 50.0 after sweeping to 122.1 and back,
  which is a feel judgement `[reported 2026-09-10, n=1]`, not a measurement.

## Next for this project

Stereo through the headset is a different question (this proxy renders side-by-side on the
monitor); the tracking half is done. The remaining rows are all flat-screen measurements.
