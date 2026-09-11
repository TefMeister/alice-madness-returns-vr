# The pixel-VP diagnostic now captures by itself during normal play — build `7af3b5f5`

From: `/lm` reader helper (dev PC), 2026-09-11. Static only: built, not deployed, no git.

Supersedes: 2026-09-11-mod-reader-why-the-pixel-vp-never-matched.md §"The diagnostic" (its
qualification rule and its main-log dumps are replaced as below), and the "flaw" section of
2026-09-11-mod-reader-kitchen-dumps-are-sh-lighting-not-a-matrix.md (now fixed).

## Build `[compile-verified 2026-09-11]`

| | |
|---|---|
| file | `staging/alice-madness-returns-vr/proxy-d3d9/build-2026-09-11c-capture/d3d9.dll` |
| size | 744,448 B |
| SHA-256 | **`7af3b5f53a7d9da7dbd3ea97e80219e417646599e30d6784a55072db3c7507b2`** |
| reproducible | two builds into different folders byte-identical; no warnings; exports unchanged; imports still ADVAPI32 / KERNEL32 / USER32 + CRT |
| on top of | `84eca4ff` (same coherent view, tiers, scale 95). Its folder `build-2026-09-11b-psdiag/` was replaced by this one; the deployed copy in the game folder is untouched |
| rebuild | `OUT=build-2026-09-11c-capture ./build.sh` |
| switch | still only `alice_vr_psdiag_on.txt` beside the exe; with no marker file, the D3D traffic is the same as `84eca4ff` `[inferred-static]` |

## What changed

**1. Only real candidates qualify** — lighting blocks can no longer get in.

- **(a) VP-SHADER-BOUND**: the bound pixel shader declares `ViewProjectionMatrix` (at any register),
  and the write touches those registers **fully or in part**. So a copy uploaded in pieces is caught
  and dumped as `PARTIAL`, register by register, each compared bit for bit with the same register
  of the last vs c0 camera matrix.
- **(b) STRICT CAMERA MATRIX**: any 4-register window passing `alice_coh_is_strict_camera`, which
  requires **five constraints, each to 1%**: forward (lane 3) unit length; right ⟂ forward, up ⟂
  forward, right ⟂ up; and the depth lane parallel to forward. The loose `SCALED-PERSP` class
  that let WorldIncidentLighting through is no longer used.
- Tested against the kitchen's real numbers: both SH lighting dumps are **rejected**, both of the
  game's own vs c0 camera matrices from the same frames are **accepted** `[verified-numerically
  2026-09-11, n=2 each]`.

**2. Dumps go to their own file**: `alice_vr_psdiag_capture.txt` beside the exe, opened in
**append** mode, so the file survives relaunches.

- **Header per launch**: date and time, **SHA-256 of the running `d3d9.dll`** (computed in-process
  with the Windows crypto API; it is the number `sha256sum` prints), coherent view ON/OFF, and the
  dump count already in the file.
- **Caps**: 8 dumps per launch, and none once 32 exist in the file (the header then says `FULL`).
- **Each `DUMP #n` records**:
  - frame and camtrace yaw/pitch, and why it qualified;
  - the upload's start register and count;
  - the bound pixel shader's **hash** (FNV-1a 32 over its bytecode up to the end token —
    reproducible offline from the shipped caches), size, declared VP register and constant count;
  - the window's 16 floats;
  - the last vs c0 camera VP and its age in frames;
  - **`BIT-IDENTICAL to the last vs c0 camera VP: YES/NO`** with per-register and transposed
    differences;
  - the coherent tier it would get with the current head offset. At rest the store is empty, which
    the line says, so read BIT-IDENTICAL instead;
  - vs c5.
- Written with `fflush` after every record, so a crash loses nothing.
- Shader hashes are only computed when the diagnostic is on.

**3. The first VP-shader-bound upload of each launch** gets one `EVENT` line in the capture file
(frame, camtrace yaw/pitch, start/count, full or PARTIAL, shader hash and VP register), even after
the dump budget is spent. It also goes to the main log.

The main log's `psdiag` counter line now reads `VP-shader-bound full=N PARTIAL=N | strict-camera=N
(bit-identical to vs c0: N) | capture file dumps N this launch, N before`.

## Tests `[verified-numerically 2026-09-11]`

`coherent_view_test` **103 checks, 0 failures** (14 new: strict test on hand-built, head-moved and
live camera matrices; rejection of both kitchen SH blocks, the transpose, a non-unit forward, a
non-perpendicular right/up and right/forward; the shader hash stopping at the real end token and not
at an end-token pattern inside a comment, matching an independent FNV-1a, ignoring trailing bytes,
and returning 0 with no end token). **18 mutants, all caught** (5 new + 7 + 6). vr_pose 64/64,
stereo, disparity 23/23 and the shadermap corpus check still green. The capture-file I/O and the
in-process SHA-256 are `[compile-verified]` only — nothing here has run in the game.

## What the capture will show when Tefa reaches a dynamic-light scene `[inferred-static]`

| capture shows | meaning |
|---|---|
| `EVENT` line, dumps `VP-SHADER-BOUND (full)`, `BIT-IDENTICAL: YES` | the pixel copy is the VP, sent whole; exact matching works once the head moves — the 11b failure was purely "no such draws" |
| `(full)` with `NO`, only register 3 differing | other origin; the ORIGIN tier handles it |
| `(full)` with `NO`, tiny differences everywhere | other rounding; the NEAR tier handles it |
| `PARTIAL` dumps | the copy arrives in pieces; the matcher (≥ 4 registers only) needs a per-register path — a small follow-up build |
| `STRICT CAMERA` dumps without any VP-bound shader | the VP is uploaded before its shader is bound; matching by value still works, binding-based guards would not |
| no `EVENT` line after a scene with visible dynamic lights | the light passes do not use this copy at all; revisit the census |
