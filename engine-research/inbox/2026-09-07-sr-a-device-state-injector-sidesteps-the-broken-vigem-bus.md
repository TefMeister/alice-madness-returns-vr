# The broken ViGEm bus need not block the input row — a sibling proved a route today that uses no Windows input at all

**From:** `/sr`, 2026-09-07 (fourth sweep) · **For:** the modding lane. Nothing run; this is a pointer
to a sibling project's live result on the same graphics API, plus the one cheap check that decides
whether it applies here.

## The row this is aimed at

Your lane recorded today that *"the virtual-pad route cannot be tested on the dev PC — its ViGEm bus is
broken"*. That blocks one route. **It does not block the row**, because
`prince-of-persia-2008-vr` demonstrated a different one live this afternoon that needs neither ViGEm,
nor a gamepad, nor Windows to deliver anything.

## What was proved next door `[verified-live 2026-09-07, n=1 session]`

That project found **no** Windows route reached its game:

- `SendInput` **scancodes**, with the game foreground, its DirectInput keyboard acquired
  `NONEXCLUSIVE`, polled at ~200 Hz, a key held **22 seconds** across four logged samples — the game
  read `keys currently down: 0` throughout.
- Posted messages were excluded **by construction** from the import table (see below).

So it stopped fighting the input stack and **wrote into the buffer the game asks for**: the
device-state call was already hooked, so after the real call returns and before the game sees the
buffer, the proxy ORs in a state block the harness writes from outside through shared memory.

It works, confirmed four independent ways: an `applied` counter (355 in six seconds of one held key);
the game's **own** instrumentation flipping `0` → `1` keys down; **by eye**, two injected taps moving a
menu highlight exactly two rows; and a frame-difference of **24.08** against a **0.00–0.23** no-input
baseline on the same scene.

**Three implementation rules that were load-bearing, so they are worth inheriting rather than
rediscovering:**

1. **OR, never assign** — a key Tefa is physically holding must never be cleared by the injector.
2. **Apply a relative mouse delta exactly once per write** — a delta left standing is re-added at the
   poll rate and spins the camera forever. Buttons are a *level*; motion is an *event*.
3. **Cover every struct flavour** the game might ask for; a game that asks for the one you did not
   implement gets nothing, silently.

## ⚠️ Whether it applies here is one check, and this drop does not assume the answer

The technique hooks **the API the game actually reads input through**. Your dossier records the
`GetAsyncKeyState` polling in **our own proxy's hotkey handler** — it does not record what the *game*
uses. So the deciding observation, before any code:

**Read `AliceMadnessReturns.exe`'s import table** for `DirectInput8Create`, the XInput exports,
`GetAsyncKeyState` / `GetKeyboardState` / `GetKeyState`, raw input (`RegisterRawInputDevices`,
`GetRawInputData`), and `GetMessageA` / `PeekMessageA` / `ToAscii`. Three outcomes, three different
next steps:

| what the imports say | what it means here |
| --- | --- |
| **DirectInput8 and/or XInput**, and no message-based key reads | the sibling's route ports almost directly — hook the device-state call in the `d3d9.dll` proxy you already have deployed |
| **`GetAsyncKeyState` / `GetKeyboardState`** | different hook, same idea: intercept the state query the game makes. Simpler than the sibling's case, not harder |
| **raw input or message-based only** | the injector idea still applies but at a different seam, and `SendInput` may well work here where it did not there — worth one direct test first |

You already have the vector that makes any of these cheap: a **working `d3d9.dll` proxy**, live-verified
2026-08-25, in the same slot the sibling used.

⚠️ **And do not read the sibling's negative as a general fact.** *"`SendInput` does not reach
DirectInput"* was measured on **one 2008 console port** and its cause is undetermined — four candidate
explanations are recorded in the library entry, none of them tested. It is a reason to have a fallback
ready, not a reason to skip trying the cheap route on this game.

## One more thing from that session, which is about test design rather than input

The sibling's **first** injection test had been run at the **title screen — the one place in that game
that polls no input at all**, which its own device-hook log later showed. Every negative from it was
worthless: the test could not have gone positive. **Before trusting an input negative here, confirm
Alice is actually reading input at that moment.** A console-port menu waiting on a gamepad is exactly
the shape that produces this.

## Where the curated version lives

`flat-to-vr-cross-engine-research/docs/techniques/README.md`:
- "⭐⭐ And when no OS route reaches the game: write into the buffer the game asks for"
- "❌ Correction, 2026-09-07: a controlled test contradicts the rule above, and the reason is undetermined"
- "Read the import table before you design the input layer" (pre-existing)

Primary evidence: `prince-of-persia-2008-vr/modding-notes/2026-09-07d-…` and
`dev-archive/recon/2026-09-07-input-injector/`.
