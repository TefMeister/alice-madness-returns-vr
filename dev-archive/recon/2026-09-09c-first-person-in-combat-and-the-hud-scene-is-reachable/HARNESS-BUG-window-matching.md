# ⚠️ The harness can grab the WRONG WINDOW — found 2026-09-09, NOT yet fixed

**Session parked on a usage limit before this could be fixed or tested. Fix it before the next
run drives anything.**

## What happened

`alice_harness.py find` returned, with the game running perfectly normally:

```
hwnd=0x9087E  title='ALICE madness return first person - Google Search - Google Chrome'
              client=(-31992, -32000, -31848, -31980)
```

It matched **the user's Chrome window**, because they had googled Alice's first-person mode.
`find_window()` matches `TITLE_SUBSTR = "Alice"` as a case-insensitive **substring of any visible
window title**, and the browser tab title contained "ALICE".

## Why it matters more than it looks

The very next thing a session does after `find` is `focus()` and then `press()`. **That would have
typed the menu-navigation keys into the user's browser** — and with `ENTER`, `DOWN` and `ESC` among
them, into whatever page they had open. Nothing would have errored; the game would simply have
"ignored the keyboard", which is the exact silent-failure signature the profile already warns about
for other causes.

The off-screen client rect (`-32000`) is the tell that it is a minimised window, and it is the only
reason this was noticed rather than acted on.

## The fix, not yet applied

Match the **process**, not the title. The game's window belongs to `AliceMadnessReturns.exe`, and
`GetWindowThreadProcessId` gives the owning PID for a candidate hwnd — filter on that. An exact
title match (`"Alice: Madness Returns"`) is a cheaper stopgap but still breaks the day a browser tab
is titled exactly that.

⚠️ Whatever is chosen, **verify it while a decoy window with a matching title is open**, or the test
proves nothing. That decoy is what exposed this.

## Scope

`TITLE_SUBSTR` substring matching is not Alice-specific — check the other games' harnesses and
`ai-game-control-profiles` entries for the same pattern. A game with a common word in its title
(`Doom`, `Unreal`, `Manhunt`) is exposed the same way.
