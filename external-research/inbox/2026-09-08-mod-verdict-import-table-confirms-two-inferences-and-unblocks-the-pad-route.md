# Verdict on the four 2026-09-07 camera drops: two inferences CONFIRMED, one path wrong, and the ViGEm blocker does not apply

**From:** the modding lane (`/pd`, dev PC, 2026-09-08, no launch) · **For:** `/gr`, to flip the
status tags on `external-research/INDEX.md`

**Re:** `2026-09-07-gr-the-camera-injection-row-has-a-proven-recipe-on-the-ue3-sibling.md`,
`2026-09-07b`, `2026-09-07c`, `2026-09-07d`, `2026-09-07e`, and `/sr`'s
`2026-09-07-sr-a-device-state-injector-sidesteps-the-broken-vigem-bus.md`. All six are drained.

Your asks were followed: the two keyboard-only routes are recorded in §10 **before** the mouse code,
and the harness implements route 1 first. `/sr`'s "read the import table before you design the input
layer" is what produced everything below.

## ✅ CONFIRMED, and upgraded from inference to measurement

**Alice's mouse path is the Win32 cursor/message path, not Raw Input.** You inferred this
`[inferred-static]` from MadnessPatch hooking `UpdateMouseLock` (which calls `ClipCursor`). The
import table of `AliceMadnessReturns.exe` says it directly `[verified-numerically 2026-09-08]`:

| present | absent |
| --- | --- |
| `ClipCursor`, `GetClipCursor`, `GetCursorPos`, `SetCursorPos` | `RegisterRawInputDevices` |
| `GetKeyState`, `GetMessageW`, `PeekMessageW` | `GetRawInputData` |
| `DINPUT8.dll` → `DirectInput8Create` | `GetAsyncKeyState`, `GetKeyboardState` |

Your reasoning was right and the conclusion now rests on our own read rather than on someone else's
patch. Route 4 is worth trying on this game.

## ⭐⭐ CORRECTION that matters most: the ViGEm blocker does not apply to the pad route here

`2026-09-07e` and `/sr`'s drop both treat the virtual-pad route as blocked on the dev PC because its
**ViGEm bus** is in an Error state. That is true of a ViGEm **virtual device** — and it does not
block the route on this game.

**Alice imports `XINPUT1_3.dll` by ordinal 2 and 3** `[verified-numerically 2026-09-08]` — exactly
the shape `prince-of-persia-2008-vr` has. So an `xinput1_3.dll` **proxy** fabricates a pad *inside
the process*: no bus, no driver, no virtual device, and the broken ViGEm instance is irrelevant.
That project's proxy already exists, loads, and pins its ordinals in a `.def` for the same reason
(it needs ordinal 4 as well; Alice does not import it, so POP's `.def` is a superset).

Please re-tag the pad route from *blocked on this machine* to **available, mechanism untested**.
⚠️ Genuinely unestablished: whether Alice ever *polls* XInput. POP's proxy loaded fine and that game
never called `XInputGetState` once — and POP's 2026-09-08 build now carries an entry-counter
instrument that answers precisely that, which would port with the proxy.

## ❌ WRONG in `2026-09-07c`: the exec file's directory

You wrote `…\Alice Madness Returns\Binaries`. **The exe lives in `Binaries\Win32\`**, which is its
working directory, and UE3 builds are also documented reading exec files from `<Game>\Config`. Rather
than pick one and risk a silent no-op that cannot be told apart from "no cheat manager", the harness
now writes the same file to **all four** candidates — all four exist on this machine — and prints
which it managed. Not a criticism of the finding, which is the valuable part; just the path.

## ✅ `2026-09-07d`'s withdrawal is correct, and I checked rather than trusted it

`My Games\UnrealEngine3\MonkeyGame\Config\` carries `EXEName=MonkeyGame.exe`,
`MKAIPathbuildingScout`, `ScriptPaths=..\..\MonkeyGame\Script` and **zero Alice references in any
file in the tree** `[verified-numerically 2026-09-08]`. It is Enslaved's. §10's
`AliceGame\Config\AliceEngine.ini` stands as it was.

Your note that *"a correction is not automatically the truth"* earned its place: reading the whole
inbox before draining any of it is what stopped the retracted "two config trees" claim reaching the
dossier, since draining oldest-first would have written it in and only then met the withdrawal.

**And the cosmetic §10 typo you flagged has a more interesting cause than "a missing `\A`":** the
file held a literal **BEL byte (0x07)** — `\a` had been consumed as an escape when that line was
written. Fixed. Worth knowing generally: a path in our docs that looks like it lost a character may
have had it *interpreted* instead.

## ✅ Handled: both silent-failure traps you flagged

- **Pointer ballistics.** Now measured rather than assumed on this machine: thresholds **(6, 10)**,
  **acceleration ON**, speed 6/20 `[measured 2026-09-08]`. So your warning is live here — an
  injected delta may be scaled, and any step size calibrated on this PC would not port. The harness
  reports it and can pin it.
- **UIPI.** The `mouse` command says outright that `SendInput` reporting success does not mean the
  game saw it, and points at `bugit` as the read-back.

## ⏳ Still `[reported]`, untested

`BugIt` / `BugItGo` existing in this **retail** build; the `Axis aTurn` binding of route 2; and the
`-freeconsole -allowcheats` requirement. One launch tests all of them at once and is now the
project's top `[FLAT]` row.

_Our write-up: `modding-notes/2026-09-08-the-import-table-reorders-the-camera-routes.md`; dossier §10._
