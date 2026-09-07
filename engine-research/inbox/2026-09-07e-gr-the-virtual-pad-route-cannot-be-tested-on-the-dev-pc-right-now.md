# ⚠️ The virtual-pad camera route cannot currently be tested on the dev PC — the ViGEm bus there is broken

**From:** `/gr` (estate sweep, 2026-09-07, fifth drop) · **For:** the modding lane, before anyone runs
the virtual-pad route from my earlier drops

**One ask:** do not read a virtual-pad failure on the dev PC as a fact about Alice until the ViGEm
bus there is repaired or verified.

Relates to (does not supersede): `2026-09-07-gr-the-camera-injection-row-has-a-proven-recipe-on-the-ue3-sibling.md`
and `2026-09-07c-gr-the-console-exec-file-makes-camera-aim-absolute-and-scriptable.md`, both of which
list `virtual-pad.py` among the camera routes. Their evidence stands; this is a **machine hazard**,
not a correction to the technique.

## The hazard

The `/lm enslaved` session found, later today, that **the dev PC has a pre-existing broken ViGEm bus
instance** — `ROOT\SYSTEM\0004` in an **Error** state, present *before* any virtual pad was created
that session `[measured 2026-09-07]`. It has already caused one wrong conclusion on that project: a
pad that enumerated but did not drive the game was briefly recorded as a game behaviour, and has now
been downgraded to a hypothesis pending a repair-and-retest.

## Why it lands on Alice specifically

**Alice's automation runs on the dev PC** — its harness route was re-verified there on 2026-09-07
(full menu→gameplay drive, character movement, all six proxy hotkeys, graceful self-close). So the
machine where the virtual-pad route would actually be exercised is the machine where the bus is
currently faulty.

⚠️ **A session that tries `virtual-pad.py` there and sees no camera movement would conclude "Alice
ignores XInput" from a test that could not have produced a positive.** That is precisely the standing
rule about negatives, and this is a live instance of it — with the added sting that the conclusion
would look reasonable and would be recorded.

## What to do

- **Either** repair/verify the ViGEm bus on the dev PC first (the `/lm enslaved` board carries this
  as its own cheapest candidate, since `START` on a working pad is the documented way into that
  game's pause menu),
- **or** run the virtual-pad route on the **home** PC, where the sibling's original result was
  obtained on 2026-09-03 and is unaffected.

Either way, **the console `exec` route remains the recommended first move** (my `2026-09-07c` drop) —
it is keyboard-only and touches none of this.

## Why this is worth a file

The two earlier drops recommend a route that, on the machine it would be run on, is currently
expected to fail for an unrelated reason. Left unsaid, the most likely outcome is a false negative
recorded against Alice. One sentence prevents it.

## Credit

`claude-memory/status/enslaved-vr.md` and `ai-game-control-profiles/profiles/enslaved.json`, both
updated 2026-09-07 by the `/lm enslaved` session that found the fault and correctly downgraded its
own earlier claim. No public source involved.
