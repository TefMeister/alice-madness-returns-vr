# WITHDRAWN: Alice has ONE config tree. `MonkeyGame` is Enslaved's, and my earlier drop repeated a half-correction

**From:** `/gr` (estate sweep, 2026-09-07, fourth drop) · **For:** the modding lane

Supersedes: my own `2026-09-07b-gr-section-10-names-one-config-tree-but-there-are-two.md` —
**entirely. Do not act on it.** If it has already been folded into `ENGINE-DOSSIER.md` §10, the text
it added needs removing again.

**One ask: ignore that drop, and leave §10's config path as it was.**

## What I got wrong

My earlier drop told you §10 was incomplete for naming
`Documents\My Games\Alice Madness Returns\AliceGame\Config\AliceEngine.ini` as *the* config path, and
asked you to record instead:

> "This game has **two config trees**, and which one is live **differs per machine**. Compare mtimes,
> and let the game tell you by rewriting one on exit."

**That is wrong, and §10 was right all along.**

## What is actually true

A `/lm enslaved` session the same day found the root cause, and the board now records it
`[verified-numerically 2026-09-07]`:

**"Monkey" is Ninja Theory's codename for *Enslaved: Odyssey to the West*.** Its install is
`Enslaved\MonkeyGame\`, and `Documents\My Games\UnrealEngine3\MonkeyGame\` is **Enslaved's** user
config tree. That tree's `MonkeyEngine.ini` carries `EditPackages=NTEngine`,
`EditPackages=NTGameFramework` and `EditPackagesOutPath=..\..\MonkeyGame\Script`, with **zero** Alice
references.

So there are not two *Alice* trees. There is **one** Alice tree — `AliceGame` — and a second tree
belonging to **a different game that also happens to be installed**. On the dev PC both directories
exist because both games are installed there; on the home PC the situation differed for the same
mundane reason. "Which one is live differs per machine" was pattern-matching on an artefact.

## How the error propagated, since that is the useful part

Three steps, each reasonable in isolation:

1. **2026-09-05** — a session reasoned *"UE3 names its config after the script package, and this
   game's is `Monkey`"* and concluded Alice's file is `MonkeyEngine.ini`. The general rule is correct;
   the package attribution was not.
2. **2026-09-07 (dev PC)** — a session found `AliceEngine.ini` alive on that machine and *partially*
   corrected it to "two trees, varies per machine". Better, but it kept the false premise that
   `MonkeyGame` was Alice's.
3. **2026-09-07 (me)** — I read step 2, treated it as settled, and filed a drop asking you to write
   that framing into the dossier. **I did not check whether `MonkeyGame` was Alice's at all**, which
   one grep of that tree's `EditPackages` lines would have shown.

The lesson worth keeping is narrow and mine: **a correction is not automatically the truth.** Step 2
corrected a real error and was itself still wrong, and I propagated it because it was the most recent
thing on the board. When a drop's whole content is "the record is incomplete", the premise deserves
the same check as a fresh claim would get.

⚠️ **The cost was real, and it was not mine:** acting on the 2026-09-05 version, a home-PC `/pd`
session set `Fullscreen=False` in `MonkeyEngine.ini` believing it was configuring Alice — **it edited
Enslaved's engine ini** (backed up as `MonkeyEngine.ini.bak-2026-09-05-pre-pd`). Harmless in effect,
but **Alice never received its windowed fix on the home PC**. The board carries the remedy; nothing
for this drop to add.

## What survives from the withdrawn drop

Only the cosmetic footnote, which is unaffected: §10 renders a log path as
`Binaries\Win32lice_vr_proxy_log.txt` — a missing `\A`. Fix it if you are in the file anyway.

Everything else in that drop should be discarded, and **`AliceGame\Config\AliceEngine.ini` stands as
§10 writes it.**

## Credit

`claude-memory/status/alice-madness-returns-vr.md`, the 2026-09-07 correction entry, and the
`/lm enslaved` session that found it. No public source involved.
