# 2026-09-09c — the key layout lives in **two** files, and neither of them is `ControlLayout`

`/pd` session, dev PC. **The game was not launched. Nothing here has been run
against it.** The `[PD]` row is answered, and the answer re-opens the capability
this morning's retraction closed.

Evidence: `dev-archive/recon/2026-09-09c-how-key-binding-actually-works/`.
Tool: `dev-archive/tools/parse_gameconfig_cfg.py`.

---

## 1. The answer

Key binding is split across two files, and `AliceControlLayout.ini` — the file
every session so far has been editing — is **neither of them**.

| half | where | what it holds |
|---|---|---|
| **the command** | `[Engine.KeyCommands]` in **`AliceInput.ini`** | 33 `Key_<Action> = <command string>` entries |
| **the key** | **`CheckPoint\<profile>\GameConfig_PC.CFG`** | a fixed array of **33 × 2 = 66** key-name strings: primary for actions 1..33, then secondary for actions 1..33 |

`[measured 2026-09-09]` — 66 length-prefixed strings parsed out of the 2,148-byte
profile, against 33 entries read out of the ini section. The counts match
exactly, and **the profile contains no command text anywhere**, so the two halves
genuinely live apart.

**The check that makes the pairing convincing rather than arithmetic:** slot 5
reads `T` / `Key_AimingMode` / `EnterFPSByRS` — and "`T` enters first person" is
the one binding this project has confirmed live `[verified-live 2026-09-09]`.
Slots 1–4 are `W`/`S`/`A`/`D` against the four movement actions, 11 is `SpaceBar`
against `Key_Jump`, 12/13 are the mouse buttons against melee/range. Every row is
coherent.

### Why added rows were inert

**The bindable action set is fixed at 33.** No ini edit can create a 34th,
because the key for action *n* is read out of a fixed-size array in the profile
and there is no slot 34. `T` works because it *ships* in slot 5.

⚠️ **And `ControlLayout` was genuinely being reloaded the whole time** — the user
copy's `[IniVersion]` stamp had been bumped from `1787589835` to `1788952193`
after the edit, i.e. UE3 regenerated it from the modified default exactly as
designed `[measured 2026-09-09]`. So the failure was never "the file was
ignored"; the file was read and is simply not what binds keys. That is a
sharper version of this morning's retraction, and it makes the same point: the
*mechanism* was the unchecked part.

### Corroboration from the executable

`.rdata` is not encrypted by the SteamStub wrapper, so the relevant strings read
straight out of the shipped binary `[measured 2026-09-09]`:

- `CheckPoint\` + `GameConfig_PC` + `.CFG` appear three times, and immediately
  beside them sits the section name **`Engine.KeyCommands`** — the profile and
  the section are adjacent in the same string block;
- the native script-function thunks are all **index-based**:
  `UAliceGameEngine::execGetAliceKeys`, `execSetAliceKeys`,
  `execGetAliceKeyIndex`, `execExecRebindKey`, `execExecResetKeyBindings`,
  `execExecControlLayout`. There is a getter, a setter and an *index* — and no
  "add a binding" call anywhere;
- **`KeyBindArray` does not appear in the executable in either encoding.**
  ⚠️ That is suggestive, not decisive: UE3 config property names come from the
  script packages' name tables rather than the exe, so its absence is expected
  either way and carries no weight on its own.

---

## 2. ⭐ What this unblocks

This morning's retraction removed the only known route to running a command with
no shipped key — and with it the `BugIt` pose dump, which was the route to
measuring **camera position and eye height**. Those are back, by a different
door.

**Eight of the 33 actions have no key bound at all** `[measured 2026-09-09]`:

`Key_SwitchLockedTargetRight` · `Key_PCAttackType` · `Key_ChangeWeaponGroup` ·
`Key_VorpalBladeAttack` · `Key_PepperGrinderAttack` · `Key_HobbyHorseAttack` ·
`Key_ArmTeapotCannonAttack` · `Key_Attack`

And three separate actions (`Key_LockOn`, `Key_LockOn1`, `Key_LockOn2`) are all
bound to `CapsLock` with near-identical commands, so at least two are redundant.

**So the recipe is: repoint an existing action's COMMAND in `AliceInput.ini`.**
The action keeps its slot and its key; only what it runs changes. Nothing needs
a new slot, and nothing needs the CONTROLS UI.

⚠️ **Two ways to do it, and they trade differently:**

| approach | pro | con |
|---|---|---|
| repoint an action that **already has a key** (`Key_LockOn2`, `CapsLock`) | works immediately, no key assignment needed | costs a redundant lock-on binding, and `CapsLock` still fires the other two LockOn actions |
| repoint a **keyless** action (`Key_PCAttackType`) | costs no existing binding | still needs a key — via the CONTROLS UI, or by writing a key name into its profile slot |

**The first is the cheap test and should be tried first**, because it needs only
an ini edit and answers whether commands are read from the ini at all.

---

## What is NOT established

- **None of this has been run.** The recipe above is `[inferred-static
  2026-09-09]`. The specific result that would show the *derivation* is wrong
  rather than a detail needing tuning: repointing `Key_LockOn2` and pressing
  `CapsLock` produces the old lock-on behaviour and nothing else — that would
  mean commands are **not** read from the ini either, and the whole
  command-side would have to be somewhere I have not looked.
- **The head of the profile (bytes 0x00–0x5F) is not decoded.** It holds
  settings of some kind; only the string table was parsed. Nothing here depends
  on it.
- **That `Engine.KeyCommands` is the section feeding those 66 slots is an
  adjacency argument** — the strings sit together in `.rdata` and the counts
  match 2:1 with a coherent row-by-row reading. Strong, but it is not a decoded
  loader. The loader itself is in `.text`, which is encrypted at rest, and **no
  unpacked copy of the exe survives on this machine** — the 2026-09-03 session
  unpacked one and did not keep it. Re-making it needs Steamless, which is a
  download and therefore the user's call, not this lane's.
- **Whether the CONTROLS UI exposes the keyless actions is unknown.** It was not
  opened.

## Housekeeping: the previous session left the game modified

`DefaultControlLayout.ini` (in the game folder) and `AliceControlLayout.ini` (in
the profile) both still carried the three rows added for the BugIt experiment —
`G`, `H`, `J` — against 36 shipped rows. The experiment concluded and was
retracted this morning, but the files were not put back.

Both restored from their own `.bak-2026-09-09-pre-bugit` backups and verified
byte-identical to them; 36 rows each, no `G`/`H`/`J` remaining. The rows were
proven inert, so nothing about the retraction changes — but a modified game file
left behind is a trap for whoever diffs it next.
