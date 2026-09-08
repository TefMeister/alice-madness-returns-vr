# 2026-09-08 — the VP diagnostic CONFIRMS the unit mismatch, Alice DOES poll XInput, and the console is not exposed

*Session: `/lm alice-madness-returns-vr`, dev PC, one launch, fully autonomous. Three of the five
`[FLAT]` rows answered in that one launch.*

---

## 1. ⭐⭐ The VP diagnostic — CONFIRMED, and the fix is one scale factor

Fired on its own on the first perspective ViewProjection, no setup:

```
row0 = [-0.917089 -0.630229  0.000853  0.000000]   (produces clip.x)
row3 = [-0.566364  0.824155  0.000000  0.000000]   (produces clip.w)
|row0.xyz| = 1.112762   (this is what p00_cached holds)
|row3.xyz| = 1.000000   (1.0 => a RIGID view part, no scale)
SCALE-FREE p00 = 1.112762
=> ORDINARY projection scale (hfov ~ 84 deg) ... the 09-08c unit-mismatch hypothesis is
   CONFIRMED and the fix is one scale factor.
```

`[measured 2026-09-08, n=1 launch]`

The row's branches were "~0.8 (hfov ~100°) ⇒ CONFIRMED" and "~0.0022 ⇒ DISPROVED". The reading is
**1.112762**, i.e. an ordinary projection scale — decisively the CONFIRMED branch, though at a
slightly narrower FOV than the branch guessed: `1/tan(hfov/2) = 1.1128` → **hfov 83.9°**.

**The scale factor, stated precisely:** the cached `p00` is `0.0022` (visible in every frame line),
against a true scale-free `p00` of `1.112762` — a ratio of **505.8×**. The row anticipated "the 380×
amplitude gap"; the measured figure is 506, so whatever is written next should use the measured
number rather than the estimate.

**Free from the same block: `|row3.xyz| = 1.000000` exactly ⇒ the view part is RIGID, no scale.**
That is the cleanest possible statement of it, and it was the row's stated bonus.

## 2. ⭐ XInput — Alice DOES poll it

`alice_xinput_log.txt`, no setup, injection still defaults OFF so nothing was changed:

```
XInputGetState ENTERED for the first time (idx=0) - Alice DOES poll XInput
first pad-0 entry did not inject: state=ok block=mapped enabled=0 pad_force=0 hr=1167
XInputSetState ENTERED for the first time (idx=0)
```

`[verified-live 2026-09-08, n=1 launch]` — and `SetState` too, so the game talks to a pad in both
directions. `hr=1167` is `ERROR_DEVICE_NOT_CONNECTED`, which is simply what a real absent pad
returns. **The pad route is viable**; nothing about it has been *driven* yet.

## 3. ⭐⭐ `bugit` — nothing at all, and the three silent failures are now excluded

`bugit` produced no console, no output, no visible change (delta 1.05 against an idle-animation floor
of 1.05). The row warned that "nothing at all" has three silent causes. All three are excluded, and
I added two more:

| candidate cause | status |
| --- | --- |
| launch flags missing | **excluded** — launched `AliceMadnessReturns.exe -freeconsole -allowcheats` |
| the key is not bound | **excluded** — the bind was verified in the live ini *before* the launch and again *while the game was running* |
| exec file in the wrong directory | **excluded** — the harness writes it to all four candidate directories |
| **keys are not reaching the game at all** | **excluded** — `W` ×12 walked Alice: delta **14.62** against a 1.05 floor |
| **the console is reachable some other way** | **excluded** — `AliceInput.ini` declares `ConsoleKey=Tilde`, and scancode `0x29` opened nothing (delta 2.42) |

⇒ **The console / cheat manager is not exposed in this retail build.** That is the row's second
outcome, reached by exclusion rather than by an error message — because **this build writes no UE3
log at all** (there is no `Logs\Launch.log` under `Documents\My Games\...`, and none in the game
folder), so a failing console command has nowhere to report.

**Route 2 (a numpad key bound to `Axis aTurn`) is next**, exactly as the row said.

⚠️ **NOT established: that the launch flags were honoured.** They were passed and the game started
normally, but with no log there is no positive confirmation the parser accepted them. The conclusion
rests on the *combination* of that with the tilde result, not on the flags alone.

## 4. ⚠️ A pre-flight catch: the exec key collided with BOTH the game and our own proxy

The row said "bind `F7`". `alice_harness.py` agreed, with the comment *"F6..F12 ... are not used by
Alice's default bindings"*. **Both were wrong, and both failures are silent:**

- **Alice binds F1–F9 by default** in `AliceInput.ini`: `F5 quicksave`, `F6 quickload`,
  `F7`/`F8` toggle `bUsePostProcessEffects`, `F9 shot`. Pressing F7 would have **disabled
  post-processing** and never run `exec commands`.
- **Our own d3d9 proxy polls `VK_F6` through `VK_F12`** for its stereo hotkeys, so F7 also
  **multiplies convergence by 0.8** on every press — silently changing the stereo state it shares a
  session with.

Between the two lists **every F-key from F1 to F12 is claimed**. One has to be taken back
deliberately: **F1** (`viewmode wireframe`, harmless to lose, and outside the proxy's F6–F12 range)
is now rebound to `exec commands`, with `AliceInput.ini.bak-2026-09-08-pre-exec-bind` kept. The
harness's key table gained F1–F5 and its comment now states both lists.

⚠️ **The F2 probe I ran first was a bad one and I am recording that too.** I pressed `F2`
(`viewmode unlit`) to test whether keys arrive, got nothing, and nearly concluded keys were not
reaching the game. But `viewmode` is a *dev* command that may simply be stripped from retail — the
standing rule that **a binding surviving in a shipped ini is not evidence the feature is live**.
`W` was the right probe because walking is unambiguously live, and it showed keys arrive fine.

## 5. Automation

| capability | status |
| --- | --- |
| 1. menu → gameplay | ✅ proven: Enter ×3 → profile → CONTINUE GAME → Whitechapel |
| 2. console / exec commands | ⛔️ **NOT AVAILABLE** — see §3. The proxy's own F-key hotkeys remain the only in-game control channel |
| 3. character + camera | ✅ character movement proven (`W`); camera still unexercised |
| 4. self-close | ✅ graceful through the game's own menus, no `taskkill`, both confirm dialogs verified |

The profile's documented exit route was followed exactly and was correct, including its own
correction that the pause menu opens on `MEMORIES` so `MAIN MENU` is Down ×3.

## 6. What to run next time

1. **`[PD]`** — apply the measured **505.8×** scale factor to the convergence path, since the unit
   mismatch is confirmed and the fix is one constant. No game needed.
2. **`[FLAT]`** — route 2 for camera control: a numpad key bound to `Axis aTurn`, since the console
   is out.
3. The two scene-dependent rows (HUD/crosshair/SSAO in a scene that has them; the long-sightline
   depth check) are unchanged and still want a purpose-built run.

Evidence: `dev-archive/recon/2026-09-08-vp-diagnostic-confirmed-xinput-polled-console-absent/`.
