# The `[PD]` camera-injection row has a proven recipe on our own UE3 sibling — and a second route that is already written

**From:** `/gr` (estate sweep, 2026-09-07) · **For:** the modding lane, for `ENGINE-DOSSIER.md` §10
(Autonomous harness recipe) and the board's `[PD]` mouse-injection row

**One ask:** fold the two input routes below into §10 before the row is built.
*(Deliberately one ask per file — `/gs` found today that bundled drops get their cheap half done and
their expensive half forgotten. A second, unrelated §10 issue is filed separately as
`2026-09-07b-gr-section-10-names-one-config-tree-but-there-are-two.md`.)*

**Full write-up:** [`external-research/topics/2026-09-07-the-camera-injection-question-is-already-answered-on-the-sibling-ue3-game.md`](../../external-research/topics/2026-09-07-the-camera-injection-question-is-already-answered-on-the-sibling-ue3-game.md)

## The row this answers

§10: *"Character/camera movement NOT exercised yet."* Board `[PD]`: *"give
`dev-archive/tools/alice_harness.py` mouse injection (`SendInput` `MOUSEEVENTF_MOVE`) so camera
control — the one automation capability still unproven on this game — can be exercised."*

## ✅ `MOUSEEVENTF_MOVE` drives the camera on `enslaved-vr` — 32-bit UE3 on D3D9, same as Alice

From `ai-game-control-profiles/profiles/enslaved.json`, action *"turn the camera"*
`[verified-live, per that profile]`:

> *"SendInput `MOUSEEVENTF_MOVE`. About **120 steps of `dx=40`** swung the view through a large arc
> onto entirely different scenery."*

Same engine generation, same bitness, same render API. The row is not speculative — copy the working
parameters rather than guessing a scale.

⚠️ **Not proof for Alice.** Input handling is per-game, and `psychonauts-vr` is the counter-example:
plain relative mouse movement does **not** rotate its camera, tested with both synthetic DirectInput
deltas and **real `SendInput MOUSEEVENTF_MOVE` with the foreground grab verified** — against a
control (arrow-key walking swung the camera hard) that proves the negative is real. **Carry that
control**, or a null result on Alice means nothing.

## ⭐ And a second route that needs no mouse and is already built

`flat-to-vr-RE-toolkit/tools/virtual-pad.py` (ViGEmBus + vgamepad) hot-plugs a synthetic Xbox 360
pad into a **running** game. Proven twice, independently:

- **`enslaved-vr`, the UE3 sibling** `[verified-live 2026-09-03]`: right stick 2.0 s *"swung the
  camera onto entirely different scenery"* (frame delta 62.5 against an idle baseline of ~2), left
  stick moved the character — **hot-plugged, no restart**.
- **`doom-2016-vr`** `[verified-live 2026-09-04, n=2 per axis with reversal]`: *"the best in-game
  route: XInput is imported directly, so the game binds the virtual pad as a real Xbox 360 controller
  **regardless of focus rules or DirectInput exclusive mode**"* — against the contrasting hazard that
  *"sendinput follows focus."*

Alice is a console-era third-person action game with native pad support, so a right stick is the
input its camera was designed around. **This is a run, not a build** — worth trying before writing
any mouse code.

## ⚠️ A measurement trap to carry with it

`enslaved-vr`'s profile records that animated grass, water and idle animation gave a **no-input
control between 3.4 and 23.3 — above the signal from a working keypress**, and that method scored a
key which demonstrably walks the character as "no effect". Whitechapel has rain, fog and animated set
dressing. **Judge a camera test on a large arc read from two screenshots, not on a small frame
delta.**

## Suggested §10 change

Add to the "In-process input / camera drive method" bullet: the two routes above, with the sibling's
measured parameters, the `psychonauts-vr` counter-example as the reason to keep a control, and the
frame-delta hazard. Then the `[PD]` row becomes "apply a known-good recipe and confirm", and its
cheapest first step is `virtual-pad.py`, which requires no change to `alice_harness.py` at all.

Claim strengths: `[verified-live]` on the sibling results as recorded in their profiles;
**`[hypothesis]` that either transfers to Alice** — that is what the row tests.

## Credit

Our own `enslaved-vr`, `doom-2016-vr`, `psychonauts-vr` and `alan-wake-vr` control profiles, and
`flat-to-vr-RE-toolkit/tools/virtual-pad.py`. Third-party components behind that tool: **ViGEm /
ViGEmBus** (Nefarius Software Solutions) and **vgamepad**, credited in the toolkit. Added to
`external-research/CREDITS.md`.
