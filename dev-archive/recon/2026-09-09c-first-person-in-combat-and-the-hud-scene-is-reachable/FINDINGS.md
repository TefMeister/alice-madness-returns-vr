# 2026-09-09c — first person in combat, and the HUD scene is now reachable

**⚠️ THIS IS A RECON DROP, NOT THE WRITE-UP.** A `/pd` held the lane claim on this project
throughout (`LIVE: /pd 2026-09-09 14:35`), so `ENGINE-DOSSIER.md`, `modding-notes/` and
`status/alice-madness-returns-vr.md` were deliberately **not** touched. Everything below still needs
folding into those three by whoever next holds the claim. Nothing here conflicts: this directory did
not exist before.

*Session: `/lm`-style live work, dev PC. The user drove Alice to a Wonderland combat encounter,
paused, and handed the machine over ("all yours"). Four launches were not needed — one live process
throughout.*

---

## 1. ⭐⭐ FIRST PERSON DID NOT ENGAGE IN COMBAT — four presses, three checkpoints

`T` never produced first person while an enemy was alive and aggroed. What it produced instead was
the **close-follow camera** (`04-T-gives-CLOSE-FOLLOW-not-first-person.png`): the camera pulls in
tight behind Alice, and she stays on screen.

That is exactly what the bind predicts. `AliceControlLayout.ini` has:

```
KeyBindArray1=(Name="T",Command="EnterFPSByRS | OnRelease ToggleCloseFollowCamera")
```

**Two actions on one key.** When `EnterFPSByRS` is refused, the `OnRelease ToggleCloseFollowCamera`
half still fires — so the key always *does something*, and "it did something" must not be read as
"first person engaged". `[verified-live 2026-09-09, n=4 presses across 3 checkpoint attempts]`

### ⚠️ THE CONFOUND, AND IT IS NOT RESOLVED

**It is NOT established that COMBAT is the blocker.** Every press in this session happened with all
of the following true at once, and none was ever varied independently:

| | state during every test |
| --- | --- |
| level | Wonderland (Whitechapel was where first person worked) |
| enemy | alive and pursuing, every single time |
| Alice | moving, fighting, or being hit — never idle |
| health | low after the first death |

So "combat blocks it", "this level blocks it", "an aggroed enemy blocks it" and "you must be idle"
all fit the evidence equally. `[hypothesis]`

**The user's own description points at the last one** — they said first person is available *"when
standing still though"*. The one test that would separate these is cheap and was attempted and lost:
**reach an enemy-free spot in Wonderland, stand completely still, then press `T`.** Alice died before
that state could be held (see §4).

---

## 2. ⭐⭐ THE HUD SCENE THE OTHER ROW HAS BEEN WAITING FOR IS NOW REACHABLE

The `[FLAT]` "outcome 4's remaining half" row has been blocked with: *"this save is 0% / 00:02,
Whitechapel has no HUD ... budget a long autonomous drive into Wonderland, not a cheap probe."*

**That blocker is gone.** The user's live session sits at a Wonderland combat encounter with the HUD
fully present — rose health meter top-left, focus prompts, hit markers, dodge effects
(`03-checkpoint-enemy-and-HUD.png`, `05-hud-rose-health-and-dodge.png`). The checkpoint reloads
straight back into it.

⚠️ **The save has NOT been captured, and this is time-limited.** The position lives in the running
process and its checkpoint; if the game is closed and reopened from the profile, whether it returns
here has not been checked. **Next session should verify the checkpoint restores this area before
planning around it.**

---

## 3. ⚠️ TWO CORRECTIONS TO CLAIMS MADE EARLIER TODAY

Both were written this morning from Whitechapel data alone, and both are too strong.

**(a) `p00cam` is NOT a general first/third-person detector.** The dossier and control profile now
say "≈1.5697 first person, ≈1.4281 third person — a free state detector". Those two numbers are
**Whitechapel-specific**. Measured in Wonderland this session:

| where | `p00cam` | hfov |
| --- | --- | --- |
| Whitechapel, third person | 1.428148 | 70.0° |
| Whitechapel, first person | 1.569685 | 65.1° |
| Wonderland, paused in combat | 1.835283 | 57.3° |
| Wonderland, unpaused third person | 1.010590 | 89.4° |
| Wonderland, after `T` | 1.000001 | 90.0° |

`[measured 2026-09-09, n=1 launch]` **The camera's field of view is scene-dependent**, and a
Wonderland third-person reading (1.0106) is nowhere near the Whitechapel third-person one (1.4281).
Using the Whitechapel thresholds elsewhere would report "unknown state" at best and the wrong state
at worst. **Judge first person by eye — is Alice in the frame — and use `p00cam` only as a
within-scene relative signal.**

**(b) "Pitch is exactly 0.000 in third person, in every line" is wrong.** It read **−8.59°** in
Wonderland `[measured 2026-09-09]`. The Whitechapel follow camera happens to be level; the
third-person camera in general is not.

---

## 4. What was spent, and what was NOT established

**Alice died three times, all mine.** Once mashing attack without using the game's lock-on, once
retreating on `S` while being hit, once standing still on low health to run the idle test. The
checkpoint reloads cleanly each time and no progress beyond the encounter was lost, but the third
death cost the one measurement that would have resolved §1's confound.

Not established:

- **Whether combat, the level, motion, or an aggroed enemy is what blocks first person.** §1.
- **Whether the enemy can be beaten by this harness at all.** Focus (`CapsLock`) + attack + dodge
  (`LeftShift`) was tried for four cycles and lost. A harness that cannot win a basic fight cannot
  reach "after combat" states on its own.
- **Eye height in first person.** Still unmeasured, and still wants a pose dump the game does not
  expose.

## 5. New capability: the harness can click the mouse

`alice_harness.py` gained `click(button, count, hold, gap)` and a `click` CLI verb, same hold/gap
discipline as `press()`. It was keyboard-only before, which is why "does first person survive
combat?" had never been askable — Alice's attack is `LeftMouseButton`. Attacks land and produce hit
flashes `[verified-live 2026-09-09, n=1 session]`.
