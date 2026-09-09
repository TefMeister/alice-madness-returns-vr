# Match the game window by PROCESS, not by title — the fix and its decoy test are in `doom-2016-vr`

Filed by: `/pd` working `doom-2016-vr`, 2026-09-09, dev PC. **No game was
launched and nothing here was run against one.** This is a create-only drop
because this session holds the claim on DOOM, not on this project.

## The problem, in this project's own file

`dev-archive/tools/alice_harness.py` finds the game window by **title only**. It matched the user's CHROME TAB on 2026-09-09 because the tab title contained "ALICE" - this is the harness the incident was ABOUT.

**A title is user data.** A browser tab, an editor, a chat window, a terminal —
any of them can contain a game's name. A title match can never establish that a
window belongs to the game; it can only narrow the search. The next call after a
bad match types keys into whatever it found.

## The fix, already written and tested next door

`doom-2016-vr/dev-archive/tools/doomdrive.py` now checks **both**: the title
narrows, and `window_process_name()` VERIFIES, via
`GetWindowThreadProcessId` → `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)`
→ `QueryFullProcessImageNameW`. A window whose process image is the game's exe
is the game's, whatever its title says.

Two details worth copying rather than re-deriving:

- **`QueryFullProcessImageNameW`, not `GetModuleFileNameEx`** — it needs only
  `PROCESS_QUERY_LIMITED_INFORMATION`, which a normal user holds for a normal
  process; the module-based calls need `PROCESS_VM_READ` and simply fail.
- **The refusal is LOUD.** When a window matches the title but fails the process
  check it is named in the error along with its owning process. A silent "not
  found" reads identically to "the game is not running", and the whole point is
  that an impostor is visible rather than invisible.

## ⚠️ Verify it with a decoy, not by inspection

`doom-2016-vr/dev-archive/tools/test_find_window_decoy.py` makes a real visible
window titled exactly like the game's, owned by `python.exe`, and requires three
things `[verified-numerically 2026-09-09]`:

1. **title-only matching FINDS it** — the bug reproduced. Without this check the
   other two could pass for the wrong reason and prove nothing;
2. process-checked matching **REFUSES** it;
3. the refusal **names** the impostor and its process.

It needs no game — the decoy is a plain Win32 window the test creates and
destroys. Copying the test is as important as copying the fix.
