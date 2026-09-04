# 2026-09-04 (`/lm`, dev PC, FULLY AUTONOMOUS) — first launch of the stereo proxy: interception is LIVE (outcome 2), the 3D STEREO menu row is present and toggles, but the F9 shear test is INCONCLUSIVE because the proxy's own diagnostics can't answer it yet

**First-ever run of the M0 stereo proxy against Alice.** The user launched it (after we set it
windowed — see below); Claude drove title → profile → CONTINUE → into Whitechapel, ran the F9
stereo test, checked the 3D STEREO video option, and quit through the game's own menu. Windowed
1280x720. Evidence: `dev-archive/recon/2026-09-04-first-launch-interception-and-stereo-test/`.

Build under test: deployed `d3d9.dll` 701,440 B (the 2026-09-03 M0 build), pass-through backup
beside it. `alice_vr_proxy_log.txt` PID=9200 session.

---

## 1. In plain words

The good news is clean: the proxy is really in the pipe. It wraps the device, sees 6,725 shaders,
and stays resident the whole session — so the interception foothold that the whole project depends
on is proven live, and the latent "reloaded past" bug a research sweep flagged this morning did
**not** bite here.

The stereo test itself did not give a clean answer, and I want to be honest about why rather than
call it a pass or a fail. Pressing F9 turned stereo on (the hotkey logged), but the image afterwards
differs from before only in the diffuse, low-level way a living scene differs from itself 1.5 s
later — Alice's idle sway, an NPC, ambient motion — not the coherent sideways slide a working shear
would produce. And the proxy's own counters can't adjudicate it, for three specific reasons I found
in the code (§3). So the delivery-path question is still open, and the next step is a cheap retest
that needs no rebuild (§4).

The third question — is the game's own "3D Stereo" video option actually there — is answered yes:
the row is present and toggles OFF↔ON freely (§5).

## 2. Interception is LIVE — outcome (2) `[verified-live 2026-09-04, n=1 launch]`

```
CreateDevice: adapter=0 type=1 flags=0x142 windowed=1 1280x720
  -> wrapped device 174A86D0 (real 1C3DC1A0). Stereo is OFF; F9 toggles...
shaders registered=6725 (registry full events=0), vp writes=0, draws given the fix texture=0
```

Wrapped device, 6,725 shaders registered, and Present/hotkey activity throughout — the status
board's outcome (2), "interception works, go on to (3)." **No reload-past signature**: the proxy
loaded once and stayed; the ~100 ms load-call-unload-silence pattern the `/sr` inbox drop warned
about did not occur, through the whole session including menu/settings screens (which can Reset the
device — the proxy's Reset handler kept the registry and fix texture, as designed). So on Alice the
missing-`FreeLibrary` bug is latent, not live — consistent with the drop's own assessment.

## 3. The F9 shear test is INCONCLUSIVE, and here is exactly why

`HOTKEY F9: stereo ON (ipd=6.50 convergence=300.0 p00=NOT SEEN YET - shear stays 0)` — that line
looks like a negative, but it cannot be read as one, because the proxy's diagnostics are gated in
three ways that all conspire here:

1. **The one-shot stats line fired BEFORE F9.** `shaders registered=… vp writes=0` logs once when
   `>2000` shaders are seen — that happened at 15:43:20, four minutes before the F9 press at
   15:47:40. So its `vp writes=0` reflects the stereo-OFF state, not whether the game writes the
   view-projection.
2. **The `vp_writes` counter only counts while stereo is ENABLED.** In `device.cpp`, the
   `SetVertexShaderConstantF(start==0, count>=4)` block is guarded by `&& g_st.enabled`. With stereo
   off, the counter cannot move even if the game is writing register 0 every frame. So it can never
   tell us "does the game write c0 at all."
3. **The F9 log samples `p00` at the toggle instant.** `have_p00` is only set inside that same
   enabled-guarded block, on a subsequent write. At the instant F9 flips `enabled` true, no enabled
   frame has run yet, so `have_p00` is necessarily still false — the log line says "NOT SEEN YET"
   by construction, not by measurement.

And the frame comparison can't stand in for the counters: baseline vs. F9-on differ by mean 6.5 /
4.9 / 3.7 per channel across 85.7% of pixels `[measured 2026-09-04]`, but that is distributed
low-magnitude change with **no coherent horizontal displacement** — the fingerprint of scene
animation over 1.5 s, not a shear. (A ~1% horizontal shear on 1280 px would be a ~13 px slide,
edge-concentrated, mean diff far above 6.) By eye the two frames read as the same composition.

**So: not confirmed, not ruled out.** The vertex-c0 delivery assumption the M0 proxy is built on
(dossier §6, "UE3 delivers ViewProjectionMatrix as StartRegister 0, 4 vec4s") is neither validated
nor disproved by this run. The standing rule applies — a negative is only evidence if the test
could have produced a positive, and this test's instrumentation could not.

## 4. The cheap retest that settles it — NO rebuild `[FLAT]`

The F9 log prints `p00` status every time F9 is toggled. So enable it, let enabled frames run, then
re-sample:

```
F9 (on) → wait ~2 s of gameplay → F9 (off) → F9 (on) → read the SECOND "stereo ON" log line
```

The second `stereo ON` line prints `have_p00` *after* enabled frames have run. If it says
`p00=known`, then the game **does** write vertex c0 with a perspective matrix, the recovery works,
and the open question becomes shear magnitude/visibility (saturate `ipd`/convergence and look
again). If it still says `NOT SEEN YET`, then vertex c0 carries no perspective view-projection
while enabled, and the delivery path is elsewhere — the dossier's own note that the view-projection
sits at **pixel-shader c4** in 4,122 shaders is then the lead to follow.

## 5. The game's "3D STEREO" video option IS present and toggles `[verified-live 2026-09-04, n=1]`

Configuration → VIDEO lists: GAMMA, RESOLUTION (1280x720), ANTI-ALIAS, **3D STEREO (OFF)**, MOTION
BLUR, POST PROCESS, DYNAMIC SHADOWS. The 3D STEREO row is present and the left/right arrows toggle
it OFF↔ON freely (I set it ON, confirmed by screenshot, then back to OFF and discarded on exit — no
CONFIRM, so the native path was never actually engaged). This answers the second open row's first
branch: **the native 3D Vision option is exposed and selectable on this driver, not driver-hidden.**
Per the dossier this is the `ExecStereo3D` / `EnableStereo3D` path — interesting as confirmation the
engine's stereo surface is live, but not a VR shortcut. Whether pressing CONFIRM actually engages
native 3D Vision on a modern driver is untested (deliberately — it risks a renderer mode switch and
is not the mod's route).

## 6. Getting it windowed (session prep)

The game launched fullscreen-exclusive first (`Fullscreen=True`), which BitBlt captures as black —
I could not see or drive it. Closed it with a graceful `WM_CLOSE` (not a force-kill; the menu was
not visible to use), then set `Fullscreen=False` in the live config
`Documents\My Games\Alice Madness Returns\AliceGame\Config\AliceEngine.ini` (backup
`.bak-2026-09-04-pre-windowed`) **while the game was closed** so UE3 would not overwrite it. The
relaunch came up windowed 1280x720 and everything after worked. Res is already 1280x720 in that ini.

## 7. Automation on Alice, scored (§5a)

1. **Menu → gameplay: proven** — title (Enter) → copyright (Enter) → PROFILE SELECT (Enter on the
   TEFA profile) → main menu → CONTINUE GAME → ~30 s load → into Whitechapel.
2. **Commands: proven (the F-key hotkey channel)** — F9 registered and logged; F7/F8/F10/F11/F12
   are the same mechanism. No console on this game.
3. **Character + camera: NOT exercised this session** — the stereo test needed a static scene, so I
   did not drive Alice's movement or camera. Unproven here; a future session should confirm it.
4. **Self-close: proven** — pause → MAIN MENU (confirm) → main menu → EXIT GAME (confirm YES).
   Process gone. Done gracefully through the game's own menu.

## 8. What is NOT established

- Whether the view-projection is delivered via vertex c0 at all (the whole M0 premise) — §3/§4.
- Whether, if it is, the shear is engaging but sub-visible at ipd 6.5 / convergence 300.
- Whether the pixel-c4 path (dossier §6) is the real delivery route.
- Character/camera drive on this game (not tried).
- Whether native 3D Vision (CONFIRM on the menu row) does anything on this driver (not tried).

## 9. Next

Live (`[FLAT]`, no rebuild): the F9 double-toggle retest (§4) to read post-enable `p00`. Static
(`[PD]`): ungate `vp_writes` from `g_st.enabled` and log `have_p00`/`vp_writes` continuously (or on
a dedicated hotkey) so the delivery-path question gets a clean read, add a saturating shear test
mode so any effect is unmistakable, and cross-check the pixel-c4 lead. Nothing needs the headset.
