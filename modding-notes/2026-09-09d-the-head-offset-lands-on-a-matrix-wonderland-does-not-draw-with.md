# 2026-09-09d — the head offset applies to 78,358 draws and the picture does not move

*Session: `/lm alice-madness-returns-vr`, dev PC, one launch, fully autonomous — the **second live
TANDEM run**, joining a `/pd` reader's seat. Evidence:
`dev-archive/recon/2026-09-09d-head-offset-applies-but-nothing-moves/`.*

## The row, and the answer

The board asked: *does the head offset move the view?* — with four outcomes named in advance. The
result is the fourth one, **"large `applied` count, nothing moves"**, and this session can say a
good deal about why.

| | measured |
| --- | --- |
| `head=` after F4×4 | **−20.0** — exactly 5 units per press, as designed |
| `head=` after 8 more | **−60.0** |
| `applied=` | **2,668 → 7,018 → 78,358** draws patched |
| `refused=` | **0**, throughout |
| picture moved? | **no** — dx **0 px**, correlation **0.986** against the unedited frame |
| control: walking | dx −5 px, correlation **0.509** — a genuinely different scene |

`[verified-numerically 2026-09-09, n=1 launch]`

So the mechanism runs end to end — the key steps the offset, the offset reaches tens of thousands of
draws, nothing is refused — **and none of it reaches the screen.**

## ⭐ Why, most likely: the matrix being edited is not the one this level draws with

The census line in Wonderland reads:

```
p00 camera=1.000000 last=1.000000 range=[1.000000 .. 2.747477]
```

**`p00 camera` is 1.000000 — and it is also the bottom of the whole range.** In Whitechapel the same
field reads **1.428148** (hfov 70°) with a range bottoming at 0.002210. `[measured 2026-09-09]`

A `p00` of exactly 1.0 is an hfov of exactly 90°, which is possible but a suspiciously round number
for a game camera, and it is what the classifier picks in **every** Wonderland reading taken across
two sessions (1.010590, 1.000001, 1.000000). Editing that matrix changes nothing visible, which is
what you would expect if it is not the view-projection the level actually draws with.

⚠️ **This is a `[hypothesis]`, not a measurement.** What is measured is that the edit lands and the
picture does not move. "The classifier picks the wrong matrix in Wonderland" is the best explanation
on the evidence, and it makes a **testable prediction**: in **Whitechapel**, where `p00cam` is
1.4281 and where the stereo shear visibly slid the whole scene on 2026-09-04, the same F4/F5 should
move the view. **That single test decides between "the mechanism is broken" and "the mechanism works
but the camera is mis-identified in this level."** It is the next thing to run.

Note this is the *third* thing that splits London from Wonderland on this project, after the
first-person camera and the field-of-view readings. Whatever differs between them is now worth
naming in its own right.

## ⚠️ `pos=` DOES NOT REPORT THE CAMERA'S POSITION — do not read it as such

The row expected `pos=` to change as the player walks. It does not: Alice walked twenty paces, the
scene visibly changed, and `pos=` stayed `0.0,0.0,0.0`.

But `pos=` **does** change when the head offset is stepped — to `−11.4,−16.4` at `head=−20`, and to
`−34.1,−49.4` at `head=−60`. Those magnitudes are **exactly 20.0 and 60.0**. So

> **`pos=` is our own head offset expressed in world axes — not the camera's world position.**
> `[verified-numerically 2026-09-09]`

It therefore cannot be used as evidence that the camera was read at all, which is precisely what the
board row was trying to use it for.

## ⚠️ A hazard the row flagged as untested, now partly answered

The row warned "F1–F5 may collide with the game's own binds". `F4` and `F5` both stepped the offset
by **−5**, never +5 — so either both are bound to decrease, or one press is being lost. **Not
established which.** ⚠️ And **`F5` is the game's own QUICKSAVE**; it is in the shipped
`AliceInput.ini` and this project's dossier already lists F1–F9 as claimed. Pressing it eight times
may have written quicksaves. **Move the head-offset keys off F5 before the next run.**

## Also this session

- **The wrong-window bug is FIXED and verified**, from a `/pd` tandem inbox drop — the first real
  handoff the tandem workflow has produced. `find_window()` now checks the owning process as well as
  the title, `need_window()` names any impostor it refused, and a decoy test creates a real window
  titled `Alice: Madness Returns` owned by `python.exe`. **Four checks pass**, including the one that
  must still reproduce the original bug. `[verified-numerically 2026-09-09]`
- **The deployed build was checked properly.** `d3d9.dll` changed under this lane (713,728 →
  717,824 B) because a **solo** `/pd` deployed at 17:50 — 20 minutes *before* it took its tandem seat
  at 18:10, so no rule was broken. A rebuild from source is **md5-identical** to what is installed.
