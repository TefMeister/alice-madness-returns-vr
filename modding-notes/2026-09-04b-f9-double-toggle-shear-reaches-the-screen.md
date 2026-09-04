# 2026-09-04b (`/lm`, dev PC, FULLY AUTONOMOUS) — RESOLVED: the vertex-c0 stereo shear REACHES THE SCREEN (outcome 3)

**Supersedes the morning note's "inconclusive" (`2026-09-04-first-proxy-launch-interception-live-stereo-test-inconclusive.md`).** The morning run could not read the shear because the proxy's diagnostics were gated; a same-day F9 double-toggle plus a saturation test settled it as a clean positive.

## The double-toggle read `[verified-live 2026-09-04]`

Into Whitechapel, then `F9 on → wait ~3 s of gameplay → F9 off → F9 on`, reading the log:

```
[16:12:31] HOTKEY F9: stereo ON  (... p00=NOT SEEN YET - shear stays 0)   <- toggle-instant, before any enabled frame
[16:12:36] HOTKEY F9: stereo OFF (... p00=known)                          <- after enabled frames ran
[16:12:39] HOTKEY F9: stereo ON  (... p00=known)
```

So the game **does** write the view-projection to vertex-shader constant register 0 with a perspective matrix, and the proxy **does** recover `p00` while enabled. The morning `NOT SEEN YET` was a sampling artefact (the log samples `p00` at the instant of the toggle, before any enabled frame has run), not evidence the path is dead.

## The saturation test — the shear reaches the screen, proportional and reversible `[verified-live 2026-09-04, reversible]`

At the default ipd 6.5 / convergence 300 the shift is sub-visible. Saturating it made it unmistakable ("saturate first, then tune down"):

- ipd 6.5 → **26.5** (F12 ×20) and convergence 300 → **20.6** (F7 ×12): the **whole scene slid horizontally** — Alice went from centre to the far-left edge, the Whitechapel arch and sign shifted left, the iron gate came into frame on the right. `evidence: saturated-ipd26-conv20.jpg`
- Restoring ipd → 6.5 (F11 ×20) and convergence → 300 (F8 ×12): the image **recentred exactly** to the baseline composition. `evidence: restored-recentered.jpg` vs `baseline-stereo-off.jpg`

The shift scales up with the parameters and reverses cleanly, and it is **horizontal, not vertical** — so this is outcome (3) ("the whole image shifts sideways ⇒ the vertex shear reaches the screen"), and the math lane is correct (not outcome 5). Reversibility is the discrimination that scene animation cannot fake.

## What this establishes, and what it does NOT

**Established:** interception (outcome 2), `p00` recovery from vertex c0, and the shear reaching the screen as a proportional, reversible horizontal shift. The M0 core lever is proven on Alice.

**NOT established:**
- **Outcome 4** — whether the HUD, crosshair and screen-space passes (SSAO, post, and the pixel-shader `c4` view-projection the dossier §6 flags) FOLLOW the sheared geometry or tear away. Whitechapel is HUD-light and I did not scrutinise screen-space alignment at the huge IPD. This is the key remaining flat question and directly tests the dossier's "pixel shaders read an unsheared c4" concern. `[FLAT]`
- **Two eyes.** The M0 shifts a single view; real VR needs per-eye rendering (side-by-side or two-submit). `[PD]`
- Comfort / real stereo feel — headset. `[VR]`

## Notes for the next session

- ⚠️ **F12 is also Steam's screenshot key** — pressing it for ipd+ also fires a Steam screenshot (harmless; the proxy reads F12 via `GetAsyncKeyState` regardless). Consider remapping the proxy's ipd+ off F12 in a future build.
- The F9 double-toggle is the no-rebuild way to read `p00`; the `[PD]` hygiene fix (ungate `vp_writes`, continuous logging) would make it a single-launch read.
- Must be windowed (`AliceEngine.ini` `Fullscreen=False`, set while closed).

## Automation (§5a)

menu→gameplay ✅, F-key command channel ✅ (F7/F8/F9/F11/F12 all exercised and logged), character+camera not exercised (static test), self-close ✅ (pause → MAIN MENU → EXIT GAME, gracefully). Game closed; nothing left running.
