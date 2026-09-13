# 2026-09-13 — the shadow matrix nobody was watching (and four other things the files answered)

Dev PC `DESKTOP-V8GTSIR`, `/lm` (auto-picked). **The game never ran: Steam is signed out on this
machine and Alice exits immediately without it**, so this session is entirely static — me deploying
and recording, one reader helper doing the work. Five reader drops drained into the dossier.

---

## The headline

**We have been chasing the wrong matrix.** The board's ⭐ row wanted the pixel-shader `ViewProjection`
copy tested in a scene with dynamic lights. While answering a *different* question — "what would a
mis-handled SSAO pass look like?" — the reader found **three more view matrices that reach pixel
shaders and that our head-tracking edit never touches**:

| constant | pixel shaders that declare it |
| --- | --- |
| **`ScreenToShadowMatrix`** | **56** |
| `ScreenToWorld` / `ScreenToWorldMatrix` | 28 / 5 |
| `PrevViewProjMatrix` | 4 |

`[measured 2026-09-13]`

**Why `ScreenToShadowMatrix` is the better suspect for "shadows slide as the head moves":**

- The shadow pass reads scene depth **drawn with our edited camera**, then maps it into shadow space
  with a matrix built from the game's **unedited** view. The two disagree by exactly our own edit.
- It needs **no dynamic light** — it runs wherever there is a shadow, so it reproduces in the save we
  already have. The VP-copy row has never once seen its shader bound (0 across 4.6 million writes).
- **The error is precisely zero at head offset 0** and grows with the offset, so the A/B is clean by
  construction: any wrongness still visible at offset 0 is not this bug.

`[inferred-static 2026-09-13]` — read from constant names and their company, not from the binary.

## The correction is a conjugation, not the ±d we already use

The existing coherent-view fix moves a *world-space* matrix, which is a translation into one register.
This one starts in *screen* space, so the same head movement has to be carried through the projection:

**`M_correct = K · M`, with `K = inv(edited view) · game view`**

Written as a ±d on some register it would be **nearly right in the middle of the screen and wrong at
the edges** — the nastiest kind of wrong, because it looks almost fixed. Both near-misses (inverting
the other matrix; multiplying on the other side) are pinned by their own failing tests.

⚠️ **One assumption is unverified and is why the rewrite ships OFF:** that the shader's screen input is
the clip vector our matrix produces. If the engine folds a viewport scale into it, `K` needs
conjugating too. Only the live run settles it.

## Built, deployed, not yet run

| build | what it adds | state |
| --- | --- | --- |
| `79f0b8737296` | the capture no longer wastes its 8 dumps on the main menu | superseded by the one below |
| `997651500bfe` | partial-upload observer (see below) | in `staging` |
| **`8dea5b9ce191`** | counters for all four passes above + the shadow correction behind its own marker file | **deployed on the dev PC** |

169 checks, 0 failures; 15 deliberate breakages all caught `[compile-verified 2026-09-13]`. The
shadow rewrite only runs if `alice_vr_shadowfix_on.txt` is present — it is **not** present, so the
first run is observe-only.

## Three smaller answers

- **The capture budget is fixed.** All 8 dumps used to be spent on the main menu. They now go to the
  event we actually want, with the menu's repeated class rationed to one. The old policy is the
  suite's control, so the test can fail `[compile-verified 2026-09-13]`.
- **The "copy arrives in pieces" suspect is dead.** Every one of the 4,126 pixel shaders that declares
  this matrix declares it **four registers wide** — a four-register-only guard misses 0.000 %
  `[measured 2026-09-13]`, and the live counter has never once incremented `[disproved 2026-09-13]`.
  Only an engine-level split of one upload survives, which no file can settle, so it is counted rather
  than assumed.
- **Where the moving lights are.** Only **27 dynamic light actors exist in the whole game** (13
  switchable, 12 movable, 2 spot; no sun-type), against 7,621 static ones `[measured 2026-09-13]`.
  The nearest from our save is one piece ahead at **"Always Elevenses"**; the richest is **Hide Park in
  Chapter 5's London — 7 of them**, and the only place whose lights are flagged to cast moving shadows
  on characters.

## The save is further along than the board thought

The save's own data lists what Alice owns: **melee, Focus, Dodge — and no ranged weapon**
`[measured 2026-09-13]`. So:

- the **combat HUD and the Focus reticle are reachable** at the next fight (minutes away);
- the **aiming crosshair is not reachable at all** in this part of the game — the aiming mode appears
  in exactly **one map of 858**, past "Always Elevenses". That independently confirms the earlier
  bytecode finding about `T`.
- **Both open FLAT rows share a destination:** the fight at "Always Elevenses" has 30 enemies and its
  own UI tutorial, and the nearest dynamic light is the very next piece. **One trip closes both.**

**SSAO is on here — but by this PC's profile, not by the game** (shipped default is off)
`[measured 2026-09-13]`. ⚠️ So an SSAO result from this machine is not automatically reproducible on
the home PC. Its passes are *global* shaders and **none declares `ViewProjectionMatrix`**, so a zero on
that counter says nothing about SSAO — which is exactly the kind of false all-clear the counter would
otherwise have handed us.

## Automation, scored

| Capability | Status |
| --- | --- |
| Self-launch | ⛔ **blocked this session** — Steam signed out; the game exits at once, and a direct exe start does too |
| Menu → gameplay | not exercised |
| Commands | ⛔ no console in this build (settled 2026-09-08) |
| Character + camera | not exercised |
| Self-close | not exercised |

## Not established

- Everything that needs the live run: the four new counters in a lit scene, whether the conjugation is
  right, and whether the screen-input assumption holds.
- Whether the engine ever splits one matrix upload across two commits `[hypothesis]`.
- How bright or far-reaching any of the 27 dynamic lights is — the light data past the header was not
  decompressed.
