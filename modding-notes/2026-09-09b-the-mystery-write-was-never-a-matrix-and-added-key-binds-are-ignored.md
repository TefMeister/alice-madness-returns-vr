# 2026-09-09b — the mystery `c0` write was never a matrix, and added key binds are ignored

*Session: `/lm alice-madness-returns-vr`, dev PC, two launches, fully autonomous. Evidence:
`dev-archive/recon/2026-09-09b-c0dump-says-it-was-never-a-matrix-and-added-key-binds-are-ignored/`.*

Three `[FLAT]` rows were open. Two are answered outright, one is answered in the negative and
**retracts a claim this project made earlier the same day**.

---

## 1. ⭐⭐ THE ONCE-PER-FRAME `c0` WRITE IS NOT A MATRIX. IT IS A BLUR PASS, AND THE SHEAR WAS CORRUPTING IT

The `/pd` session had written the discriminator into the code as a comment and deployed the
instrument. One launch reads it:

```
OTHER  SKEWED  Vector4fCount=8  p00=0.002210 |row3|=0.001353 perp=0.816497
   row0 -0.001563  0.000000 -0.001563  0.000000
   row1 -0.002778 -0.002778 -0.001389 -0.001389
   row2 -0.002778 -0.002778 -0.001389 -0.001389
   row3 -0.000781  0.000781 -0.000781  0.000781
c0 writes by Vector4fCount: 4=23372 5=0 6=0 7=0 8+=1112
c0 writes by kind: camera=23352 affine=20 scaled=0 skewed=1112 degenerate=0
```

**`Vector4fCount = 8`, so it is not a 4×4 matrix at all**, and the numbers say what it is outright.
The backbuffer is 1280×720, and:

| value | is exactly |
| --- | --- |
| 0.00078125 | 1 / 1280 |
| 0.0015625 | 2 / 1280 |
| 0.00138889 | 1 / 720 |
| 0.00277778 | 2 / 720 |

Every element is a whole-texel offset in UV space. It is a **filter/blur pass uploading
`SampleOffsets` as an eight-register array**, exactly as the shipped `GlobalShaderCache` predicted.
`[verified-numerically 2026-09-09, n=1 launch, 24,484 c0 writes]`

**And the census is total: every skewed write is an 8-register write.** 1112 skewed against 1112 at
count ≥ 8, in the same run — the two counters are independent and agree exactly. There is no
residual mystery matrix left over. `[verified-numerically 2026-09-09]`

### The defect this exposes, and the fix

The interception test was `start == 0 && count >= 4`. A four-register ViewProjectionMatrix satisfies
it — and so does the eight-register blur array. So **whenever stereo was on, the shear rewrote
registers 0..3 of a blur pass's sample offsets, every frame.** That is a real rendering defect that
had never been seen, because it only fires with stereo enabled and its symptom (a wrongly-filtered
blur) looks like ordinary stereo weirdness.

A ViewProjectionMatrix is exactly four registers, so the fix says so: `count == 4`. The
classification and census deliberately still see every write — that census is what found this.

**Verified, both directions:**

- The blur array is no longer touched: the only writes that can now reach the shear are the 4-count
  ones. `[compile-verified 2026-09-09]`
- **The stereo shear itself is unchanged.** Stereo off → on, measured on the same scene by phase
  correlation: **−5 px before the fix, −6 px after** `[measured 2026-09-09, n=1 scene each]`. The
  1 px is framing noise between two launches, not a change in the shear. So the fix removed the
  corruption without touching the thing that was working.

---

## 2. ⛔️ RETRACTION: added key bindings are NOT read. There is no "bind any command to any key" channel

**This retracts what this project wrote this morning.** The 2026-09-09 note and dossier §9 said
`AliceControlLayout.ini` "binds engine commands straight to keys with no console in the path" and
called it a live second command channel `[verified-live]`. **The `verified-live` part covered only
that `T` enters first person.** The generalisation to *rebinding* was never tested, and it is wrong.

### What was done

Three unused engine commands were bound to three free keys in **both** copies of the layout file
(the live per-user one and the game-folder template), while the game was closed:

```
KeyBindArray1=(Name="G",Command="BugItForGameController")
KeyBindArray1=(Name="H",Command="StatUnitAndStatFPS")
KeyBindArray1=(Name="J",Command="ChangeCameraMode true | OnRelease ChangeCameraMode false")
```

All three did nothing. The rows were still in the file afterwards, so the game had not rewritten it.
But **two explanations fit that equally**: the added rows are ignored, or those three commands are
absent from this retail build the way the console is.

### The discriminator, which is the whole point

Put a command **known to work** on a new key. `G` was rebound to `EnterFPSByRS` — the exact command
that `T` carries — and the game relaunched:

```
before   : third-person
after G  : third-person      <- the same command that works on T
after T  : FIRST-PERSON      <- seconds later, same run
```

`[verified-live 2026-09-09, n=1 launch]` **The game does not honour rows added to this file.** The
shipped bindings work; new ones do not. `T` works because it shipped, not because the file is a
channel.

⚠️ **Why the mechanism is still open.** Not established: whether the layout is cached in the profile
or save, compiled into the build, or read with a fixed row count. `[hypothesis]` The game's own
CONFIGURATION → CONTROLS screen rebinds keys, and the exe exports `ExecRebindKey` and
`ExecResetKeyBindings` (dossier §9), so **the game clearly can rebind — through its own UI.** Driving
that UI is the obvious next attempt and is untried.

### What survives

- **`T` → first person is real and unaffected.** It shipped on that key.
- **The library rule from this morning's inbox drop survives too** — reading every input-related ini
  is what found `T`. What does *not* survive is the inference that anything named in such a file can
  be reached by adding a row. A correction has been filed to `enslaved-vr`'s inbox, where that
  inference was passed on.

---

## 3. What first person survives — measured

Using `p00cam` as a free state detector (≈1.5697 first person, ≈1.4281 third person — no screenshot
needed):

| action | result |
| --- | --- |
| jump (SpaceBar) | **stays in first person** `[verified-live 2026-09-09, n=1]` |
| run then jump | **stays in first person** `[verified-live 2026-09-09, n=1]` |
| walking (12 taps, 2026-09-09a) | stays in first person |
| weapon switch (`One`) | **exits to third person** `[verified-live 2026-09-09, n=1]` |

The weapon-switch exit was `[inferred-static]` from `QuitFPS` appearing in that key's command list.
It is now verified live, which raises confidence in the rest of that list without proving it.

⚠️ **Combat is still untested** — the Chapter 1 opening has no enemies, and reaching some is the
long drive the HUD row already needs. **Eye height is still unmeasured**, and now looks harder: it
wanted `BugIt`, and §2 says `BugIt` cannot be reached by rebinding.

---

## 4. What this session did NOT establish

- **How the game actually loads its key layout.** Only that adding rows to the ini does not work.
- **Whether the corrupted blur was ever visible.** The defect is proven by construction — an
  8-register array had its first four registers rewritten — but no before/after shot isolates a
  blur artefact, because Whitechapel at rest does not obviously run one.
- **Whether `BugItForGameController` exists at all.** It was never actually executed; the failure
  was in the delivery, not the command.
- **Combat behaviour and eye height in first person**, as above.
