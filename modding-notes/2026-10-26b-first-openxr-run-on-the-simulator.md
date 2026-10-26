# 2026-10-26b — First OpenXR run in the game, on the OpenXR Simulator: it works

`/lm`, dev PC, unattended (Tefa away), one background reader. Three launches; the game was closed through its own
window close each time. Evidence: `dev-archive/recon/2026-10-26-first-openxr-run-on-the-simulator/`.

## Result

The OpenXR output built this morning (`2026-10-26-alice-can-reach-an-openxr-headset.md`) works inside the game:

- `xr: session running`, picture format 21 (A8R8G8B8, the kind the handover takes), 1280x720 per eye, the first
  OpenXR pose taken as the origin `[verified-live 2026-10-26, n=2 launches]`.
- In the level (Whitechapel kitchen, from the save): **4,607 left+right pairs handed over, 0 failed, 0 dropped,
  0 not ready; 17,993 headset frames submitted with the pose they were drawn with** `[measured 2026-10-26, n=1 run]`.
- The simulator shows Alice in **both eyes**, and its stereo check says **PASS: 5 px of disparity, expected 2-30**
  `[measured 2026-10-26, n=1]`.
- **A head turn of 20° to the left turned the game's view to the left** (more of the room on the left, Alice moved
  right in the picture) `[verified-live 2026-10-26, n=1]`. `headrot=on applied=11025 refused=0`.

## What went wrong on the way (and what fixed it)

1. **The game started fullscreen.** `Fullscreen=True` was back in `AliceEngine.ini` (Documents, My Games), so the
   first launch switched the whole screen to 1280x720. It was set to `False` with the game closed (backup
   `AliceEngine.ini.bak-2026-10-26-was-fullscreen`); the next launches measured windowed on the 1920x1080 desktop.
   Who set it back to True is not known (UE3 rewrites its config on exit). The display-mode change cost 80 failed
   readbacks in one burst during the Reset that followed; none afterwards.
2. **The menu replay got lost at the profile screen, twice.** The simulator's preview window opens on top of the
   game window, so the screen the replay tool compared was half preview. Moving the preview window off the game
   fixed it; the route then ran from the profile screen into the level. Recorded in the route folder's `KNOWN.md`.
3. **One crash during the level load** (second launch): `AliceMadnessReturns.exe` + `0x00be0f63` and `0x00067d48`,
   `c0000005`, faulting module the exe. Both offsets are the intermittent level-load crash already seen on
   2026-09-09 and 2026-09-10, before any OpenXR code existed. The third launch loaded the level fine. Not caused by
   today's work as far as can be told `[hypothesis]` (n=1 crash in 2 level loads today).

## The reader (background helper)

Asked to check two assumptions of the new code against old logs. It found: no log ever recorded the back buffer
format (this run answered it: 21); 1280x720 in every launch; Reset only ever seen around a fullscreen launch (true
again today); and the square-pixel assumption for the headset angles holds in all 106 camera dumps (p11/p00 =
1.7778 = 1280/720) `[measured 2026-10-26]`. Its caveat: only 16:9 has ever been measured, so a 21:9 window might
break the height formula `[hypothesis]`; the window rule keeps it 1280x720 on both PCs.

## Not established

- Comfort, scale and whether the drawn angles look right: needs a person in a real headset.
- The half-rate pose (one eye per frame) has not been judged for jitter; the BeG0nE camera log of this run will
  say whether the camera is renewed at half the picture rate, which is expected.
- Motion blur and depth of field are still on in `AliceEngine.ini` (`MotionBlur=True`, `DepthOfField=True`); the
  VR rule wants them off in VR only. New `[PD]` row.

## State left behind

`alice_xr.ini` back to `enable=0` (an ordinary launch is unchanged), `Fullscreen=False` kept (windowed is the rule).
Installed files unchanged since the morning's record (`deployed.sh check`: all 4 match).
