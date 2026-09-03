# SteamStub identified, the NVAPI scan RUN AND ANSWERED (Automatic), and the per-eye maths verified — but it is a TRANSPOSE of Alan Wake's

> **Reading order note.** Sections 1–4 were written before the user approved fetching Steamless, so
> section 1 ends by saying the scan "moves back to `[PD]`". **It then ran the same session** — see
> the addendum at the end, which answers it: **the mode is AUTOMATIC**. The earlier text is left as
> written rather than retro-edited, because the gating sequence is part of the record.

**Session:** `/pd`, dev PC, 2026-09-03. **The game was not launched, and nothing here has been
run.** Everything below is read off files already on this disk, or compiled and run on the host.

## 1. 🚦 GATE DROP — the NVAPI scan is back to `[PD]`

`/gr` proposed that the `.bind` wrapper is **SteamStub**, Valve's own DRM applied at upload, and
that unpacking is therefore a *static* step rather than the runtime memory dump the dossier assumed.
**Confirmed here, in the stub's own code.**

The SteamStub v3.x header magic **`0xC0DEC0DF`** sits at `.bind + 0x4A0` (VA `0x016614A0`), and the
surrounding instructions are the stub validating it:

```
8B 4D F8                 mov ecx, [ebp-8]
81 79 04 DF C0 DE C0     cmp dword [ecx+4], 0xC0DEC0DF
74 0A                    je  ...
```

The entry point at `0x01661310` is a textbook stub prologue — `call $+5`, push-all, `and esp,-16`.
`[inferred-static 2026-09-03]`

**Consequence:** `.text` can be decrypted without running the game, with a public open-source
unpacker (Steamless covers v3.x; this exe is PE32, in range). That moves the whole NVAPI
Direct-vs-Automatic scan from `[FLAT]` back to **`[PD]`** — the runtime dump is now only a fallback.

### ⚠️ The witness `/gr` suggested FAILED, and that is worth recording

The drop proposed a cheap second witness: *is `steam_api.dll` in the import table?* It is **not** —
and there is no `steam_api.dll` anywhere in the install, and **no "steam" string anywhere in the
exe** `[measured 2026-09-03]`.

That is **not** evidence against SteamStub. It means the game has no Steamworks *API* integration at
all, only the DRM wrapper applied at upload — plausible for an EA-published title on Steam. But it
would read as a refutation to anyone re-running it, so it is now a named dead end in §11. The header
magic is the witness that actually carries the claim.

## 2. ✅ The per-eye maths is verified — and the implementation is NOT what the dossier's wording implies

The queued item was: *verify the clip-space per-eye maths numerically before anything is built on
it.* Doing so turned up something worth more than the verification.

**Alice's `ViewProjectionMatrix` is `D3DXPC_MATRIX_COLUMNS`.** `alan-wake-vr`'s matrices are
`MATRIX_ROWS`. Established two independent ways, the same discipline used on Alan Wake:

1. **CTAB type metadata** in `RefShaderCache-PC-D3D-SM3.upk` — `MATRIX_COLUMNS`, `4×4`, at
   `vs_3_0 c0 ×4` (2,431 shaders) and `ps_3_0 c4 ×4` (4,122).
2. **The shipped bytecode.** The simplest vertex shader carrying it, in full:

   ```
   mul r0, c1, v0.y
   mad r0, c0, v0.x, r0
   mad r0, c2, v0.z, r0
   mad r0, c3, v0.w, r0
   mov o0, r0
   ```

   `clip = c0·v.x + c1·v.y + c2·v.z + c3·v.w` — the row-vector form `mul(v, M)`, with **no `dp4`
   against `c0` anywhere in it.** `[inferred-static 2026-09-03, two independent reads]`

**So `clip.x` is the `.x` LANE across all four registers, not `dot(c0, v)`**, and the edit is:

```
for i in 0..3:  c[i].x += S · c[i].w        then        c3.x -= S · C
```

against Alan Wake's `c0 += S·c3` then `c0.w -= S·C`. **Same algebra, transposed storage, completely
different register writes.**

The dossier's own phrasing — `row0' = row0 + S·row3` — is **correct as mathematics and misleading as
instructions**: in this layout the mathematical row 0 is a lane, not a register. Anyone implementing
it literally, or porting the Alan Wake code that looks identical, would mix columns.

**The suite proves that rather than warning about it.** It transplants the Alan Wake implementation
verbatim and shows it diverges (`ndc.x +0.355` vs `+0.324`) and **corrupts `clip.w`** (1388.87 vs
1656.58) — the signature of mixing columns rather than shearing. `clip.w` is untouched by the
correct form.

### The `c5` immunity is demonstrated, not assumed

The whole reason clip space was chosen is `PreViewTranslation` at `c5`: UE3 hands vertices to the
shader in translated world space, and an offset applied in world or view space that ignores it
**looks right near the world origin and drifts as the player moves away** — passing its first test
and failing later, far from where it was written.

Every case in the suite therefore runs at `PreViewTranslation` of **0, 1,000 and 250,000 units**,
and the results are identical to the true off-axis pair at all three.

### How it was verified

Ground truth is built the other way — an explicit asymmetric frustum applied to a **physically
translated eye**, in plain matrix maths — while the thing under test is evaluated by **simulating the
shader's own accumulation**, so nothing in the comparison assumes the register-to-lane mapping the
code uses.

- **54 configurations** (3 IPDs × 3 convergences × 3 PreViewTranslations × both eyes) × 5 world
  points, matching on `clip.x`, `clip.y`, `clip.w` and `ndc.x`.
  `[verified-numerically 2026-09-03, n=54 configurations]`
- A register round-trip check first, so the column-major storage is known to reproduce plain matrix
  maths before anything is compared through it.
- Convergence property, parallax sign and falloff (near 50u `+0.112`, far 3000u `−0.020`), `p00`
  recovered from the matrix, orthographic and `C ≤ 0` refused, `S = 0` bit-identical to mono.
- **Six mutants, all caught, control passes** — including putting the constant term on Alan Wake's
  register (514 failures), which is precisely the porting error.
- Clean under `-Wall -Wextra -Wpedantic -Wshadow -Wconversion`, host and `i686-w64-mingw32`.
  `[compile-verified 2026-09-03]`

Code: `staging/alice-madness-returns-vr/proxy-d3d9/src/stereo_ue3.{h,c}`, with the full account in
that folder's `README-stereo.md`.

## 3. Smaller things folded in from the same inbox

- **F2 is patch-only, settled without a launch.** MadnessPatch 3.0.0+ adds `EnableConsole` "bound to
  F2" as its own feature `[reported]`. On the stock game, try Tilde — UE3's shipping default. The
  dossier's "worth testing both live" question is resolved.
- **A confidence tag corrected as it was folded in.** `/gr`'s earlier drop tagged its NVAPI id table
  `[verified-static …]`, which is not one of the eight vocabulary names and therefore counts as
  untagged. Written into the dossier as `[reported 2026-09-03, n=3 independent reads]` — first-party,
  from NVIDIA's published `nvapi_interface.h`, but a document read rather than a measurement.

## 4. What is NOT established

- **The pixel-stage half is not done.** `ViewProjectionMatrix` is also `ps_3_0 c4 ×4` in 4,122
  shaders, but **`ps c4` is `WorldToViewMatrix` (4×3) in 135 others**, so a blind `ps c4` write
  corrupts those. It needs a per-shader register map — the `ctab.c` approach built for
  `alan-wake-vr` today — not a fixed register.
- **`p00` recovery assumes nothing non-rigid is baked in after the projection.** True for Alice's
  `c0` (ViewProjection, with `LocalToWorld` separate at `c6`/`c10`/`c231`); not for a fused matrix.
- **The RHI re-upload is the most likely runtime failure.** The dossier records `c0` receiving **47
  uploads per frame** — UE3 re-applying the reserved view registers around bound-shader-state
  changes. That means **our write may simply be overwritten** unless it is applied on *every* upload
  rather than once per frame. If both eyes come out identical in the first live test, this is the
  first thing to suspect, and it is **not** evidence against the maths.
- Untested until something runs: that the projection is left-handed with `clip.w = view.z`, and
  which engine unit the IPD is in (UE3 convention ≈ 1 unit = 1–2 cm, so ~6.5 is the starting guess).

**Diagnostics.** Vertical separation instead of horizontal ⇒ the wrong lane (`.y` not `.x`).
Geometry correct near spawn and drifting far from it ⇒ something is still acting in world space,
i.e. the `c5` trap after all. Both eyes identical ⇒ most likely the RHI re-upload above.


---

# ADDENDUM, same session — the user approved fetching Steamless, so the scan RAN. **The mode is AUTOMATIC.**

**Still no launch.** A **copy** of the exe was unpacked on disk; the shipped binary was never
touched and the game was never started.

## The unpack

Steamless v3.1.0.5 (`github.com/atom0s/Steamless`, sha256 `e3e2d22e098ff3fb…` on the release zip)
independently identified the file as **SteamStub Variant 3.1 (x86)** — matching the static call made
earlier from the `0xC0DEC0DF` magic alone. Validated before trusting anything from it:

| | packed | unpacked |
| --- | --- | --- |
| `.text` entropy | 8.00 | **6.71** |
| `.text` `CC` padding runs | 0 | 1 |
| `.bind` section | present | removed |
| entry point | `0x01661310` (in `.bind`) | **`0x00FAEF67`** (the original OEP in `.text`) |
| `.text` disassembles | no | **yes — clean MSVC with `int3` padding** |

## The result, with the control that makes it mean something

| function | id | unpacked | **still-packed control** |
| --- | --- | --- | --- |
| `NvAPI_Initialize` | `0x0150E828` | **1** ✅ | 0 |
| **`Stereo_SetActiveEye`** | `0x96EEA9F8` | **0** | 0 |
| **`Stereo_SetDriverMode`** | `0x5E8F0BEC` | **0** | 0 |
| `Stereo_CreateHandleFromIUnknown` | `0xAC7E37F4` | 1 | 0 |
| `Stereo_Activate` | `0xF6A1AD68` | 1 | 0 |
| `Stereo_GetSeparation` | `0x451F2134` | 1 | 0 |
| `Stereo_GetConvergence` | `0x4AB00934` | 1 | 0 |
| `Stereo_GetEyeSeparation` | `0xCE653127` | 1 | 0 |
| `Enable` / `SetSeparation` / `SetSurfaceCreationMode` | — | 0 | 0 |

**I kept the packed copy and scanned it too, deliberately.** Its column is all zero *including the
positive control* — so that scan could not have produced a positive. That is exactly the false
negative the 2026-09-02 note warned about, and it is now demonstrated side by side instead of
argued. A negative result is only evidence if the test could have returned a positive; here both
states are on the page.

**All six live references sit in one 825-byte function** (`0x00E65663`–`0x00E6599C`, unpacked
image): init → create handle → activate → **read** separation, convergence, eye separation.
**Three getters and no setters at all** — `SetSeparation` is 0 here where Alan Wake had 1, so Alice
is an even purer consumer.

## ⛔️ Verdict: AUTOMATIC — the same conclusion as `alan-wake-vr`, reached independently

The game activates 3D Vision and then reads back what the driver decided. It never sets driver mode
or active eye, so **it never takes the eyes off the driver**. `NvStereoEnabled` (`ps c3`, 28,017
shaders) and `NvStereoFixTexture` (14,479) are **consumers of driver-published values, not producers
of an eye offset**. `[inferred-static 2026-09-03]`

**This also resolves a caveat that had been recorded as genuinely ambiguous.** Epic's page is titled
*"UE3 and NVIDIA 3D Vision **Direct**"*, which pointed one way, while an eye-sign channel in a
texture is the signature of the Automatic pattern, which pointed the other. **The texture reading
was right**; the page title describes what UE3 can support, not what this title shipped.

## Why this is good news rather than a setback

`/gr` pre-committed the outcomes, and this is the one where **the plan does not change**: *"no
callers on either, with callers on Activate/getters ⇒ Automatic (same as Alan Wake; the render-twice
+ own-texture plan is unchanged)."*

And it is better than merely "unchanged". Because the game **reads** separation and convergence from
the driver and feeds them into its own shaders, a proxy that supplies those values itself — writing
`ps c3` and binding its own `NvStereoFixTexture` — drives a stereo path **the shipping shaders
already implement, in 28,017 of them**. The discontinued NVIDIA driver is not required for that. The
existing `[PD]` plan is now confirmed rather than hypothetical.

## Housekeeping

The unpacked binary is **game content and is deliberately not committed**. It regenerates in one
command from a copy, so nothing is single-copy. The scan output — ids, counts and addresses, which
are interface metadata — is preserved at
`dev-archive/recon/2026-09-03-steamstub-and-matrix-layout/nvapi-direct-vs-automatic-scan.txt`.

⚠️ Note for anyone reading those addresses: they are in the **unpacked** image. The shipped exe's
`.text` is encrypted, so they do not correspond to on-disk addresses of the retail binary.
