# 2026-09-08b — camera control route 2 is LIVE

*Session: `/lm alice-madness-returns-vr`, dev PC, one launch, fully autonomous including the launch.*

**Camera control on Alice is solved.** Numpad keys bound to UE3 axes in `AliceInput.ini` drive yaw
and pitch. Route 1 (console) was dead; route 2 works on the first try.

## The binds

Added to the live `AliceInput.ini` while the game was closed (backup:
`AliceInput.ini.bak-2026-09-08-pre-axis-binds`):

```
NumPadFour  / NumPadSix    Axis aTurn    Speed=-/+200.0 AbsoluteAxis=100
NumPadSeven / NumPadNine   Axis aBaseX   Speed=-/+200.0 AbsoluteAxis=100
NumPadTwo   / NumPadEight  Axis aLookUp  Speed=-/+25.0  AbsoluteAxis=100
```

Three axes were bound rather than one so a single launch could tell them apart — the board row named
`aTurn`, but the game's own `TurnLeft`/`TurnRight` binds use `aBaseX`, and there was no reason to
guess.

## The result — all three work

Mean absolute luma delta, 15 presses each, against a no-input control taken the same way
`[verified-live 2026-09-08, n=1 launch]`:

| key | axis | delta |
| --- | --- | --- |
| — | **no-input control** | **0.28** |
| `NumPadSix` | `Axis aTurn` | **14.96** |
| `NumPadNine` | `Axis aBaseX` | **9.81** |
| `NumPadEight` | `Axis aLookUp` | **15.84** |

All three are 35–56× the control. And by eye it is unmistakable: the camera rotated roughly 90° and
pitched down, from facing the Whitechapel Market arch to looking at Alice side-on against a gate
(`dev-archive/recon/2026-09-08b-camera-route-2-is-live/side-by-side.png`).

⚠️ **The scancode detail that makes this work:** numpad keys share their scancodes with the
arrow/navigation cluster and are told apart *only* by the extended flag being **absent** — the same
trap the toolkit records in the other direction (arrows *need* the flag). `NumPadSix` is `0x4D`
without the flag; `0x4D` *with* it is `Right`. Nothing errors either way.

## ⚠️ What is NOT established: the turn rate

I tried to calibrate degrees-per-press by turning in batches of 10 and looking for the frame to come
back round to the start. **It did not work and the result is discarded.** Deltas against the start
frame across 10–100 presses ran 12.75–24.02 with no clean minimum — 80 presses (12.75) is not
meaningfully different from 60 (13.08) or 100 (14.45). A "4.5° per press" figure falls out of taking
80 as the answer, and **it is not supported**; I am recording it only so nobody re-derives it from
the same numbers and believes it.

Two plausible reasons, not separated: the third-person camera re-centres behind Alice, so a pure yaw
sweep never happens; or the earlier pitch input left the view unable to match the start frame at any
yaw.

**The right instrument is the proxy, not the screen.** It already reads the ViewProjection every
frame (that is where the VP diagnostic came from), so a hotkey that logs yaw out of the VP matrix
would make camera aim quantitative and self-verifying. That is a `[PD]` change and it is the natural
follow-on.

## Automation — five capabilities

| capability | status |
| --- | --- |
| 1. self-launch | ✅ **first time on this game** — launched it myself, no prompt |
| 2. menu → gameplay | ✅ Enter ×4 → profile → CONTINUE GAME → Whitechapel |
| 3. console / exec commands | ⛔️ not available on this build (2026-09-08 session) |
| 4. character + camera | ✅ **camera now proven** — all three axes; movement already proven |
| 5. self-close | ✅ graceful through the game's menus, both confirm dialogs verified |

Four of five. Only the console is missing, and it is missing because the build does not have one.

Evidence: `dev-archive/recon/2026-09-08b-camera-route-2-is-live/`.
