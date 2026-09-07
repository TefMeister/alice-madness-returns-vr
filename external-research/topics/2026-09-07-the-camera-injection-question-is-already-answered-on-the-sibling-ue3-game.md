# The `[PD]` mouse-injection row is already answered — on our own UE3 sibling, and there is a second route that skips the question

**Status:** 🆕 new · **Priority:** high — it de-risks a `[PD]` row before it is built, and it offers a
second input route that is already written, already proven on this engine, and needs no mouse at all.

## Why this was looked up

The board's new `[PD]` row, added when the gate dropped FLAT → PD on 2026-09-07:

> "give `dev-archive/tools/alice_harness.py` mouse injection (`SendInput` `MOUSEEVENTF_MOVE`) so
> **camera control** — the one automation capability still unproven on this game — can be exercised,
> and so a better scene can be framed for the row above. The harness is keyboard-only today"

Dossier §10 agrees it is unexercised: *"Character/camera movement NOT exercised yet."* And this
project's control profile says the same in its own words: *"Camera control still unexercised — it
needs mouse injection and the harness is keyboard-only."*

**Before writing it, the obvious question: has any sibling project already measured whether
`MOUSEEVENTF_MOVE` reaches a UE3 game?** It has.

## ✅ 1. `SendInput MOUSEEVENTF_MOVE` drives the camera on our own UE3 sibling

**`enslaved-vr`** — *Enslaved: Odyssey to the West*, a **32-bit UE3 game on D3D9**, the same engine
generation, the same bitness and the same render API as Alice. From its control profile
`[verified-live, recorded in `ai-game-control-profiles/profiles/enslaved.json`]`:

> input API: *"Win32 SendInput (scancode keyboard **and relative mouse**)"*
> camera binding, action *"turn the camera"*: *"**SendInput `MOUSEEVENTF_MOVE`**. About 120 steps of
> `dx=40` swung the view through a large arc onto entirely different scenery."*

That is precisely the mechanism Alice's `[PD]` row proposes to build, exercised to a large,
unmistakable effect on the closest engine sibling in the estate. The row is not speculative work.

⚠️ **It is not proof for Alice**, because input handling is a per-game property and this estate has
already been burned assuming otherwise (see §3). It converts the row from *"try an unknown"* into
*"apply a known-good recipe and confirm"*, which is a different and much cheaper thing.

Two details from that profile worth copying with the mechanism:

- **Use scancodes, not virtual keys**, for the keyboard half — *"it keeps keyboard layout out of the
  path, which is the trap that cost a sibling project (`doom-2016-vr`) a session."*
  ⚠️ **But not blindly:** `alan-wake-vr` recorded the exact opposite on 2026-09-05 — scancodes did
  **not** reach that game while virtual-key events did, against a dev-PC record from the day before
  saying scancodes worked. `n=1` each way. **Try one, fall back to the other.**
- Alice's harness is **already driving menus with scancode `SendInput` successfully**
  `[verified-live 2026-09-04, re-verified 2026-09-07 — full menu→gameplay drive, character movement,
  all six proxy hotkeys and a graceful self-close, unassisted]`. So the transport is proven on this
  game; only the mouse half is untried.

## ⭐ 2. There is a second route that avoids the mouse question entirely — and it is already built

**A virtual XInput pad.** `flat-to-vr-RE-toolkit/tools/virtual-pad.py` (ViGEmBus + vgamepad) hot-plugs
a synthetic Xbox 360 controller into a *running* game. Two projects have proven it independently:

- **`enslaved-vr` — the UE3 sibling** `[verified-live 2026-09-03]`: *"a virtual X360 pad hot-plugged
  into the running game drives movement (left stick) and **camera (right stick)** with no restart."*
  Measured against an idle baseline of ~2: left stick full-forward 2.5 s moved the character (frame
  delta 48.9); **right stick 2.0 s swung the camera onto entirely different scenery (delta 62.5)**.
- **`doom-2016-vr`** `[verified-live 2026-09-04, n=2 per axis with reversal]` calls it *"the best
  in-game route: XInput is imported directly, so the game binds the virtual pad as a real Xbox 360
  controller **regardless of focus rules or DirectInput exclusive mode**."*

**Why this matters more than it looks for Alice specifically:**

- It **does not need the window to be foreground.** `doom-2016-vr` records the contrasting hazard:
  *"sendinput follows focus. The virtual XInput pad does NOT need focus, which is one reason it is
  the better in-game route."* Alice's harness must keep the window foreground for BitBlt capture
  anyway, but an input route that does not depend on focus removes a whole class of silent failure
  from unattended runs.
- **Alice is a console-era third-person action game with full native pad support**, so a right stick
  is the input its camera was actually designed around — arguably a *better* fit than mouse-look.
- **The tool already exists.** This is not a build; it is a run.

## ⚠️ 3. The cautionary sibling: mouse-look is NOT universal, and the estate has the scar

**`psychonauts-vr`** is the case that stops this being a blanket "just do it"
`[disproved, recorded in its control profile]`:

> *"UNRESOLVED and important. Plain relative mouse movement does NOT rotate the camera, tested
> carefully: (a) synthetic deltas injected at `IDirectInputDevice8::GetDeviceState` — no change;
> (b) **real `SendInput MOUSEEVENTF_MOVE` with the foreground grab VERIFIED — no change**;
> (c) control, walking with the arrow keys — the camera forward vector swung hard, proving the field
> is live, keyboard input arrives, and the camera responds to something."*

Note the shape of that test: **a control that could have produced a positive.** The negative is
trustworthy precisely because (c) proved the camera field was live and reachable at the time. Any
Alice mouse test should carry the same control, or a null result means nothing.

That case is also why this project's standing rule — build several input routes and measure which one
the game obeys against a no-input control — exists. **The recommendation here is therefore both
routes, not one:** wire `MOUSEEVENTF_MOVE` (cheap, the sibling says it works on UE3) *and* try
`virtual-pad.py` (free, already written, proven on the same engine).

## ⚠️ 4. And a measurement trap the sibling already paid for

`enslaved-vr`'s profile records a hazard that would bite the very row this unlocks — framing a scene
by screenshot delta:

> *"Animated grass, water and idle animation put a no-input control between 3.4 and 23.3, which is
> **ABOVE the signal from a working keypress**. That method scored a key which demonstrably walks the
> character as 'no effect'. Keep the no-input control — it is the right instinct — but prefer a large
> unmistakable action plus reading two screenshots. If a number is genuinely needed, camera motion is
> a coherent whole-frame change."*

Whitechapel has rain, moving fog and animated set dressing. **A camera test judged on a small frame
delta will produce a false negative there.** Swing the camera through a large arc — as the sibling
did, ~120 steps of `dx=40` — and read two screenshots.

## The concrete next steps this unlocks

1. **Try `virtual-pad.py` first.** It is written, proven on the same engine, needs no code in
   `alice_harness.py`, and does not depend on window focus. Right stick = camera.
2. **Then wire `MOUSEEVENTF_MOVE`** into the harness as the second route, copying the sibling's
   working parameters (~120 steps of `dx=40` for a large arc) rather than guessing a scale.
3. **Judge both against a no-input control, on a large arc, by two screenshots** — not by a small
   frame delta, for the reason in §4.
4. Whichever wins, record the verdict in
   `ai-game-control-profiles/profiles/alice-madness-returns.json`, whose camera entry currently reads
   "unexercised".

## Sources

All from our own account; no public source was needed for the findings above.

- `ai-game-control-profiles/profiles/enslaved.json` — the UE3 `MOUSEEVENTF_MOVE` result, the virtual
  XInput pad result, and the frame-delta hazard.
- `ai-game-control-profiles/profiles/doom-2016.json` — the virtual pad as the best in-game route, and
  the focus contrast.
- `ai-game-control-profiles/profiles/psychonauts.json` — the disproving case, with its control.
- `ai-game-control-profiles/profiles/alan-wake.json` — the scancode-vs-virtual-key reversal.
- `ai-game-control-profiles/profiles/alice-madness-returns.json` — this game's current state.
- `flat-to-vr-RE-toolkit/tools/virtual-pad.py` — the tool.
- `claude-memory/status/alice-madness-returns-vr.md`, OPEN block 2026-09-07 — the row this answers.
- **ViGEm / ViGEmBus** (Nefarius Software Solutions) and **vgamepad** — the third-party components
  `virtual-pad.py` builds on, credited in the toolkit.
