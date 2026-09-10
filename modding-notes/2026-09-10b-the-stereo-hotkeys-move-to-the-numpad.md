# 2026-09-10b — the stereo hotkeys move to the numpad, and the F-keys are gone

`/pd` session, dev PC. **The game was not launched and nothing here has been run.**
Everything below is either read from files the game ships or compile-verified.

---

## The headline

**The proxy no longer polls a single F-key.** `VK_F6` through `VK_F12` appear nowhere in the
source or the built DLL `[compile-verified 2026-09-10]`. Build `ade1d41d34b7`, 718,848 B,
deployed, backup `d3d9.dll.bak-2026-09-10b-pre-numpad`, exports unchanged at 2, imports still
system-only, zero compiler warnings.

| function | was | now |
|---|---|---|
| stereo ON / OFF | F9 | **NumPad0** |
| eye mode: LEFT → RIGHT → WIGGLE | F10 **and** F6 | **NumPad1** |
| ipd − / + | F11 / F12 | **NumPad/** and **NumPad\*** |
| convergence − / + | F7 / F8 | **NumPad3** and **NumPad.** |
| head offset: axis / step down / step up | — | NumPad5 / NumPad− / NumPad+ (unchanged) |

The whole keypad afterwards, with nothing doubled:

```
      /  ipd -        *  ipd +        -  head step down
    7 aBaseX -      8 aLookUp +     9 aBaseX +      +  head step up
    4 aTurn -       5 head axis     6 aTurn +
    1 eye mode      2 aLookUp -     3 convergence -
         0 stereo on/off                 .  convergence +
```

## The keys were checked, not assumed

The instruction was to make sure a numpad key was not already doing something. Both binding files
were read in full `[measured 2026-09-10]`:

- **`AliceControlLayout.ini` — the action bindings — names no numpad key at all.** Its complete key
  set is `C, CapsLock, E, Enter, Escape, Four, L, LeftControl, LeftMouseButton, LeftShift,
  MouseScrollDown, MouseScrollUp, One, Q, R, RightMouseButton, SpaceBar, T, Tab, Three, Two, U`.
- **The only numpad `Bindings=` rows in `AliceInput.ini` are the six camera axes we added
  ourselves** on 2026-09-08 (NumPad 2/4/6/7/8/9). The game ships none.

So the free keys were exactly **0, 1, 3, `.`, `/`, `*` — six of them**, and seven functions needed
homes. That is the whole reason eye-swap and wiggle were merged.

## Merging two keys into one removed a wart, not a feature

F10 used to be **refused** whenever the wiggle was on, because the wiggle owns the eye, and the
refusal had to be explained every time it came up. NumPad1 now cycles LEFT → RIGHT → WIGGLE → LEFT,
so there is no state in which a press does nothing. Every capability the two keys had is still
reachable.

## ⚠️ Ctrl is not available as a modifier on this game

The obvious way to fit seven functions into six keys is a Ctrl bank, and it would have been wrong.
`AliceControlLayout.ini` ships

```
KeyBindArray1=(Name="LeftControl",Command="ChangeShrinkingMode | OnRelease UnShrinking")
```

so **holding Ctrl is a gameplay action — it makes Alice shrink** `[measured 2026-09-10]`. The
`ctrlPressed()` helper added on 2026-09-09 (to keep the head-offset keys off F3/F4/F5) had already
become dead code when those moved to the numpad; it is now deleted, together with the comment that
recommended the approach. The modifier was never the fix. Moving off the F-keys was.

## ⚠️ NumLock now gates four of the six, and the failure would be silent

`GetAsyncKeyState` reads **virtual** keys, and with NumLock OFF the numpad digits deliver the
navigation VKs instead `[inferred-static 2026-09-10]`:

| key | NumLock ON | NumLock OFF |
|---|---|---|
| NumPad0 | `VK_NUMPAD0` | `VK_INSERT` |
| NumPad1 | `VK_NUMPAD1` | `VK_END` |
| NumPad3 | `VK_NUMPAD3` | `VK_NEXT` |
| NumPad. | `VK_DECIMAL` | `VK_DELETE` |
| `/ * + −` | unaffected | unaffected |

So stereo, eye mode and convergence-down would go quiet while ipd and the head offset kept
working — a *partial* failure, which is the kind that gets misread as "the game ignores that key".
Two guards, both cheap:

1. **The startup banner now reports NumLock state**, with a loud warning naming the four affected
   keys when it is off.
2. **Every hotkey already logs when it fires**, so a missing line means the key never arrived —
   the same read-it-back discipline that caught the 2026-09-09 silent-key sweep.

Deliberately **not** aliased to the navigation VKs: that would hand the grey
Insert/End/PageDown/Delete keys a second way to fire the stereo controls, trading a visible failure
for an invisible collision.

## ⚠️ One overlap survives, and it is menu-only

`AliceInput.ini` maps `Add` and `Subtract` to the `UISlider` Increment/DecrementSliderValue aliases
and to the `ShiftUp`/`ShiftDown` button prompts `[measured 2026-09-10]`. So stepping the head offset
with NumPad+/− **while a settings screen is open** also drags whatever slider has focus. It cannot
bite in gameplay, which is the only place the offset is used, and the alternative — moving the head
offset too — would cost the three keys that were verified live this morning. Recorded rather than
fixed.

## ⚠️ Numpad `/` is an extended scancode

`E0 35`; bare `0x35` is the main-row slash key, which nothing binds, so getting it wrong would be
silent. This is the mirror of the trap already on record for the numpad digits, which need the
extended flag *absent*. The harness key is `NPDIV` and it is the only one of the six new names with
`ext=True`. Added alongside `NP0`, `NP1`, `NP3`, `NPDEC` and `NPMUL`; the table was checked for
scancode collisions and has none beyond the intentional `ESC`/`ESCAPE` alias.

## What is NOT established

- **That any of these keys reaches the proxy.** Nothing was launched. The six are `[compile-verified
  2026-09-10]` only, and the F-key set they replace was `[verified-live 2026-09-07]` — so this
  trades proven keys for unproven ones and the next launch must re-prove them.
- **That NumLock is on** on this machine right now. It was during the three launches this morning
  (VK_NUMPAD5 and VK_ADD/VK_SUBTRACT both fired), which is good evidence but not a guarantee for the
  next launch — hence the banner.
- **The diagnostic that would show this is wrong rather than merely untuned:** if the startup banner
  says `NumLock is ON` and a numpad press still writes no `HOTKEY` line, the key is not reaching the
  proxy at all and the scancode in the harness is the first suspect, not the proxy.
