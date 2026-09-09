# 2026-09-09c — the built-in first person is gated by the LEVEL, and the HUD scene is now reachable

**⚠️ THIS IS A RECON DROP, NOT THE WRITE-UP.** A `/pd` held the lane claim on this project
throughout (`LIVE: /pd 2026-09-09 14:35`), so `ENGINE-DOSSIER.md`, `modding-notes/` and
`status/alice-madness-returns-vr.md` were deliberately **not** touched. Everything below still needs
folding into those three by whoever next holds the claim. Nothing here conflicts: this directory did
not exist before.

*Session: `/lm`-style live work, dev PC. The user drove Alice to a Wonderland combat encounter,
paused, and handed the machine over ("all yours"). Four launches were not needed — one live process
throughout.*

---

## 1. ⭐⭐ FIRST PERSON IS GATED BY THE LEVEL — it is a London-hub feature, not a combat question

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

### ⭐⭐ RESOLVED, AND NOT THE WAY IT LOOKED — IT IS THE LEVEL, NOT COMBAT

The confound was real for an hour: level, enemy, motion and low health all varied together. It was
then resolved by accident and confirmed deliberately. After the third death the checkpoint left
Alice **alive, idle, at full stop, with no enemy anywhere in the frame, still in Wonderland** — the
exact state the test needed.

**`T` was pressed four times in that state. Every one stayed in third person.**
`[verified-live 2026-09-09, n=4 presses, idle and enemy-free]`
(`07-T-idle-no-enemy-STILL-third-person.png`)

So:

| where | state | `T` |
| --- | --- | --- |
| Whitechapel (London hub) | idle, no enemies | **first person** ✅ |
| Wonderland | enemy engaged, moving | third person / close-follow ❌ |
| Wonderland | **idle, no enemy, full stop** | **third person** ❌ |

**⇒ The blocker is the LEVEL, not combat, not motion, and not an aggroed enemy.** Every one of those
was eliminated by the last row of that table. `[verified-live 2026-09-09, n=1 level each]`

### ⚠️ WHAT THIS MEANS FOR THE VR ROUTE — it is worse news than "combat blocks it"

The board row asked whether the built-in first-person camera "is the route". On this evidence it is
**not a way to play the game**: it appears to be a **London-hub sightseeing mode**, available where
there is nothing to fight and absent in the Wonderland levels that are most of the game. A VR mod
cannot be built on a camera that switches itself off for the actual gameplay.

⚠️ **NOT established, and each would change the conclusion:**

- **Why.** Per-level flag, gameplay-mode gating, or level scripting — untested. `[hypothesis]`
- **Whether it is really "London vs Wonderland"** or something narrower. `n=1 level on each side`;
  Whitechapel is one London area and this is one Wonderland area.
- **Whether the OTHER London areas allow it**, and whether any Wonderland area does.
- The `EnterFPS` variant (as against `EnterFPSByRS`) has never been reachable, since added binds are
  ignored — so it is unknown whether the plain command is gated the same way.

**The cheap next test** is one launch that reaches a second area on each side and presses `T` in
both — no combat needed, no risk to a save.

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
checkpoint reloads cleanly each time and no progress beyond the encounter was lost. **The third
death is what produced the answer**: continuing from it dropped Alice into an idle, enemy-free spot,
which is the state §1's test had needed all along and could not manufacture.

Not established:

- **WHY the level gates it** — per-level flag, gameplay-mode gating or level scripting. §1.
- **Whether the gate is really "London vs Wonderland"**, on `n=1` level each side. §1.
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
