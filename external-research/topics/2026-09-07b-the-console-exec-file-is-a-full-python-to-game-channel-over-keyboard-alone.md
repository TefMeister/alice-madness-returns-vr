# The mouse may be the wrong question: UE3 binds keys to *axes*, and `exec <file>` is a full Python→console channel over keyboard alone

**Status:** 🆕 new · **Priority:** ⭐ high — it offers two routes to camera control that are **cheaper
and more precise than mouse injection**, and it revises the recommendation in
[the sibling-input topic](2026-09-07-the-camera-injection-question-is-already-answered-on-the-sibling-ue3-game.md)
filed earlier today.

## Why this was looked up

The `[PD]` row asks for `SendInput` `MOUSEEVENTF_MOVE` in the harness. The earlier topic today
answered *"will that work?"* from our own siblings (yes on `enslaved-vr`, no on `psychonauts-vr`).
This one asked a different question of the public record: **does UE3 offer a route that needs no
mouse at all?** It does — two of them.

## ⚠️ First, what is NOT new here

**This lane already established on 2026-08-25 that the console is reachable** — the MadnessPatch
topic records "Developer console access (F2)" as an explicit documented feature of that patch, and
notes the open question of whether F2 works without it; the `enslaved-vr` sibling topic adds that
UE3's default console key is **Tilde**, not F2. None of that is rediscovered here.

**What is new is that the console is *scriptable from Python over a single keypress*, and that it
carries an absolute pose-set command.** That is what turns a known-reachable console from a
convenience into an automation channel — and it is what makes the `[PD]` row's mouse question
optional rather than central.

## ⭐⭐ 1. `exec <file>`: rewrite a text file from Python, press one key, run any console command

Bind a key to `exec commands`, put an **extensionless** file named `commands` in
`…\Alice Madness Returns\Binaries` containing lines like `sendtoconsole god`, and press the key. **The
file can be rewritten while the game is running**, and the next press executes the new contents
`[reported 2026-09-07]`.

That is a **complete Python→console channel driven by a single synthetic keypress** — which the
harness already does reliably. Every console command becomes reachable without solving the mouse
question at all.

And the console carries the primitive this row actually wants:

- **`BugItGo <X> <Y> <Z> <Pitch> <Yaw> <Roll>`** — a UE3 `CheatManager` exec that **sets the player's
  location *and rotation*** to the given values. Its partner **`BugIt`** prints the current location
  and rotation. `[reported]` A read-pose/write-pose pair is close to ideal for a harness: it makes
  aim **absolute and repeatable** rather than a calibrated nudge, and it gives a **read-back for
  verification** — which is exactly what the earlier topic said any camera test needs.
- Also available: `playersonly` (freezes the world, player still moves), `toggledebugcamera`,
  `fov <deg>`, `ghost`, `fly`, `walk`, `teleport`, `viewmode`. `[reported]`
- **`SetSensitivity <float>`** is the real `PlayerInput` exec — useful for making any injected mouse
  delta map to a known yaw. ⚠️ `SetMouseSensitivity` and `SetRotation` **do not exist** under those
  names; `BugItGo` is the working equivalent of the latter `[checked 2026-09-07 — the same searches
  did return `playersonly`, `toggledebugcamera`, `fov` and `BugItGo`, so they were capable of
  positives]`.

**Enabling it:** launch flags `-freeconsole -allowcheats` are reported for this game, and the console
key is bound with `Bindings=(Name="Tilde",Command="set console consolekey Tilde")` in
`AliceInput.ini`, reportedly after resetting in-game bindings to default. `[reported]`

## ⭐ 2. UE3 binds a keyboard key directly to an analog axis — and Alice already uses the grammar

The hoped-for syntax is real and ships in retail UE3. From a retail UE3 game's `BmInput.ini`
(Batman), `[Engine.PlayerInput]`:

```
Bindings=(Name="TurnLeft",Command="Axis aBaseX Speed=-200.0 AbsoluteAxis=100")
Bindings=(Name="TurnRight",Command="Axis aBaseX Speed=+200.0 AbsoluteAxis=100")
```

and from UDK's stock `UDKInput.ini`, including pitch:

```
Bindings=(Name="LookUp",Command="Axis aLookUp Speed=+25.0 AbsoluteAxis=100")
```

`AbsoluteAxis=100` is what makes a *digital* key produce a constant axis value — a steady turn rate
while held — rather than an accumulating one `[inferred-static 2026-09-07]`. UE3 binds in two levels:
a key name binds to an alias, and the alias carries the `Axis` command, so
`Bindings=(Name="NumPadFour",Command="TurnLeft")` gives keyboard yaw.

**Alice already uses this exact grammar** — its `AliceInput.ini` contains
`+Bindings=(Name="XboxTypeS_RightX",Command="Axis aTurn Speed=-1.0 DeadZone=0.2")`, so `aTurn` and
`aLookup` are live axes in this game `[reported 2026-09-07]`.

This finding is strong because it came back **unprompted and identically from two independent files**
— a UDK project's stock config and a retail `BmInput.ini` — in response to an open request for
"all Bindings lines containing Axis", not a question naming the syntax.

⚠️ **Two Alice-specific gotchas, both documented:**

1. **Add the binding to BOTH files or the game strips it out**: `…\Alice Madness Returns\AliceGame\Config\DefaultInput.ini`
   **with** a leading `+`, and `Documents\My Games\…\AliceGame\Config\AliceInput.ini` **without** it.
   `[reported]` ⚠️ See the config-tree caveat below — which `My Games` tree is live differs per machine.
2. **A held turn key will probably accelerate rather than turn at a constant rate.**
   `AAlicePlayerController` ramps look speed through `aTurnElapsedTime` / `aLookUpElapsedTime`
   `[inferred-static]`. Calibrate turn-per-frame empirically, or flatten the curve (§4).

## ✅ 3. And the mouse question itself now has an answer for *this* game

**Alice's mouse path looks like the Win32 cursor/window-message path, not Raw Input**, which
`SendInput` reaches by definition `[inferred-static 2026-09-07]`. The evidence is indirect but
Alice-specific: Wemino's open-source **MadnessPatch** hooks two engine functions by name —
`UpdateMouseLock`, whose hook calls **`ClipCursor`**, and **`ProcessDeferredMessage`**, the engine's
deferred **Win32 window-message** handler. An engine reading mouse-look from Raw Input has no reason
to clip the cursor or route look through a deferred `WM_*` queue. Corroborating: the same patch
toggles `PlayerInput->bEnableMouseSmoothing` and the `aTurn…ElapsedTime` fields, i.e. mouse deltas
arrive as ordinary UnrealScript `PlayerInput` axes.

⚠️ **Do not read the patch's `dinput8.dll` proxy as evidence about the mouse.** It proves the game
loads `dinput8.dll`, but UE3's `WinDrv` uses DirectInput8 for **joystick/gamepad enumeration**, which
is fully consistent with the mouse being on the message path.

**Two practical `SendInput` caveats to design around, whichever route wins:**

- **UIPI**: input may only be injected into an application at an equal or lesser integrity level, and
  when it is blocked **`SendInput` fails silently** — neither the return value nor `GetLastError`
  reports it. Run the harness at the same integrity level as the game. `[reported]`
- **Windows pointer ballistics scale injected deltas** — the system may multiply relative mouse
  movement by **up to four times** depending on pointer speed and the two-threshold values. **Injected
  `dx` is not a stable unit.** Pin the pointer-speed/threshold values via `SystemParametersInfo` at
  harness start, or calibrate. `[reported, Microsoft's own documentation]` This also means the
  sibling's *"120 steps of `dx=40`"* figure is **not portable between machines** unless the pointer
  settings match — a caveat the earlier topic did not carry.

## 4. Existing tooling worth knowing about — and one warning it implies

**Wemino's MadnessPatch** (GPL-2.0, C++, ships as a `dinput8.dll` proxy) disables the game's heavy
mouse smoothing and negative acceleration, fixes input bindings, adds windowed mode and an FPS cap —
**and fixes stuck keys caused by a desync between the game's key state and the real key state**.

That last one matters directly: **a game with a known key-state desync bug is exactly the kind that
mishandles rapid synthetic key events.** If the harness ever sees a key that "sticks", this is the
first suspect and it is a known, already-diagnosed defect rather than something to debug from scratch.

⚠️ It is a `dinput8.dll` proxy while our own mod is a `d3d9.dll` proxy, so they occupy different
slots — but nothing has tested them together, and this project should not install it casually. Noted
as available, not recommended.

## ⚠️ 5. A reported negative about the built-in free camera

The game has a `FreeCamera` exec (bindable the same two-file way), but public guides explicitly note
that **"the mouse doesn't move the camera" in free-cam mode**, recommending a controller instead, and
describe it as unstable `[reported]`. `playersonly` reportedly does **not** freeze Alice herself while
in free camera.

So free-cam is a screenshot tool here, not an aim mechanism — **and the fact that a controller is the
recommended input in that mode is a small point in favour of the virtual-pad route** from the earlier
topic.

## ✏️ Revised recommendation — this supersedes the ordering in the earlier topic

The earlier topic recommended `virtual-pad.py` first, then `MOUSEEVENTF_MOVE`. Both remain good, but
two cheaper and more *precise* routes now sit in front of them:

1. **`exec` file + console.** Test `BugIt`. If it prints a location and rotation, aim becomes
   **absolute, scriptable and self-verifying**, and the mouse question leaves the critical path
   entirely. This is the single highest-value thing to try.
2. **Keyboard `Axis aTurn` / `aLookup` bindings** (`AbsoluteAxis=100`), in **both** ini files. Pure
   keyboard, which the harness already drives reliably.
3. **`virtual-pad.py`** — still proven on the UE3 sibling, still focus-independent, and now with a
   second argument for it: the free camera reportedly wants a controller.
4. **`SendInput MOUSEEVENTF_MOVE`** — expected to work here (§3), but it is the least precise of the
   four and needs pointer-ballistics pinning and an integrity-level check.
5. **Fallback:** write the rotation directly into `AAlicePlayerController` — the class name is already
   known from MadnessPatch, and this is what every serious UE3 camera tool actually does.

**Whichever route is used, `BugIt` is the read-back.** That converts "did the camera move?" from a
screenshot judgement — which the sibling's frame-delta hazard makes unreliable in rainy Whitechapel —
into a number.

## The concrete next step

One launch with `-freeconsole -allowcheats`, the `Tilde` console binding in place, and `BugIt` typed
at the console. **It prints a location and rotation ⇒ route 1 is live and the `[PD]` row's scope
collapses to "wire the `exec` file".** It errors ⇒ the cheat manager is not exposed in this retail
build, and route 2's test is the next cheapest: does a numpad key bound to `Axis aTurn` turn the
camera?

## Sources and credit

Read online only; nothing cloned, downloaded, installed or copied.

- **Wemino — MadnessPatch** (GPL-2.0): the `UpdateMouseLock`/`ClipCursor` and
  `ProcessDeferredMessage` hooks, the `bEnableMouseSmoothing` / `aTurnElapsedTime` fields, and the
  stuck-key diagnosis. <https://github.com/Wemino/MadnessPatch>
- **snorrewb** — a UDK project whose stock `UDKInput.ini` carries the `Axis … AbsoluteAxis=100`
  bindings. <https://github.com/snorrewb/IMT3601>
- The publicly posted retail **`BmInput.ini`** (Batman, UE3), the second independent witness to that
  grammar.
- **GreatEmerald** — the UnCodeX UT3 API browser (the `PlayerInput` axis list and exec functions).
  <http://greatemerald.eu/uncodex/UT3/engine/playerinput.html>
- **Epic Games** — `UCheatManager::BugItGo` documentation.
- **ikrima** — the Gamedev Guide UDK console-command lists. **Fusilade** — the Alice launch-flag page.
  **Romero UnrealScript blog** — `PlayerInput`. The **Steam Alice community guide authors** — the
  console key, the `exec commands` batch primitive, and the free-camera caveat.
- **Microsoft Learn** — `SendInput`, `MOUSEINPUT` (pointer ballistics), UIPI, and the DirectInput
  high-DPI mouse note.
- **learncodebygaming** (pydirectinput), **changeofpace** (MouClassInputInjection),
  **ClassicOldSong** (Apollo) and the **LizardByte/Sunshine** team, **Frans Bouma / Otis_Inf** (IGCS),
  **Breno Sarmento** — consulted on the injection question.

## What came back empty, and whether it is real

- **UE3's `WinDrv` mouse path at source level**: not found — **genuinely unavailable**, UE3 source was
  never public. The only legitimate window into it is symbol names in open-source mod code, which is
  how the two hook names above were obtained.
- **Windowed vs fullscreen difference in UE3's mouse path**: not found in public docs. Test it.
- **Any public project driving UE3 mouse-look by injection**: not found — **partly a fetch limit**.
  GuidedHacking, the AutoHotkey forums and Nexus all return 403 to automated fetching, so only search
  snippets were seen. Treat as *not found*, not disproved.
- **PCGamingWiki's Alice page**: HTTP 403 on two attempts — a fetch failure, not a negative; snippets
  confirm the page exists and covers this game.
- ⚠️ **Whether `SendInput` reaches a pure Raw Input consumer is genuinely contested in public
  sources** — streaming projects (Apollo, Sunshine) report it failing for raw-input games and needing
  kernel HID injection, while the entire user-mode injection ecosystem targets raw-input shooters and
  the anti-cheat literature treats user-mode injection as working-but-detectable. **Unresolved, and
  recorded as unresolved** — it does not need resolving for Alice, which is not on that path.
