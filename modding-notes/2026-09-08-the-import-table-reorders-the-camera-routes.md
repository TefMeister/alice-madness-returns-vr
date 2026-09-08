# The import table reorders the camera routes — and unblocks one of them

`/pd`, dev PC, 2026-09-08. **The game was not launched. Nothing in this note has been run.**

Tool: `dev-archive/tools/alice_harness.py`. Evidence: `llvm-objdump -p` on the shipped exe.

## The row said "add mouse injection". The inbox said not yet, and it was right

The board's `[PD]` row asked for `SendInput` `MOUSEEVENTF_MOVE` in the harness so camera control —
the one automation capability still unproven on this game — could be exercised.

Six `/gr` and `/sr` drops were sitting undrained in `engine-research/inbox/`, and one of them exists
specifically to answer that row: *"the `[PD]` row may not need a mouse at all"*, asking that two
cheaper, keyboard-only routes be recorded **before any mouse code is written**. Draining first is
what the lane rule is for, and here it changed the work.

⚠️ **Read the whole inbox before draining any of it** mattered concretely this time: one drop
(`2026-09-07b`) is **withdrawn in full** by a later one (`2026-09-07d`), and a third supersedes the
recommended order of a fourth. Draining oldest-first would have written a retracted claim about
"two config trees" into the dossier and only then met its withdrawal.

I corroborated the withdrawal rather than taking it on trust — one command:
`My Games\UnrealEngine3\MonkeyGame\Config\` has `EXEName=MonkeyGame.exe`, `MKAIPathbuildingScout`,
`ScriptPaths=..\..\MonkeyGame\Script` and **zero Alice references** across every file in the tree.
It is Enslaved's. §10's `AliceGame\Config\AliceEngine.ini` stands as written.
`[verified-numerically 2026-09-08]`

## What the import table settles

`AliceMadnessReturns.exe`, read directly `[verified-numerically 2026-09-08]`:

| imported | **not** imported |
| --- | --- |
| `DINPUT8.dll` → `DirectInput8Create` | `RegisterRawInputDevices` |
| `XINPUT1_3.dll` → **ordinals 2 and 3, by ordinal** | `GetRawInputData` |
| `USER32`: `GetKeyState`, `GetMessageW`, `PeekMessageW` | `GetAsyncKeyState` |
| `USER32`: `ClipCursor`, `GetClipCursor`, `GetCursorPos`, `SetCursorPos` | `GetKeyboardState` |

### 1. Raw Input is excluded by construction — so route 4 is worth trying

The `/gr` drop *inferred* Alice's mouse path was the Win32 cursor/message path, from the fact that
Wemino's MadnessPatch hooks `UpdateMouseLock` (which calls `ClipCursor`). The import table says it
outright: **no raw-input imports at all**, and four cursor APIs present. An injected
`MOUSEEVENTF_MOVE` moves the system cursor, so on this game it has a plausible way in — where on a
Raw-Input game it would not. The inference was right; it is now a measurement.

### 2. ⭐⭐ The virtual-pad route is **not** blocked, and the record saying so is about a different mechanism

Two drops warn that route cannot be tested on the dev PC because **its ViGEm bus is broken**
(`ROOT\SYSTEM\0004`, Error state, pre-existing). That is true — of a ViGEm **virtual device**.

It is irrelevant here. **Alice imports `XINPUT1_3.dll` by ordinal 2 and 3 — exactly the shape
`prince-of-persia-2008-vr` has** — so an `xinput1_3.dll` **proxy** fabricates a pad *inside the
process*. No bus, no driver, no ViGEm. That project's proxy already exists, loads, and pins its
ordinals in a `.def` precisely because its exe imports by ordinal too; POP even imports ordinal 4 as
well, so its `.def` is a superset of what Alice needs.

⚠️ **What is NOT established is whether Alice ever *polls* XInput.** POP's proxy loaded fine and that
game never called `XInputGetState` once. So this is a route that is **available**, not one known to
work — and the `/pd` session on POP earlier today built the instrument that answers exactly that
question, which would port with it.

**I did not build it this session.** The row asked for mouse injection; this is a different, larger
piece of work, and its value depends on a poll that has never been observed. It is queued as its own
`[PD]` row with the measurement attached, rather than started at the end of a session.

## What was built

`alice_harness.py` gains two of the four routes, ordered as the drop asked:

```
console CMD...        write the exec file and press the bound key   [route 1]
bugit                 shorthand for `console BugIt` - prints pose   [route 1]
bugitgo X Y Z P Y R   set location AND rotation absolutely          [route 1]
mouse DX DY [steps]   relative mouse move via SendInput             [route 4]
ballistics [pin]      report / pin pointer acceleration             [route 4 prereq]
```

**Route 1 is first because it is self-verifying.** `BugItGo` sets pose absolutely and `BugIt` prints
it back, so *"did the camera move?"* becomes a number rather than a screenshot judgement — which
also sidesteps the frame-delta hazard the sibling drop warned about in rainy Whitechapel.

### Two things I handled that the drops flagged as silent-failure traps

- **Pointer ballistics.** Windows can scale an injected relative delta by up to 4× depending on
  pointer settings, so a calibration is not portable. `ballistics` reports them and can pin them.
  **Measured on this dev PC: thresholds (6, 10), acceleration ON, speed 6/20** — so a `mouse` step
  size calibrated here would *not* reproduce elsewhere unless pinned first.
  `[measured 2026-09-08]`
- **UIPI.** If the game runs at higher integrity than the harness, `SendInput` fails *silently* —
  neither the return value nor `GetLastError` says so. `mouse` says this in its output and points at
  `bugit` as the read-back, because the only honest confirmation is a number from inside the game.

### Where the exec file goes is not settled, so it is written everywhere plausible

The drop said `Binaries\`. The exe actually lives in `Binaries\Win32\` — its working directory — and
UE3 builds are also documented reading exec files from `<Game>\Config`. Rather than guess and get a
silent no-op that cannot be told apart from "no cheat manager", the harness writes the same file to
**all four** candidates and prints which it managed. All four exist on this machine
`[verified-numerically 2026-09-08]`.

### A defect the first test run caught

My new warning lines contained `⚠️`, and Windows' console is cp1252: printing one raised
`UnicodeEncodeError` and **killed the harness after the input had already been sent** — the worst
possible time. The docstring carried the same characters, so `sys.exit(__doc__)` would have crashed
on a plain usage error too. Fixed twice over: every printed string is now ASCII, and
`sys.stdout.reconfigure(errors="replace")` is the floor under that habit for whatever gets added
next. The existing harness had no non-ASCII output, so this was mine.

## Verification

- `alice_harness.py` parses, and `ballistics` and the exec-path resolution both **ran on this
  machine** with no game — that is the whole part of this work that can run without one.
- `deployed.sh` reported **NO-RECORD** for this project; the installed `d3d9.dll` (702,976 B) is now
  stamped.

**Nothing that touches the game has been run.**

## The next launch

Launch with `-freeconsole -allowcheats`, bind `F7` to `exec commands`, then:

```
python alice_harness.py bugit
```

| what happens | what it means |
| --- | --- |
| the console prints a **location and rotation** | **Route 1 is live and the row collapses to "use it".** `bugitgo` then gives absolute, repeatable camera aim, and routes 2–4 become optional. |
| the console errors on `BugIt` | the cheat manager is not exposed in this retail build. Route 2 next: bind a numpad key to `Axis aTurn` and see whether it turns the camera. |
| **nothing at all happens** | three silent failures share this symptom, and they must be separated before concluding anything: the launch flags missing, `F7` not bound to `exec commands`, or the exec file in the wrong directory. The harness prints all three as a pre-flight, and writing to four directories removes the third. |

## What is NOT established

- That any of the four routes works. **None has been run.**
- That `BugIt`/`BugItGo` exist in this retail build — `[reported]`, from UE3 documentation and
  community guides, never tested here.
- Whether Alice polls XInput at all, which is what decides route 3.
- Whether the game reads input at the moment any future test is run. The `/sr` drop's most useful
  warning is a test-design one: a sibling's first injection test ran at a title screen that polls no
  input at all, and **every negative from it was worthless because it could not have gone positive.**
