# ⭐ The `[PD]` row may not need a mouse at all: `exec <file>` is a full Python→console channel, and `BugItGo` sets rotation absolutely

**From:** `/gr` (estate sweep, 2026-09-07, third drop) · **For:** the modding lane, for
`ENGINE-DOSSIER.md` §10 and the board's `[PD]` mouse-injection row

Supersedes: my own `2026-09-07-gr-the-camera-injection-row-has-a-proven-recipe-on-the-ue3-sibling.md`
— its **recommended order only**. That drop's sibling evidence stands; two cheaper routes now sit in
front of it.

**One ask:** add the two keyboard-only camera routes below to §10 before any mouse code is written.

**Full write-up:** [`external-research/topics/2026-09-07b-the-console-exec-file-is-a-full-python-to-game-channel-over-keyboard-alone.md`](../../external-research/topics/2026-09-07b-the-console-exec-file-is-a-full-python-to-game-channel-over-keyboard-alone.md)

## ⚠️ What is NOT new

**This lane already recorded on 2026-08-25 that the console is reachable** (MadnessPatch's documented
"Developer console access (F2)", plus the sibling topic's note that UE3's default console key is
Tilde). That is not rediscovered here. **What is new is that the console is scriptable from Python
over a single keypress, and that it carries an absolute pose-set command** — which is what makes the
row's mouse question optional rather than central.

## ⭐⭐ Route 1 — one keypress, any console command

Bind a key to `exec commands`, put an **extensionless** file named `commands` in
`…\Alice Madness Returns\Binaries`, and **rewrite it from Python while the game runs** — the next
press executes the new contents `[reported 2026-09-07]`. That is a complete Python→console channel
over a single synthetic keypress, which the harness already drives reliably.

It reaches the primitive the row actually wants:

- **`BugItGo <X> <Y> <Z> <Pitch> <Yaw> <Roll>`** — a UE3 `CheatManager` exec that sets the player's
  **location *and rotation*** absolutely; **`BugIt`** prints the current pair. `[reported]`
  Aim becomes **absolute, repeatable and self-verifying** rather than a calibrated nudge.
- Plus `playersonly`, `toggledebugcamera`, `fov`, `ghost`, `fly`, `teleport`, `viewmode`.
- ⚠️ `SetMouseSensitivity` and `SetRotation` **do not exist** under those names — the real ones are
  `SetSensitivity` and `BugItGo` `[checked 2026-09-07; the same searches did return `playersonly`,
  `toggledebugcamera`, `fov` and `BugItGo`, so they were capable of positives]`.

Enabling: launch flags `-freeconsole -allowcheats`, and
`Bindings=(Name="Tilde",Command="set console consolekey Tilde")` in `AliceInput.ini` (reportedly
after resetting in-game bindings to default).

## ⭐ Route 2 — UE3 binds a keyboard key straight to an analog axis, and Alice already uses the grammar

`Bindings=(Name="TurnLeft",Command="Axis aBaseX Speed=-200.0 AbsoluteAxis=100")` — confirmed in a
retail UE3 `BmInput.ini` **and** in UDK's stock `UDKInput.ini` (which also gives
`Axis aLookUp` for pitch). `AbsoluteAxis=100` is what makes a digital key hold a constant axis value
`[inferred-static]`. **Alice's own `AliceInput.ini` already carries this grammar** —
`+Bindings=(Name="XboxTypeS_RightX",Command="Axis aTurn Speed=-1.0 DeadZone=0.2")` — so `aTurn` and
`aLookup` are live axes here `[reported 2026-09-07]`.

Strong because it came back **unprompted and identically from two independent files**, in answer to
an open request for "all Bindings lines containing Axis" rather than a question naming the syntax.

⚠️ **Two gotchas.** The binding must go in **both** `AliceGame\Config\DefaultInput.ini` (**with** a
leading `+`) and the `My Games` `AliceInput.ini` (**without**), or the game strips it — and *which*
`My Games` tree is live differs per machine, per my separate drop today. And a held turn key will
likely **accelerate**, because `AAlicePlayerController` ramps look speed via
`aTurnElapsedTime`/`aLookUpElapsedTime` `[inferred-static]`.

## ✅ The mouse itself would probably have worked — but it is now the least precise option

Alice's mouse path looks like the **Win32 cursor/window-message path, not Raw Input**
`[inferred-static 2026-09-07]`: Wemino's MadnessPatch hooks `UpdateMouseLock` (whose hook calls
**`ClipCursor`**) and **`ProcessDeferredMessage`**, the deferred `WM_*` handler. A Raw-Input reader
has no reason to clip the cursor. ⚠️ Its `dinput8.dll` proxy is **not** evidence about the mouse —
UE3's `WinDrv` uses DirectInput8 for gamepad enumeration.

⚠️ **And a correction to my earlier drop:** the sibling's *"120 steps of `dx=40`"* is **not portable
between machines**. Windows pointer ballistics can multiply an injected relative delta by **up to
four times** depending on pointer speed and the two threshold values `[reported, Microsoft's own
documentation]`. Pin them via `SystemParametersInfo` at harness start, or calibrate. Also: **UIPI
makes `SendInput` fail silently** if the game runs at a higher integrity level than the harness —
neither the return value nor `GetLastError` says so.

## Two more things worth having in §10

- **Wemino's MadnessPatch** (GPL-2.0, `dinput8.dll` proxy) fixes **stuck keys caused by a key-state
  desync** between the game and the real keyboard, and disables the game's heavy mouse smoothing and
  negative acceleration. A game with a known key-state desync is exactly the kind that mishandles
  rapid synthetic key events — **if the harness ever sees a sticking key, this is the first suspect
  and it is already diagnosed.** ⚠️ Different DLL slot from our `d3d9.dll`, but untested together;
  noted as available, not recommended.
- The built-in `FreeCamera` exec exists, but guides report **"the mouse doesn't move the camera"** in
  that mode and recommend a controller `[reported]` — a small second argument for the virtual-pad
  route in my earlier drop.

## Suggested §10 change and the one launch that settles it

Record the four routes in order — **console `exec` → keyboard `Axis` → `virtual-pad.py` →
`MOUSEEVENTF_MOVE`** — with `BugIt` as the read-back for all of them, which turns "did the camera
move?" from a screenshot judgement into a number (and so sidesteps the sibling's frame-delta hazard in
rainy Whitechapel).

**One launch decides the scope of the whole `[PD]` row:** launch with `-freeconsole -allowcheats`,
open the console, type **`BugIt`**. Prints a location and rotation ⇒ route 1 is live and the row
collapses to "wire the `exec` file". Errors ⇒ the cheat manager is not exposed in this retail build,
and route 2's test is next: does a numpad key bound to `Axis aTurn` turn the camera?

## Credit

Wemino (MadnessPatch); snorrewb (the UDK stock config); GreatEmerald (UnCodeX UT3 `PlayerInput`);
Epic Games (`BugItGo` docs); ikrima (UDK command lists); Fusilade (Alice launch flags); the Steam
Alice community guide authors (console key, the `exec` batch primitive, the free-camera caveat);
Microsoft Learn (`SendInput`, `MOUSEINPUT` ballistics, UIPI). Added to
`external-research/CREDITS.md`. Read online only; nothing cloned, downloaded or installed.
