# ⚠️ A board row regressed, and a design lead that may remove the `BugIt` dependency entirely

Filed by: `/pd` in the **tandem seat**, 2026-09-09 15:34, dev PC. **The game was
not launched and nothing here was run.** Session ended early (usage limit), so
this is a short hand-over, not a finished piece of work.

The tandem seat forbids editing `status/`, `modding-notes/` and the dossier, so
both items below are for the `/lm` (or a later solo `/pd`) to action.

---

## 1. ⛔️ ACTION NEEDED — an answered `[PD]` row was re-added to the OPEN block

**The row that begins "how does the game actually load its key layout?" is
answered and should not be on the board.**

| time | commit | what |
| --- | --- | --- |
| 14:48 | `e06901b` (`/pd`) | removed the row — it had just been **answered** |
| 15:03 | `ee5d694` (`/lm`) | **re-added it**, with the pre-answer wording |

The re-added text still says *"profile cache, compiled defaults or a fixed row
count all fit `[hypothesis]`"*. All three were settled at 14:48:

- **commands** live in `[Engine.KeyCommands]` in **`AliceInput.ini`** — 33
  `Key_<Action>` entries;
- **keys** live in `CheckPoint\<profile>\GameConfig_PC.CFG` — a **fixed
  33 × 2 = 66** key-name array with no command text in it at all;
- so the action set is **fixed at 33** and no ini edit can create a 34th.

`[measured 2026-09-09]`. Full detail:
`modding-notes/2026-09-09c-the-key-layout-lives-in-two-files-and-neither-is-controllayout.md`
and dossier **§6c**, both of which survived — **only the board row regressed.**

**⚠️ Why this matters more than a stale line:** `gate-scan --next` walks straight
into whatever the board says. A `[PD]` row describing an answered question as an
open hypothesis will be picked up and worked again.

**Suggested fix:** delete the row. If something about it is still wanted, the
open part is only *"can a repointed action actually run an arbitrary command?"*,
which is `[FLAT]`, not `[PD]` — see §6c's "what this unblocks".

### The shape of the mistake, for the tandem trial's own record

Nothing went wrong with git, and neither session did anything careless: both
held the claim legitimately, in sequence, and the `/lm` re-audited the whole
`OPEN` block as it is supposed to. **Rewriting a block wholesale silently
reverts rows another session closed inside it.** That is the same failure mode as
2026-09-05, in a form the claim system cannot catch — the claim was correctly
held both times.

⭐ **This is an argument FOR the tandem shape rather than against it:** a reader
sitting alongside is exactly what noticed. It is the first thing the seat caught.

---

## 2. ⭐ DESIGN LEAD — the camera's WORLD POSITION looks recoverable from the VP alone

For the `[PD]` row *"first person is ours to build … decide where the head offset
comes from, given no pose dump is reachable"*.

**`[hypothesis]` — derived on paper this session and NOT yet verified
numerically.** I ran out of session before writing the test, so please treat the
algebra as unchecked. It is written down because, if it holds, it removes the
`BugIt` dependency that has been blocking camera position and eye height.

Using the shipped accessors' own convention (`clip = c0·x + c1·y + c2·z + c3`,
so "column *j*" means `(regs[0][j], regs[1][j], regs[2][j])`):

- column 3 is the coefficient set producing `clip.w`, and for a camera-shaped VP
  it is the **unit forward axis** — this is exactly what
  `alice_stereo_row3_len()` already measures as 1.0, and what
  `alice_stereo_camera_angles()` already reads yaw and pitch out of;
- column 0 is `p00 · right`, so `right = col0 / p00`;
- column 1 is `p11 · up`, so `up = col1 / |col1|`;
- and the fourth register `regs[3]` is the translation row, whose entries are the
  negated projections of the eye onto those axes:

```
    eye·right   = -regs[3][0] / p00
    eye·up      = -regs[3][1] / |col1|
    eye·forward = -regs[3][3]
    eye         = (eye·right)·right + (eye·up)·up + (eye·forward)·forward
```

The last step is only valid because right/up/forward are orthonormal, which
`alice_stereo_is_camera_vp()` already partly enforces (it checks
`|col3| == 1` and `col0 ⊥ col3`).

**How to check it cheaply and honestly:** build a VP from a known eye and
orientation in a host test, run the recovery, and require the eye back to ~1e-4.
That is a self-contained numeric test in the existing `stereo_ue3_test.c` style
and needs no launch. **If it works, camera position becomes a free per-frame
read**, and the `camtrace` line can carry position beside yaw/pitch.

### And the matching write, same algebra

Moving the eye by a world offset `d` is exactly translating the world by `-d`:

```
    for j in 0..3:  regs[3][j] -= dot(d, column_j)
```

Four multiply-adds, exact, no decomposition, works for any offset — which is the
"move the view to a head position along the camera's own axes" the row asks for.

### ⚠️ THE HAZARD TO DESIGN AROUND, and it is easy to miss

**Do not apply an eye translation on the X axis on top of the existing shear —
it would double-apply.** The dossier already records that the shear's one-element
part *"alone reproduces a parallel (on-axis) eye translation"*, with the extra
constant NDC shift making it off-axis. So the per-eye IPD translation **is
already in `alice_stereo_apply_viewproj()`**.

The new function is for the **head/body offset** — a different quantity from the
IPD — and the two must stay separate, with the shear left owning the eye
separation. A function that silently did both would look correct in a static test
and be wrong by exactly one IPD in the headset.
