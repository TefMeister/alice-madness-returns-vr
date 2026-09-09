# 2026-09-09c — the built-in first person is gated by the LEVEL, so it is not the VR route

*Live session on the dev PC. The user drove Alice to a Wonderland combat encounter, paused, and
handed the machine over. Full detail and evidence:
`dev-archive/recon/2026-09-09c-first-person-in-combat-and-the-hud-scene-is-reachable/FINDINGS.md`.*

## The answer to the board's ⭐⭐ row: no, it is not the route

| where | state | `T` |
| --- | --- | --- |
| Whitechapel (London hub) | idle, no enemies | **first person** ✅ |
| Wonderland | enemy engaged, moving | third person ❌ |
| Wonderland | **idle, no enemy, full stop** | **third person** ❌ |

`[verified-live 2026-09-09, n=4 presses in the idle enemy-free state]`

The last row is the one that matters. It was reached by accident — the third death dropped Alice
somewhere quiet — and it eliminates combat, motion and an aggroed enemy in a single measurement.
**The gate is the level.**

So the built-in camera reads as a **London-hub look-around mode**, absent from the Wonderland levels
that are most of the game. **A VR mod cannot be built on a camera that switches itself off for the
actual gameplay** — which is what the user had assumed all along, and it is the right assumption:
first person in VR will be built with what we have, not borrowed from the game.

⚠️ `n=1` level on each side. **NOT established:** why the gate exists, and whether the split is
really "London vs Wonderland" rather than something narrower. The cheap next test is one launch that
touches a second area on each side.

⚠️ **The `T` bind fires two actions** — `EnterFPSByRS | OnRelease ToggleCloseFollowCamera`. When
first person is refused, the close-follow half still fires and the camera visibly pulls in. **"The
key did something" is not "first person engaged."**

## Two corrections to claims made earlier the same day

Both were Whitechapel-only generalisations.

**`p00cam` is not a general first/third-person detector.** Whitechapel third person reads 1.428148
and first person 1.569685, but Wonderland third person reads **1.010590** — nowhere near either.
The camera's field of view is scene-dependent, so those thresholds only work within one scene.
Judge first person by eye: is Alice in the frame. `[measured 2026-09-09]`

**Third-person pitch is not always 0.** It read **−8.59°** in Wonderland. The Whitechapel follow
camera happens to be level; the camera in general is not. `[measured 2026-09-09]`

## What this session also produced

- **The harness can click the mouse** (`click()` plus a `click` verb). It was keyboard-only, which is
  why "does first person survive combat?" had never been askable — Alice's attack is
  `LeftMouseButton`. Attacks land and produce hit flashes `[verified-live 2026-09-09]`.
- **The HUD scene the other `[FLAT]` row has been waiting for is reachable.** The user's checkpoint
  sits in a Wonderland encounter with the rose health meter, focus prompts and hit markers on screen
  — the row was blocked on "this save is 0% / 00:02 and Whitechapel has no HUD". ⚠️ Not verified that
  a fresh launch returns to it; check before planning around it.
- **Alice died three times, all mine** — bad combat, not a game or harness defect. The harness lost a
  straightforward fight even using the game's own lock-on, so **it cannot yet reach "after combat"
  states under its own power.**
