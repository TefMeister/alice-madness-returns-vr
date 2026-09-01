# 2026-09-01 — A truncation bug in the CTAB tool, the vs/ps split, and folding it all into the dossier

**Date:** 2026-09-01, dev machine, second `/pd` session of the day.
**The game was not launched, and nothing here has been run.**

---

## ⚠️ Read `2026-09-01b-the-real-toggle-is-Stereo3D-in-the-options-menu.md` first

**This note does not discover Alice's stereo path — the earlier `/pd` pass (commit `35e93ca`, 14:29)
did**, and it got the headline right: 45,832 CTAB tables, `NvStereoEnabled` at `c3` in 28,017
shaders, `NvStereoFixTexture` in 14,479, and the `Stereo3D` entry in the options list. I re-derived
those independently before realising the work existed, which is worth recording as a cheap
corroboration — two passes, same numbers — but the credit is not mine.

What follows is only what that pass did not have.

## 1. The tool it was written with truncates silently, and that capped its own sample

`flat-to-vr-RE-toolkit/tools/d3d9-ctab.py` was written earlier the same day. Two defects:

- **`find` stopped after `--limit 20` layouts and printed nothing to say so.** For
  `ViewProjectionMatrix` that turns **2,299 matching layouts / 6,557 shaders** into a confident-looking
  handful. I published "900 shaders" from it myself before catching it.
- **It parsed the CTAB `target` field but never surfaced it**, so `vs_3_0` and `ps_3_0` tables with
  the same constant layout were merged into one.

Both are fixed in the toolkit: target is now part of a table's identity and is printed, `find` always
reports matched-vs-shown, and `--limit 0` means no limit. **Anyone who ran `find` before 2026-09-01
and recorded a total from it should re-run.**

## 2. The vs/ps split — the register list in the earlier note is a vertex-shader list

With the target exposed, the picture changes in a way that matters for a hook:

| Constant | Target | Register | Shaders | Layouts | Exceptions |
|---|---|---|---|---|---|
| `ViewProjectionMatrix` | `vs_3_0` | **`c0`** (×4) | 2,431 | 576 | **none** |
| `CameraPosition` | `vs_3_0` | **`c4`** | 1,989 | 473 | **none** |
| `PreViewTranslation` | `vs_3_0` | **`c5`** | 486 | 195 | **none** |
| `ViewProjectionMatrix` | **`ps_3_0`** | **`c4`**, plus `c11` ×4 | 4,126 | 1,723 | — |
| `NvStereoEnabled` | `ps_3_0` | `c3` | 28,017 | 11,004 | none |

`[inferred-static 2026-09-01]` The earlier note lists `ViewProjectionMatrix c0 x4` and no pixel-shader
entry. **The pixel-shader copies at `c4` outnumber the vertex ones**, and were not visible through the
capped `find`. That is a real consequence, not bookkeeping: a stereo override written only at vertex
`c0` leaves 4,126 pixel shaders reading an un-offset view-projection, which is exactly the shape of
bug that produces correct geometry with wrong screen-space effects.

**Vertex and pixel constant registers are separate spaces.** Aggregated together, `c0` looks like the
minority case and the obvious conclusion is the wrong one.

Related display trap: the tool prints *sampler* registers with a `c` prefix, so
`NvStereoFixTexture sampler c1` is `s1` and does **not** collide with `ScreenPositionScaleBias` at
float4 `c1`.

## 3. What I could add: it is unanimous

The earlier pass showed one representative table. Across the whole cache, **every vertex shader that
references the view-projection puts it at `c0` — 576 independent layouts, no counter-example** — and
`CameraPosition`/`PreViewTranslation` are likewise unanimous at `c4`/`c5`. That is what makes this a
register *map* rather than a sample.

It also means Alice independently reproduces `enslaved-vr`'s map (`c0`/`c4`/`c5`) from a **different
class of evidence**: Enslaved read its shipped `.usf` *sources*, Alice its compiled shader
*reflection*. Filed to the cross-engine library to raise that claim from n=1 to n=2.

## 4. The dossier had none of it

**The earlier pass wrote `modding-notes/` and `claude-memory` but never touched
`engine-research/ENGINE-DOSSIER.md`** — which is the distilled, durable doc the next session actually
reads first. It still contained zero mention of CTAB or `NvStereo`, and still carried this warning:

> *"`c0` is probably NOT a simple shared view-projection register … expect the harder
> per-object-WVP decomposition case instead."*

That was inherited from Enslaved's early histogram and **was withdrawn at the source the same day**
(`enslaved-vr/modding-notes/2026-09-01-shared-viewprojection-confirmed-at-c0.md`). It was actively
telling the next session to expect the hard case. §6 of the dossier is now written up, and the
paragraph is marked as history rather than deleted so the reasoning stays visible.

## What is NOT established

- That writing `c0` steers the picture. `c0` is where the matrix arrives.
- The layout `NvStereoFixTexture` is expected to hold — still the open item from the earlier note.
- Anything about `UpdateViewTarget`; the UnrealScript half is untouched.

## The check to run when this game is next up

Override vertex `c0` with a deliberate large yaw (~45°) and watch **whether all opaque geometry
rotates together**.

- **All of it rotates** → shared-VP model holds; proceed to per-eye offsets at `c0`.
- **Geometry rotates but screen-space effects do not** → the `ps_3_0` `c4` copies need the same
  offset. Expected, given the table above; fix rather than rethink.
- **Some opaque passes ignore it** → the shared-VP model is incomplete and the *derivation* is wrong,
  not a value needing tuning.
- **Nothing moves** → the proxy is not reaching `SetVertexShaderConstantF`; a hooking failure, not a
  camera finding.
