# SteamStub identified (the scan is `[PD]` again), and the per-eye maths verified — but it is a TRANSPOSE of Alan Wake's

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
