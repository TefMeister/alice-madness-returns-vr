# 2026-09-09b — nothing else *binds* c0, so the mystery write is either another view or **not a matrix at all**

`/pd` session, dev PC. **The game was not launched. Nothing here has been run
against it.** The board's `[PD]` row — *"what IS the once-per-frame non-camera
matrix at c0?"* — is advanced as far as static evidence can take it, and the
instrument that finishes it is built, tested and deployed.

Evidence: `dev-archive/recon/2026-09-09b-what-else-writes-c0/`.
Tool: `dev-archive/tools/c0_constant_census.py`.
Code: `staging/alice-madness-returns-vr/proxy-d3d9/`.

---

## 1. The static answer: no shipped shader binds anything else to vertex c0

Compiled D3D9 shaders carry a `CTAB` block naming every constant and its
register, so "what lives at c0?" is plain data on disk. Across **both** shipped
caches `[measured 2026-09-09]`:

| cache | `vs_3_0` shaders | `ViewProjectionMatrix` at c0 | anything else at c0 |
|---|---|---|---|
| `RefShaderCache-PC-D3D-SM3.upk` | 2,807 | 2,431 (`c0 ×4`) | **none** — the other 376 bind *nothing* at c0 |
| `GlobalShaderCache-PC-D3D-SM3.bin` | 39 | 4 (`c0 ×4`) | `SampleOffsets` `c0 ×8`, `SampleOffsets` `c0 ×2`, `SceneCoordinateScaleBias` `c0 ×1` |

⚠️ **Earlier passes on this project only ever read `RefShaderCache`.** The
`GlobalShaderCache` — where UE3 keeps its post-process, filter and fullscreen
shaders, i.e. exactly the passes that run *last* in a frame — had never been
looked at. That is where the interesting row is.

**What this rules out:** the mystery write is not some other *named constant*
quietly sharing the register. No material shader binds anything but the
view-projection there.

⚠️ **What it cannot see:** a constant table says what a shader **reads**.
`SetVertexShaderConstantF` writes the register whether or not anything reads it,
so a write with no matching CTAB entry is invisible to this method. This narrows
the question; it does not close it.

---

## 2. ⭐ The lead this turned up: the mystery write may not be a matrix

The proxy intercepts on **`start == 0 && count >= 4`**. A 4×4
`ViewProjectionMatrix` satisfies that with `count == 4` — **and so does anything
bigger.**

The `GlobalShaderCache` contains **exactly one** vertex shader that binds a
non-view constant at c0: `SampleOffsets`, an **8-register array**, and it
declares *no other constants at all* `[measured 2026-09-09]`. That is the shape
of a UE3 filter/blur vertex shader.

That single fact fits every property the census measured, without needing a
second view to exist:

| census observation | fits a blur pass? |
|---|---|
| exactly **one** non-camera write per frame | a single post-process filter setup |
| always the **last** write of the frame | post-processing runs last |
| never camera-shaped | sample offsets are not a projection |
| `p00 = 0.0022`, three orders below the camera's | ≈ one texel of UV at a reduced-resolution target |

⚠️ **This is `[hypothesis]`, not a finding.** It is a mechanism that would
explain the observations, derived from what the game ships — not a measurement
of what the game does. Two things would each kill it: the write arriving with
`count == 4`, or the dumped numbers looking like a projection.

⚠️ **If it is right, it is a real defect, not a curiosity.** The proxy shears
every qualifying c0 write, so with stereo on it has been **writing a shear into
a blur's sample offsets**. The board already carried "whether that is a defect
still has no evidence either way" — this gives it a concrete mechanism and a
one-launch test.

---

## 3. What was built

### `alice_stereo_classify_vp()` — *why* a matrix is not the camera's

`alice_stereo_is_camera_vp()` returns 0 or 1, so the log could say a write was
rejected but never **which** of its two tests failed — and the failures mean
completely different things:

| kind | test | meaning |
|---|---|---|
| `CAMERA` | \|row3\|=1, row0 ⊥ row3 | rigid view, symmetric projection |
| `AFFINE-ORTHO` | \|row3\| ≈ 0 | orthographic: shadow, light, or 2D canvas |
| `SCALED-PERSP` | ⊥ but \|row3\| ≠ 1 | perspective × a uniform scale — the case a scale factor *would* fix, and the one 2026-09-08c wrongly assumed |
| `SKEWED` | row0 not ⊥ row3 | something non-rigid baked in after the projection |

It reports the **raw** `p00`, `|row3|`, `perp` and `c3.w` beside the verdict.
That is deliberate: this project has already been burnt by a diagnostic printing
*"uniformly scaled by ~1× … CONFIRMED"* for `|row3| = 1.0` — a sentence that
contradicts itself — and **the interpretation is what gets read, not the number**.

**9 new checks, all against ground truth built in the test, none from a capture**
`[verified-numerically 2026-09-09]`. They include a 1280-wide 2D canvas whose
width the classifier recovers knowing nothing about it, and — deliberately — a
909-unit shadow volume that classifies **identically**, to keep visible that
`AFFINE-ORTHO` *cannot* separate a canvas from a shadow volume. Only the
caller's knowledge of the backbuffer width can, which is why the proxy now
records it.

### Two instruments in the proxy

1. **The same-frame `c0dump`** — the camera's matrix and the frame's last
   non-camera matrix, printed **in full, on the same frame**, each with its kind
   and the reason. This is literally what the board row asked for. Capped at 6
   dumps; fires at frame 150 and every 1800 after, so a menu, a level and a
   cutscene each get one.
2. **⭐ `Vector4fCount`, which was never recorded at all** — and is the cheapest
   discriminator available. `count == 4` means a 4×4 really did arrive;
   `count == 8` means it never was a matrix.

⚠️ **A related gap this closed on the way:** the old census ran *inside* the
`is_perspective()` gate, so an **orthographic** write at c0 was not merely
unclassified — it was **invisible**. Every c0 write is now classified.

`[compile-verified 2026-09-09]`, `-Wall -Wextra` clean, exports intact, and the
existing suite still passes in full.

---

## 4. Housekeeping: a `CHANGED` deploy, run down and cleared

`deployed.sh check` reported **`CHANGED`** on entry — the recorded hash was
stamped at 12:33 and the installed DLL was 1,024 bytes larger, dated 12:40.

**Cause found, benign:** the `/lm` session that held this game earlier today
built a second `camtrace` iteration at 12:40 and did not re-stamp. Confirmed by
rebuilding from committed `HEAD` and comparing: the installed file was
**byte-identical** to a fresh build, `4a7139f4…` `[verified-numerically
2026-09-09]`. This build pins the PE timestamp (`-Wl,--no-insert-timestamp`), so
that comparison is meaningful here — on a project without that fix it silently
would not be.

Re-stamped, then re-stamped again after this session's own deploy.

---

## What the next flat run should do

**Nothing to configure — the instruments are ungated and the stereo path is
untouched.** Launch, get into a level, and read the `c0dump` lines.

| what the `OTHER` line says | meaning |
|---|---|
| **`Vector4fCount=8`** | ⭐ settled: it was never a matrix. It is a blur/filter pass's `SampleOffsets`, and **the shear has been corrupting them** whenever stereo is on. The fix is to tighten the interception to `count == 4`. |
| `Vector4fCount=4` + `AFFINE-ORTHO` | a real orthographic matrix. Compare `extent 2/p00` with the printed backbuffer width: equal ⇒ a 2D canvas/HUD pass; unrelated ⇒ a shadow or light projection. |
| `Vector4fCount=4` + `SCALED-PERSP` | a second perspective view carrying a uniform scale. |
| `Vector4fCount=4` + `SKEWED` | a fused local-to-clip matrix — a per-object transform reaching a register we assumed was view-only. |

In every case the four printed rows are the matrix itself, so the answer does
not depend on trusting the verdict.
