# The scale-free `p00`, and a build whose hash check silently could not work

`/pd`, dev PC, 2026-09-08d. **The game was not launched. Nothing in this note has been run.**

Source: `staging/alice-madness-returns-vr/proxy-d3d9/`. Deployed `d3d9.dll` md5 `37293f99…`,
704,512 B, dated backup kept.

## The instrument

2026-09-08c derived `disparity(z) = p00·ipd·W/2 · (1/C − 1/z)`, confirmed its **shape** against the
convergence sweep to 97%, and showed the **amplitude** cannot come from the recovered
`p00 = 0.0022` — 380× short in two independent measurements. It left one question, and one number
that answers it.

That number is **scale-free**:

> **`|row0.xyz| / |row3.xyz|`**

Row 0 produces `clip.x`, row 3 produces `clip.w`. If the whole ViewProjection carries a uniform
scale `k`, then `row0.xyz = k·p00·right` and `row3.xyz = k·forward`, so **`k` cancels and the ratio
is `p00` exactly, whatever units the matrix is in.**

That property is not assumed — it is a host test. `stereo_ue3_test.c` builds a matrix with a known
`p00 = 0.836`, checks the ratio returns it, then multiplies the entire matrix by **1/380** and checks
that the raw `p00` is dragged down while **the ratio is unchanged**. It also refuses an orthographic
matrix rather than dividing by zero. `[verified-numerically 2026-09-08]`

Had the ratio *not* been scale-free, the number logged in-game would have been uninterpretable and
the launch wasted.

## What the proxy now logs

`alice_log_vp_diagnostic()` prints mathematical **row 0** and **row 3** in full, their xyz lengths,
and the ratio — **and states what the reading means**, so it does not depend on anyone having the
09-08c note open:

- **ratio ≈ 0.3–3** → an ordinary projection scale (it reports the implied hfov). The matrix is
  uniformly scaled, `p00_cached` is **not** the projection scale, `convergence` is not in `clip.w`
  units, and the 09-08c unit-mismatch hypothesis is **confirmed** — the fix is one scale factor.
- **anything else** → `p00` really is ~0.0022, the matrix is not merely scaled, the hypothesis is
  **disproved**, and the screen motion measured at R² 0.99948 did not come from our `S` as the code
  describes — which becomes the next question.

It fires on the **first perspective ViewProjection** (so a launch that never touches a hotkey still
answers the question) and again on **every F9** (the FOV changes in cutscenes and on aiming, so the
diagnostic is a property of the moment, not of the launch).

Cost on the hot path: one 64-byte `memcpy` on a path that already `memcpy`s the same bytes, and no
I/O except on those two events.

## ⭐ And a defect found on the way: this build could never have been hash-checked

`CONVENTIONS.md` tells a session to **rebuild and compare the hash** to decide whether a deployed DLL
is current. Doing exactly that here produced a mismatch — and the cause was not stale source.

**`build.sh` had no `-Wl,--no-insert-timestamp`, so the PE TimeDateStamp changes on every link.** Two
builds of *identical* source, back to back, hashed `56fe72c6…` then `f4fee746…`
`[verified-numerically 2026-09-08]`. **On this project the check silently could not work**, and a
session doing it properly would have concluded the deployed binary was stale when it was not.

So I checked it the way that does work — a byte diff:

> the deployed DLL differed from a build of its own committed source in **exactly six bytes**, at
> offsets 129–131 and 249861–249863: the PE header timestamp and the debug-directory timestamp.
> **The stamp was honest; only the proof was missing.** `[verified-numerically 2026-09-08]`

The flag is now in, and reproducibility is verified by the check that could not have passed before:
two builds of the same source now hash **identically** (`95069ae8…` twice).

⚠️ **This is the fifth project found with this defect.** It is worth treating as a default for any
new proxy rather than something to rediscover.

## Verification

- Builds clean, PE32/i386, export table intact. `[compile-verified 2026-09-08]`
- The stereo suite reports **ALL CHECKS PASSED** including the six new scale-free checks; the
  disparity model still reports **17 checks, 0 failures**.
- Deployed byte-identical to the build; `deployed.sh record` re-run for both DLLs.

**Nothing here has been run in the game.**

## The next launch

No setup at all — the diagnostic fires on its own. Launch, reach gameplay, quit, read
`Binaries\Win32\alice_vr_proxy_log.txt` and find `VP DIAGNOSTIC`.

| what it prints | what it means |
| --- | --- |
| `SCALE-FREE p00 ≈ 0.8` (hfov ~100°) | **the unit mismatch is confirmed.** The convergence slider is not in `clip.w` units; one scale factor in one place reconciles the amplitude, and the 09-08c model becomes usable for real convergence tuning. |
| `SCALE-FREE p00 ≈ 0.0022` | **the hypothesis is disproved.** `p00` really is tiny, and the question becomes what produced the measured screen motion, since it was not our `S` acting as documented. |
| `no perspective ViewProjection seen yet` | the game is not writing `c0..c3` on this path at all — which would contradict `vp_writes` climbing to 1,146,811, so read that counter in the same log before believing it. |

⚠️ It also settles, for free, whether `|row3.xyz|` is 1.0. That single number is the cleanest
statement of whether the matrix has a rigid view part.

## What is NOT established

- Which branch is true. **That is what the instrument is for.**
- That a confirmed unit mismatch would be fixable by a single scale factor. It is the natural fix if
  the scale is uniform; a non-uniform scale would need more, and the logged row lengths are what
  would show that.
- Anything new about the disparity measurements themselves. This session added an instrument and
  fixed a build; it did not revisit the 09-08c numbers.
