# ⚠️ READ BEFORE PRESSING ANYTHING — the head-offset hotkeys sit on three commands the game itself binds

Filed by: `/pd` in the **tandem seat**, 2026-09-09, dev PC. **The game was not
launched and nothing here was run against it.** A fixed build is waiting in
`staging/`; the seat forbids deploying, so that is the `/lm`'s call.

---

## The problem, and it is not hypothetical

I flagged "F1–F5 may collide with the game's own binds — untested" when I added
the head-offset keys earlier today. **It is now tested, statically, and they do.**

`AliceInput.ini` → `[Engine.PlayerInput]` binds F1–F9 `[measured 2026-09-09]`:

| key | what the GAME does | what the PROXY does |
|---|---|---|
| F1 | `exec commands` | — |
| F2 | `viewmode unlit` | — |
| **F3** | **`viewmode lit`** | **head axis select** ← added today |
| **F4** | **`viewmode shadercomplexity`** | **head −5** ← added today |
| **F5** | **`quicksave`** | **head +5** ← added today |
| **F6** | **`quickload`** | wiggle toggle (pre-existing) |
| F7 | postprocess OFF | convergence − (pre-existing) |
| F8 | postprocess ON | convergence + (pre-existing) |
| F9 | `shot` | stereo toggle (pre-existing) |
| F10–F12 | *nothing* | eye / ipd — **the only clean ones** |

**The one that would have wasted the session: `F4 = viewmode shadercomplexity`.**
The board row says to step the head offset with F4/F5. Pressing F4 would turn the
whole scene into a shader-complexity heat map — and the obvious reading of that
is *"the mod broke the rendering"*, not *"I pressed a debug key"*. The row's own
failure table has no entry for it, so it would not have been diagnosed quickly.

**`F5 = quicksave` writes a save file** every time the offset is stepped up.

## ⚠️ AND ONE PRE-EXISTING HAZARD NOBODY HAS RECORDED: F6 = `quickload`

The proxy has used **F6 for the two-eye wiggle toggle** since 2026-09-04. The
game binds the same key to **`quickload`**. If both fire, toggling the wiggle
**loads the last quicksave** — which would throw away play progress mid-session,
and would look like the game had crashed back to an earlier point.

This has apparently not bitten yet, which is itself informative but not
reassuring: `[hypothesis]` that the `[Engine.PlayerInput]` bindings are live at
all. Evidence both ways — the dossier notes F12 is also Steam's screenshot key
and calls it harmless, implying double-firing is tolerated elsewhere; and on
**Enslaved** the same section turned out to be gamepad-only with added keyboard
binds inert, so a declared binding is not proof of a live one.

**Which is exactly why this is worth one deliberate press rather than an
assumption.** See the check below.

## The fix, built and waiting — NOT deployed

`staging/alice-madness-returns-vr/proxy-d3d9/`, sha256 `0bd5a608182a…`
(deployed right now is `df862ab544c0…`).

The three **new** keys move behind **Ctrl**: `Ctrl+F3` / `Ctrl+F4` / `Ctrl+F5`.
UE3 matches modifier state on a binding — the game's own F7/F8 lines say
`Control=False` explicitly — so `Ctrl+F4` does not fire `viewmode
shadercomplexity`.

⚠️ **The pre-existing stereo keys (F6–F12) are deliberately left alone.** They
have live history behind them, and changing them mid-measurement would
invalidate the comparison this session exists to make. Their collisions are
recorded above instead.

`[compile-verified 2026-09-09]`, full stereo suite still green, exports
unchanged. **Deploying it is yours** — the tandem seat must not swap a file
under a running game.

### One subtle bug fixed on the way

The original `if (pressed(F4) || pressed(F5))` then re-tested `pressed(F5)` to
pick the direction. `pressed()` **consumes the edge**, so the second read always
returned false and *every* press would have stepped **down**. The Ctrl version
reads the direction from `GetAsyncKeyState` instead. Nobody would have noticed
except as "the offset only ever decreases".

---

## What to do

**If you deploy the fixed build:** use `Ctrl+F3/F4/F5` and the collision is gone.

**If you do not:** F3 is survivable (`viewmode lit` is the normal mode), but
**do not use F4** — read the offset changes from the `camtrace` line instead,
and step with F5 only, accepting a quicksave per press.

**Either way, one deliberate press settles the open question:** press **F2**
once, on its own. The proxy does not use F2 at all, so nothing of ours can
respond.

- the scene turns **unlit** ⇒ `[Engine.PlayerInput]` bindings **are live**, and
  every collision above is real — including F6 = `quickload`, so **avoid F6**;
- nothing happens ⇒ they are inert in this build, as on Enslaved, and the whole
  table is a non-issue. Record that either way; it settles it for good.

## What is NOT established

- **That the game's F-key bindings actually fire.** Everything above is read
  from config; no key has been pressed. The F2 check is what decides it.
- Whether `Ctrl+F4` is genuinely ignored by the game — it follows from UE3's
  modifier matching and the explicit `Control=False` on F7/F8, but it is
  `[inferred-static]`, not measured.
