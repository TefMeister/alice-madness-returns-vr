# Engine Dossier — Alice: Madness Returns (Unreal Engine 3)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 done — static recon complete, external research folded in. No DRM found (reconciled: EA Cuckoo DRM was present historically, removed via a Jan 2022 patch — a dated, documented history, not a lucky negative result). **This is the strongest VR-feasibility case in the whole portfolio: vorpX already delivers true Geometry 3D + working motion-controller emulation for this exact game**, plus a mature open-source community patch (MadnessPatch) that already exposes the console, disables VR-harmful mouse smoothing, and confirms a real framerate-dependent-physics risk. · **VR-readiness verdict:** genuinely the most promising front so far — no environmental blockers, no DRM, the best third-party feasibility signal of any project here, AND a real chance the developers' own shipped code already solves the hard per-eye camera problem (see §6). Proxy `d3d9.dll` is built, **deployed, and live-verified** (2026-08-25) — see §4.

## 1. Identity
- Game / build / version: Alice: Madness Returns (2011, Spicy Horse Games, published by Electronic Arts), Steam release. Exe: `Binaries\Win32\AliceMadnessReturns.exe` (17.4 MB).
- Platform & store; unofficial port? (extra fragility/legal notes): Steam (PC). No known unofficial-port concerns.
- Legitimacy: owned copy confirmed.

## 2. Engine lineage
- Family / base engine and how it was modified: **Unreal Engine 3, confirmed** — standard UE3 `Binaries\Win32\` + `Core\` folder layout, `Direct3DCreate9` present. Developer "Spicy Horse Games" confirmed via an internal string (`unlimited.ky.SpicyHorse.Alice2...`, likely a Steam stat/achievement key). Modification depth not yet investigated.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.): **NVIDIA PhysX + APEX** confirmed (`PhysXCore.dll`, `PhysXExtensions.dll`, `PhysXCooking.dll`, `PhysXDevice.dll`, `NxCharacter.dll`, `APEX_Clothing_x86.dll`, `APEX_Clothing_Legacy_x86.dll`, `APEX_Destructible_x86.dll`, `APEX_Destructible_Legacy_x86.dll`, `ApexFramework_x86.dll`) — cloth and destructible-mesh physics specifically called out, matching UE3's well-known standard PhysX/APEX integration of this era. **CUDA present** (`cudart.dll`, `cudart32_30_9.dll`) — likely GPU-accelerated PhysX. **Bink** for video (`binkw32.dll`, same middleware as Mad Max and Prince of Persia). **Ogg Vorbis** (`ogg.dll`, `vorbis.dll`, `vorbisenc.dll`, `vorbisfile.dll`) plus XAudio2-family (`X3DAudio1_7.dll`, `XAPOFX1_4.dll`) for audio — UE3's standard audio stack. Compiled with **VS2008** (`MSVCR90.dll`).
- Distinctive file formats / build tags / symbol naming: not yet investigated (UE3's standard `.upk`/`.u` package formats are a reasonable expectation but unconfirmed for this specific title).

## 3. Binary & memory
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): **32-bit** (PE32, `coff-i386`). Standard-ish section layout (`.text`/`.textidx`/`CONST`/`.rdata`/`.data`/`.rsrc`/`.reloc`/`.bind`) — `.textidx` is a known, benign UE3-toolchain section, not a red flag (no giant opaque blob, no Denuvo/anti-tamper-shaped structure). **`.bind` is NOT a UE3 artefact: it is the SteamStub v3.x DRM stub section, and it holds the entry point** (§4, §6). 17.4 MB.
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: **Direct3D 9 confirmed** — `d3d9.dll` statically imported, literal string `Direct3DCreate9` present.
- Developer console / cvar system present? how opened?: **Confirmed reachable (external-research, 2026-08-25): "Developer console access (F2)" is documented as an explicit feature by the MadnessPatch community patch.** ✅ **Settled 2026-09-03 (`/gr`): F2 is PATCH-ONLY.** MadnessPatch 3.0.0+ adds `EnableConsole` "bound to F2" as its own feature `[reported, release notes]`. **On the stock game try Tilde (`~`)**, UE3's shipping default. So the old "worth testing both live" is resolved without a launch.

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **⚠️ READ NARROWLY — "no DRM" means EA's Cuckoo is gone; the shipping binary IS wrapped in Valve's own SteamStub.** Corrected 2026-09-03: `.bind` holds the entry point and `.text` is encrypted at rest, and the **SteamStub v3.x header magic `0xC0DEC0DF` is verified inside the stub's own validating `cmp`** (§6). That is a **packaging wrapper, not an anti-tamper system** like Denuvo — it does not fight a debugger, and a public open-source unpacker (Steamless) restores `.text` for static analysis without running the game. Injection is unaffected: the `d3d9.dll` proxy is live-verified on this build. `[inferred-static 2026-09-03]` The Cuckoo history below remains accurate and is unchanged. **No DRM found — reconciled with a real, dated history (external-research, 2026-08-25), not just a lucky static result.** The original 2011 release used **"EA Cuckoo"**, an online-authentication DRM tied to EA's own activation servers. EA delisted the game entirely in September 2016 after accidentally distributing already-used Steam keys (refunding affected buyers rather than replacing keys), leaving existing owners with server-dependent DRM on a no-longer-sold title. The game was later **relisted on Steam, and a January 14, 2022 patch removed EA Cuckoo authentication DRM entirely** from that build. Our own static recon (zero Denuvo/SecuROM/StarForce/Cuckoo/link2ea strings) is fully consistent with this — **this is a "DRM was present historically, current build is clean" case, same pattern as Prince of Persia (2008), not a lucky negative result.** Worth being glad about specifically given this is EA-published (same publisher as Burnout Paradise, which still needs the EA App) — this title evidently doesn't carry that requirement anymore. Not yet tested live.
- Attach workflow that works: not yet tested live, but no static evidence predicts a block.
- Injection vector that works (proxy DLL name / injector / framework): **✅ LIVE-VERIFIED (2026-08-25), a from-scratch `d3d9.dll` proxy**, matching this portfolio's Psychonauts and Prince of Persia precedent. **First deploy attempt failed the game outright** — see `staging/alice-madness-returns-vr/proxy-d3d9/README.md` for the full story: `AliceMadnessReturns.exe` statically imports *two* functions from `d3d9.dll` (`Direct3DCreate9` and `D3DPERF_SetOptions`, a real D3D9 perf-marker export), not just one — a proxy exporting only `Direct3DCreate9` left Windows' loader unable to resolve the exe's import table at all, so the process exited before running any code (zero log output, "ran ~2 seconds then stopped"). Isolated via a clean control test (DLL removed → game launched fine), fixed by adding the second forwarding wrapper, redeployed — **confirmed working cleanly on the retest**: `Direct3DCreate9` called twice (SDKVersion=0x20 both times), `D3DPERF_SetOptions` called once (dwOptions=0x1), game ran for ~5 minutes of real play. **Lesson for future D3D9 proxies in this portfolio: check the exe's actual per-function import list for the target DLL, not just whether the DLL name appears in the import table** — Prince of Persia's exe only needed `Direct3DCreate9`, but that isn't guaranteed for every D3D9 title.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)

### ⛔️ THE EXE'S `.text` IS ENCRYPTED AT REST — NO STATIC CODE SCAN ON THIS BINARY CAN RETURN A TRUE NEGATIVE (2026-09-02, `/pd`, no launch)

**Read this before planning any static work on `AliceMadnessReturns.exe`.** `.text` measures
**entropy 8.00** (the ceiling), the **entry point is at `01661310` inside a `.bind` wrapper section**
(entropy 7.98) rather than in `.text`, `.text` does not disassemble, and it contains **zero `CC`
padding runs** — impossible for a real MSVC code section. `[measured 2026-09-02]` A wrapper decrypts
it at load.

> #### ✅ THE WRAPPER IS IDENTIFIED: **SteamStub v3.x**, and unpacking is a STATIC step (2026-09-03)
>
> `/gr` proposed SteamStub from the section signature; this session confirmed it **in the stub's own
> code**. The v3.x header magic **`0xC0DEC0DF`** is present at `.bind + 0x4A0` (VA `0x016614A0`), and
> the surrounding instructions are the stub validating it:
> `mov ecx,[ebp-8]` / `cmp dword [ecx+4], 0xC0DEC0DF` / `je …`. The entry point at `0x01661310` is a
> textbook stub prologue (`call $+5`, push-all, `and esp,-16`). `[inferred-static 2026-09-03]`
>
> ⚠️ **The cheap second witness `/gr` suggested — `steam_api.dll` in the import table — FAILED, and
> should not be re-run.** There is no `steam_api.dll` in the import table, no `steam_api.dll`
> anywhere in the install, and **no "steam" string anywhere in the exe**. That is not evidence
> against SteamStub: it means the game has no Steamworks *API* integration at all, only Valve's DRM
> wrapper applied at upload — plausible for an EA-published title on Steam. The header magic is the
> witness that actually carries the claim. `[measured 2026-09-03]`
>
> **Consequence: `.text` can be decrypted without running the game.** Public open-source unpackers
> cover SteamStub v3.x — [Steamless](https://github.com/atom0s/Steamless) (this exe is PE32, in
> range) and [Steamstub-v3-Unpacker](https://github.com/GHFear/Steamstub-v3-Unpacker). **Work on a
> COPY; never overwrite the shipped exe**, and expect the unpacked binary **not to launch** (it still
> wants the environment the stub set up) — that is the expected outcome, not a failed unpack.
> `[reported 2026-09-03]`

- **Consequence:** strings, `push imm32` operands and xrefs in `.text` are all unreadable off disk.
  A scan that finds nothing has found nothing *about the game* — the test could not have produced a
  positive result.
> ### ✅✅ SETTLED 2026-09-03 — **THE MODE IS AUTOMATIC.** The scan ran, on an unpacked copy, with the game never launched.
>
> A **copy** of the exe was unpacked with Steamless v3.1.0.5, which independently identified it as
> **SteamStub Variant 3.1 (x86)** — matching the static call above. Unpack validated before trusting
> anything from it: `.text` entropy **8.00 → 6.71**, `CC` padding **0 → 1** run, `.bind` removed,
> entry point moved `0x01661310` (`.bind`) → **`0x00FAEF67`** (the original OEP in `.text`), and
> `.text` now disassembles as clean MSVC code. `[measured 2026-09-03]`
>
> | function | id | unpacked | **still-packed control** |
> | --- | --- | --- | --- |
> | `NvAPI_Initialize` | `0x0150E828` | **1** ✅ positive control | 0 |
> | **`Stereo_SetActiveEye`** | `0x96EEA9F8` | **0** | 0 |
> | **`Stereo_SetDriverMode`** | `0x5E8F0BEC` | **0** | 0 |
> | `Stereo_CreateHandleFromIUnknown` | `0xAC7E37F4` | 1 | 0 |
> | `Stereo_Activate` | `0xF6A1AD68` | 1 | 0 |
> | `Stereo_GetSeparation` | `0x451F2134` | 1 | 0 |
> | `Stereo_GetConvergence` | `0x4AB00934` | 1 | 0 |
> | `Stereo_GetEyeSeparation` | `0xCE653127` | 1 | 0 |
> | `Stereo_Enable` / `SetSeparation` / `SetSurfaceCreationMode` | — | 0 | 0 |
>
> **The packed column is all zero including the positive control** — that scan could not have
> produced a positive, which is precisely the false negative the 2026-09-02 note warned about, now
> demonstrated side by side rather than argued.
>
> **All six live references sit in ONE 825-byte function** (`0x00E65663`–`0x00E6599C` in the
> unpacked image): init → create handle → activate → **read** separation, convergence and eye
> separation. **Three getters and no setters at all** — `SetSeparation` is 0 here where Alan Wake
> had 1, so Alice is even more purely a consumer. `[inferred-static 2026-09-03]`
>
> **⛔️ Consequence — the same verdict as `alan-wake-vr`, reached independently: the game never takes
> the eyes off the driver.** It activates 3D Vision and reads back what the driver decided.
> `NvStereoEnabled` (`ps c3`, 28,017 shaders) and `NvStereoFixTexture` (14,479) are therefore
> **consumers of driver-published values, not producers of an eye offset**.
>
> ✅ **This CONFIRMS the existing plan rather than changing it** — exactly the outcome `/gr`
> pre-committed to: *"no callers on either, with callers on Activate/getters ⇒ Automatic (same as
> Alan Wake; the render-twice + own-texture plan is unchanged)."* And it is better news than it
> sounds: because the game *reads* separation and convergence and feeds them to its own shaders, a
> proxy that supplies those values itself — writing `ps c3` and binding its own stereo texture —
> drives a stereo path the shipping shaders already implement. The discontinued NVIDIA driver is not
> required. Evidence: `dev-archive/recon/2026-09-03-steamstub-and-matrix-layout/nvapi-direct-vs-automatic-scan.txt`.
>
> ⚠️ **The unpacked binary is GAME CONTENT and is deliberately not committed.** Regenerate in one
> command when needed; work on a copy, never the shipped exe.

- **🚦 The scan's history, kept because the gating lesson is the point (re-gated `[FLAT]` → `[PD]` 2026-09-03, then answered the same day).** `/gr`'s method
  (`SetActiveEye` `0x96EEA9F8`, `SetDriverMode` `0x5E8F0BEC`, control `NvAPI_Initialize`
  `0x0150E828`) is sound and works on Alan Wake's unencrypted exe. It was gated `[FLAT]` on
  2026-09-02 because the remedy looked like a runtime memory dump; **it is not — unpack a copy with
  Steamless first, statically.** The runtime dump (`static-disasm.py --raw`, the Manhunt route) is
  now only the fallback if the variant is unrecognised.
  - **The discriminator ids are already settled and need no re-checking**: `0x96EEA9F8` →
    `NvAPI_Stereo_SetActiveEye`, `0x5E8F0BEC` → `NvAPI_Stereo_SetDriverMode`, read out of NVIDIA's
    published `nvapi_interface.h` three times by two session types, with two positive controls inside
    the query. `[reported 2026-09-03, n=3 independent reads]` — first-party, from NVIDIA's own
    published header, but a document read rather than a measurement.
  - ⚠️ **Re-run the positive control on the unpacked file before believing any result**:
    `NvAPI_Initialize` `0x0150E828` must be found. That control is what stopped the 2026-09-02 scan
    being misread as a clean "Automatic", and it is what will stop a *partial* unpack being misread
    the same way.
- **It also withdraws an inference:** the 2026-09-01 "the exe has essentially no stereo strings, so
  the integration lives in the engine layer" reasoning. The premise is an artefact of encryption.
  `[disproved 2026-09-02]` as an inference.
- **`.rdata`/`.data` are NOT encrypted** and stay fully readable — which is where the table below
  came from, and why the shader-cache work is unaffected.
- **Injection is unaffected** — the `d3d9.dll` proxy is live-verified on this build.
- ⚠️ **§4's "no DRM" needs reading narrowly:** EA's Cuckoo really is gone, but the shipping binary is
  **wrapped**. Correction, not contradiction.

#### The NVAPI interface table is readable — and it does NOT decide Direct vs Automatic

A **105-entry** table at `013d452c` (`{u32; u32; u32 interfaceId}`), ids matching NVIDIA's published
`nvapi_interface.h`. **27 are `NvAPI_Stereo_*`** (Enable/Disable/IsEnabled, CreateHandleFromIUnknown,
DestroyHandle, Activate/Deactivate/IsActivated, Get/Set/Increase/Decrease Separation and Convergence,
GetEyeSeparation, Get/SetFrustumAdjustMode, ReverseStereoBlitControl, SetNotificationMessage,
Capture{Jpeg,Png}Image, and the four configuration-profile-registry calls). **`SetActiveEye` and
`SetDriverMode` are absent.**

**⚠️ Do not read that absence as "Automatic".** The same table carries `NvAPI_VIO_*` (Quadro SDI),
`GPU_GetECC*`, `Mosaic` and `I2CRead/Write` — functions no game calls — so it is **the linked NVAPI
SDK's fixed table, not this game's usage.** The positive control settles it: **`NvAPI_Initialize` is
missing from the table too**, and the game certainly calls it (`nvapi.dll` and
`nvapi_QueryInterface` sit in readable `.rdata` at `0131ba4c`). `[inferred-static 2026-09-02]`
Full decode: `dev-archive/recon/2026-09-02-text-is-encrypted-and-nvapi-table/`.

#### Register facts re-derived 2026-09-02, with two refinements

Every published number reproduces `[verified-numerically 2026-09-02]` (45,832 tables = 43,025
`ps_3_0` + 2,807 `vs_3_0`; `ViewProjectionMatrix` `vs_3_0` `c0 ×4` in 2,431, no exceptions;
`CameraPosition` `vs_3_0` `c4` 1,989; `PreViewTranslation` `vs_3_0` `c5` 486; `NvStereoEnabled`
`ps_3_0` `c3` 28,017). Two things the earlier pass did not separate:

- **`NvStereoFixTexture` is not only `s1`:** `s1` 14,221, **`s3` 202, `s0` 46, `s2` 10.** A proxy
  binding a stereo texture must key off the sampler each shader declares — assuming `s1` silently
  mis-feeds 258 shaders.
- **`ps_3_0` `c4` is a slot with two meanings:** `ViewProjectionMatrix` `c4 ×4` in 4,122 shaders, but
  **`WorldToViewMatrix` `c4 ×3` in 135**. Writing `ps c4` blind corrupts those 135.

#### ✅ Per-eye maths: VERIFIED 2026-09-03 — and the matrix is stored TRANSPOSED from Alan Wake's

NVIDIA's `x' = x + S·(w − C)` with `S = (f/aspect)·t/C` is confirmed correct, over **54
configurations** against ground truth built the other way (explicit asymmetric frustum + a
physically translated eye), with the thing under test evaluated by simulating the shader's own
accumulation. `[verified-numerically 2026-09-03, n=54 configurations]` Code:
`staging/alice-madness-returns-vr/proxy-d3d9/src/stereo_ue3.{h,c}`.

**✅ The `c5` immunity is demonstrated, not assumed.** Every case runs at `PreViewTranslation` of
**0, 1,000 and 250,000 units** and agrees at all three — so the drift trap below genuinely cannot
bite the clip-space form.

⚠️ **BUT THE IMPLEMENTATION IS A TRANSPOSE OF `alan-wake-vr`'s, AND COPYING THAT CODE HERE PRODUCES
GARBAGE.** Alice's `ViewProjectionMatrix` is **`D3DXPC_MATRIX_COLUMNS`** (Alan Wake's matrices are
`MATRIX_ROWS`), established two ways: the CTAB type metadata, and the shipped bytecode, whose
simplest vertex shader carrying it is

```
mul r0, c1, v0.y  ;  mad r0, c0, v0.x, r0  ;  mad r0, c2, v0.z, r0
mad r0, c3, v0.w, r0  ;  mov o0, r0
```

— i.e. `clip = c0·v.x + c1·v.y + c2·v.z + c3·v.w`, the row-vector form `mul(v, M)`, with **no `dp4`
against `c0` anywhere**. `[inferred-static 2026-09-03, two independent reads]` So **`clip.x` is the
`.x` LANE across all four registers, not `dot(c0, v)`**, and the edit is:

```
for i in 0..3:  c[i].x += S · c[i].w        then        c3.x -= S · C
```

against Alan Wake's `c0 += S·c3` then `c0.w -= S·C`. **The wording "row0' = row0 + S·row3" used here
before is correct as MATHEMATICS and misleading as INSTRUCTIONS** — in this layout the mathematical
row 0 is a lane, not a register. The test suite transplants the Alan Wake implementation verbatim
and shows it diverges (`ndc.x +0.355` vs `+0.324`) **and corrupts `clip.w`**, so the distinction is
falsifiable rather than asserted. Six mutants, all caught, control passes.

**✅ THE PIXEL STAGE IS ANSWERED 2026-09-03 — and NOT the way it was queued.** The plan was to
extend the matrix edit to `ps c4`. **Do not.** Two measured reasons:

1. **`ps c4` is wildly overloaded** — far worse than this dossier previously warned. Occupants
   include `UniformPixelVector_1` (14,557 shaders), `UniformPixelVector_0` (5,080),
   `WorldIncidentLighting` (4,130), `ViewProjectionMatrix` (4,122),
   `LightColorAndFalloffExponent` (2,843), `LightMapScale` (2,348)… **A blind `ps c4` write corrupts
   roughly 33,000 shaders, not the 135 recorded here before.** `[inferred-static 2026-09-03]`
2. **The shipped pixel shaders ALREADY apply the shear themselves.** From the bytecode:
   ```
   mad   r0.xyz, c4.xyww, v2.x, r0   ; clip = ViewProjectionMatrix * worldpos
   ifc   c3., -c3.x                  ; if (NvStereoEnabled)
     texld r1, c0.yzzw, s1           ;   read NvStereoFixTexture
     add   r1.y, r0.w, -r1.y         ;   w - convergence
     mad   r0.z, r1.x, r1.y, r0.x    ;   x + separation*(w - convergence)
   ```
   That is NVIDIA's `x' = x + S·(w − C)`, compiled into retail. **Shearing `ps c4` too would
   DOUBLE-APPLY it.** `[inferred-static 2026-09-03]`

**The stages are asymmetric, and that is the whole design.** `NvStereoEnabled` is in **28,017 of
43,025 pixel shaders, always at `ps c3`, zero exceptions** — and in **0 of 2,807 vertex shaders**.
Breakdown of the 28,017: 13,454 use it as a bare branch selector; **10,437 apply a screen-space fix**
(same formula, on an interpolated position); **4,042 apply the clip-space fix** above; 84 have the
matrix but no fix texture.

| stage | built-in stereo? | what we do |
| --- | --- | --- |
| vertex (2,807) | **none** | shear `vs c0` ourselves |
| pixel (43,025) | **yes, 28,017** | set `ps c3`, bind the fix texture — **never touch `ps c4`** |

⚠️ **THE COUPLING INVARIANT:** the pixel side must get **the same S and C** as the vertex shear, and
the flag must be non-zero whenever the matrix is sheared. Flag off ⇒ geometry moves while every
screen-space effect stays put; different S ⇒ they disagree by a constant. Both look like "broken
stereo" and neither is a maths error. `alice_stereo_fix_texel()` routes through the same
`alice_stereo_shear()` so they cannot drift apart.

**`NvStereoFixTexture` is bound per shader**, not at a fixed `s1`: `s1` (14,221), `s3` (202), `s0`
(46), `s2` (10) — hence `shadermap.c`, a CTAB parser plus a pointer-keyed registry.
**Validated against the game's own 45,832 shaders** against an independent Python pass; every bucket
agrees, including `NvStereoEnabled` never appearing outside `ps c3` and `PreViewTranslation` never
outside `vs c5`. `[verified-numerically 2026-09-03, n=45832 shaders]` Plus 36 configurations proving
the two stages land in the same place, and a falsifiability check that they diverge with the flag
off. Code and full account: `staging/alice-madness-returns-vr/proxy-d3d9/README-stereo.md`.

**Still open on this front:** nothing in the shader maths. What remains is the proxy plumbing.
The superseded note read: the pixel-stage half. `ViewProjectionMatrix` is also `ps_3_0 c4 ×4` in
4,122 shaders and needs the same treatment, but **`ps c4` is `WorldToViewMatrix` (4×3) in 135 other
shaders**, so a blind `ps c4` write corrupts those — it needs a per-shader register map, not a fixed
register. And `p00` recovery from the matrix assumes nothing non-rigid is baked in after the
projection (true for Alice's `c0`; not for a fused local-to-clip).

### ✅ SETTLED STATICALLY, 2026-09-01 — the registers are read out of the game's own shipped shaders

*Discovered by the `/pd` pass at 14:29 (`modding-notes/2026-09-01b-…`), which recorded it in the notes
and on the status board but not here; folded into the dossier, with the vertex/pixel split added, by
the later `/pd` pass (`modding-notes/2026-09-01c-…`).*

**The game was never launched.** This came from `AliceGame\CookedPC\RefShaderCache-PC-D3D-SM3.upk`,
a file that ships with the game, read with `flat-to-vr-RE-toolkit/tools/d3d9-ctab.py`. Compiled D3D9
shaders carry a `CTAB` block naming every constant and its register, so this is plain data on disk —
no capture, no debugger. The cache holds **45,832 constant tables (43,025 `ps_3_0`, 2,807 `vs_3_0`)**.

| Constant | Target | Register | Shaders | Distinct layouts | Exceptions |
|---|---|---|---|---|---|
| `ViewProjectionMatrix` | `vs_3_0` | **`c0`, 4 regs (4×4)** | 2,431 | 576 | **none** |
| `CameraPosition` | `vs_3_0` | **`c4`** | 1,989 | 473 | **none** |
| `PreViewTranslation` | `vs_3_0` | **`c5`** | 486 | 195 | **none** |
| `NvStereoEnabled` | `ps_3_0` | `c3` | 28,017 | 11,004 | none |
| `ViewProjectionMatrix` | `ps_3_0` | `c4` (and `c11` ×4) | 4,126 | 1,723 | — |

`[inferred-static 2026-09-01]` — every vertex shader in the shipped cache that references the
view-projection puts it at `c0`, across 576 independent layouts, with no counter-example. 2,431 of
the 2,807 vertex shaders (87%) carry it.

**⭐ The useful split: VIEW constants are fixed, PER-OBJECT constants are not.** The three registers
above never move. The per-object matrices move with the vertex factory, and a hook must not assume
them:

| Constant | Registers seen (`vs_3_0`) |
|---|---|
| `LocalToWorld` | `c6` (1,761 shaders), `c231` (468 — the skinned/GPU-skin factory), `c10` (228) |
| `LocalToView` | `c10` (154), `c14` (114) |
| `InstancedPreViewTranslation` | `c6` (46), `c10` (28) — a **separate constant** from `PreViewTranslation`, used by the instanced factory |

`[inferred-static 2026-09-01]` This is why a per-eye override belongs at `c0`: it is the one place the
camera arrives at a fixed address regardless of which factory drew the object. It also explains the
early Enslaved histogram that started the per-object-WVP scare — `c6`/`c10`/`c231` genuinely do change
per draw; they are just not where the camera lives.

**⚠️ Vertex and pixel registers are different spaces — do not merge them.** The same name sits at
`c0` in a vertex shader and `c4` in a pixel shader. Reading the two together is what makes `c0` look
like a minority case; split by target and the vertex side is unanimous.

**And the pixel-shader copies are not a footnote: they outnumber the vertex ones (4,126 vs 2,431).**
A per-eye offset written only at vertex `c0` would leave every one of those pixel shaders reading an
un-offset view-projection — the shape of bug that yields correct geometry with wrong screen-space
effects (reflections, fog, SSAO, decals). Plan for both from the start. (Related display trap: the
CTAB tool prints *sampler* registers with a `c` prefix too, so `NvStereoFixTexture sampler c1` is
`s1` and does **not** collide with `ScreenPositionScaleBias` at float4 `c1`.)

### ⛔️ This supersedes the "c0 is probably NOT a shared view-projection" warning below

That warning was inherited from `enslaved-vr`, whose early gameplay histogram showed only per-draw
4×4 uploads and no frame-constant register. **It was withdrawn at the source on 2026-09-01**
(`enslaved-vr/modding-notes/2026-09-01-shared-viewprojection-confirmed-at-c0.md` — Enslaved's own
shipped `.usf` sources put the shared view-projection at `c0`). Alice now agrees from a completely
different kind of evidence: Enslaved from shader *source*, Alice from compiled shader *reflection*.
**Both UE3/D3D9 games independently land on `c0` = ViewProjection, `c4` = CameraPosition,
`c5` = PreViewTranslation.** Treat the paragraph below as history, not as guidance.

**What this does NOT establish:** that writing `c0` steers the picture. The register is where the
matrix *arrives*; nothing here proves the engine does not also fold a camera term into per-object
matrices for some passes, and the `ps_3_0` copies at `c4` mean at least some screen-space work
re-reads it. The diagnostic that would show the *derivation* is wrong rather than a value needing
tuning: override `c0` with a deliberate large yaw and check whether **all** opaque geometry rotates
together. If some passes rotate and others do not, the shared-VP model is incomplete for this game.

### 🪤 The `c5` trap: a per-eye offset that ignores `PreViewTranslation` drifts

From `/sr`'s inbox drop, 2026-09-01. `PreViewTranslation` at `c5` means vertices arrive in
**translated world space** — UE3's precision trick for large levels. **A per-eye offset that ignores
`c5` looks correct near the world origin and drifts as you move away from it.** `[reported]`

That failure mode is nastier than a wrong-looking picture: it **passes its first test** and fails
later, far from where it was written. Given Alice's level sizes this is a real risk, not a footnote.
Any stereo maths written here must account for `c5` from the start.

**The clean injection point,** same source: `SetVertexShaderConstantF` filtered on
`StartRegister == 0 && Vector4fCount == 4` is where the view-projection arrives — one intercept, per
eye. The camera position comes free at `c4` rather than being solved out of a matrix. `LocalToWorld`
and friends are compiler-allocated per vertex factory (see the table above) and are not in the way.

**Also worth keeping — why the old warning was wrong.** The pessimistic reading came from a live
capture showing `c0` receiving **47 uploads per frame**, which looked like per-draw traffic. UE3's
D3D9 RHI **re-applies the reserved view registers around bound-shader-state changes**, so those were
47 writes of *the same value*. The count was real; the inference from it was not — "counting events
is not measuring content", now written up as a named failure mode in the cross-engine library.
**And the dossier's own suggested test (flag any register whose 4×4 value is identical across every
draw) would have got it right.**

**Status of the verification `/sr` asked for:** the drop was `[inferred-static, n=1]` from *Enslaved's*
shader sources and asked that it be confirmed on Alice before being built on. **That is now done** —
the CTAB reflection above is Alice's own shipped data, and it agrees on all three registers.

### ⭐ The native stereo path is real, and it is compiled into the shipping shaders

`NvStereoEnabled` is present in **28,017 pixel shaders (65% of all of them), always at `ps_3_0` `c3`**,
with `NvStereoFixTexture` as a companion sampler. `[inferred-static 2026-09-01]` This is much harder
evidence than the config key `AllowNvidiaStereo3d=True` or the HelixMod author's remark: the stereo
path is not a menu option bolted on, it is **branch logic baked into the majority of the game's
shipped pixel shaders**. It corroborates the "this game ships real stereo-3D support" lead below and
promotes it from a strong lead to a static fact about the shaders.

**Careful about what it buys us:** this is *NVIDIA 3D Vision* support — a driver-era stereo path.
Its presence proves per-eye rendering was designed for, and `c3` is a live switch worth probing, but
it is not an OpenXR submission path and it does not by itself give us head tracking.

#### ✅ `NvStereoFixTexture`'s layout is documented — no disassembly needed (`/gr`, 2026-09-01)

It is NVIDIA's **`StereoParmsTexture`** from the freely published `nvstereo.h` that shipped with 3D
Vision. Channels, in NVIDIA's own wording `[reported]`:

| channel | contents |
|---|---|
| `.r` | eye-specific **separation** |
| `.g` | **convergence** |
| `.b` | **unit vector identifying the current eye — left = −1, right = +1** |

The texture is **app-provided** (the game creates it) and updated once per frame. Dimensions and
format come from `StereoTexWidth`/`StereoTexHeight`/`StereoTexFormat`, whose values the doc names but
does not print — **so the size/format still has to be read off the game's own `CreateTexture` call.**
That is a much smaller open question than the one it replaces.

**Why this matters more than it looks:** a proxy can bind **its own** stereo texture, and all 14,479
sampling shaders then read *our* separation, *our* convergence and *our* eye sign — unmodified, with
no NVIDIA driver involved. The `.b` channel is the mechanism by which one shader behaves differently
per eye. With the view-projection at `c0`, the whole shape is specified without a launch: render
twice; per eye write that eye's view-projection to `c0`; per eye bind a stereo texture carrying that
eye's sign; ship all 28,017 shaders exactly as they are. **That is NVIDIA's division of labour with us
in the driver's role.**

**⚠️ Two caveats, both unresolved:**
1. **✅ RESOLVED 2026-09-03 — the mode is AUTOMATIC.** This was recorded as genuinely ambiguous:
   Epic's page is titled *"UE3 and NVIDIA 3D Vision **Direct**"* (the optimistic reading), but an
   **eye-sign channel in a texture is the signature of the Automatic pattern** — an app rendering in
   Direct mode already knows which eye it is drawing. **The texture reading was right.** The caller
   scan on an unpacked copy (§6) finds **zero** references to both `Stereo_SetActiveEye` and
   `Stereo_SetDriverMode`, against live references to `Initialize`, `CreateHandleFromIUnknown`,
   `Activate` and three getters. `[inferred-static 2026-09-03]` Epic's *page title* describes what
   UE3 can support, not what this title shipped. **The plan above was unaffected either way, which
   is why it was still worth acting on — and it now stands confirmed rather than merely unblocked.**
2. **UE3 stereo is reported fullscreen-only** `[reported]` — a windowed live test could show nothing
   and be misread as the approach failing.

- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**:
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention: (D3D9 note: shader constant registers, not D3D11-style
  cbuffers — same caveat as Prince of Persia.)
- Where projection `P` / FOV comes from: **`FOV <10-150>` is a real, native, config-bindable console command (external-research, 2026-08-25)** — confirmed via two independent Nexus Mods ultrawide/FOV-fix mods, both of which work by binding a key in `BaseInput.ini` (`[Engine.PlayerInput]`) to issue this command. This is UE3's well-known generic built-in FOV command, not specific to this game. Low-risk way to probe camera/FOV behavior early, before any hooking work — bind a test key via `BaseInput.ini` and observe directly.
- The per-eye override maths (`K_eye = …`):
- **Potentially the single most important finding in this project so far (external-research, 2026-08-25): this game may ship its own native, already-working stereoscopic-3D camera system.** The HelixMod fix for this game (by "Chiz," the same author credited for Prince of Persia 2008's fix) describes its own job in a very specific way: *"Even though it comes with Stereoscopic support it wasn't 100% but Your fixes made 100%."* That means Alice: Madness Returns **ships a real, built-in stereo-3D mode** (very plausibly targeting official "NVIDIA 3D Vision Ready" certification, common for UE3 titles of this era) — and the third-party fix's job was narrow: it *"push[es] 2D UI to 3D depths"* only, a **shader-level UI-layer intervention, not a camera or world-projection change.** If the native mode's core per-eye camera/projection handling was already correct enough that a third party only needed to fix flat UI, **this game's own shipped code may already contain a working per-eye projection override mechanism** — exactly what this section exists to reverse-engineer. **Concrete next step, before any from-scratch shader-reflection work:** check for a native in-game "Stereo 3D" setting (options menu or a config/`.ini` value) and whether it's still functional on the current build — if reachable and toggleable live, watching what changes in the constant-register/matrix data between mono and native-stereo rendering would be far more direct than reverse-engineering the mono path alone. Not yet confirmed to exist/work on the current build — a strong lead, not a confirmed shortcut.
- **UE3's camera architecture is publicly documented (external-research, 2026-08-25) — a real advantage no other project in this portfolio has** (every other front runs a fully proprietary, undocumented engine). Two levels, from Epic's own UDK docs and the community BeyondUnreal wiki:
  - **Gameplay/UnrealScript layer:** `PlayerController` owns the camera (`PlayerCamera`, `CameraClass`, `ViewTarget` properties); FOV lives on the controller too (`FOVAngle`, `DefaultFOV`). **`UpdateViewTarget` is the documented per-frame function to look for/override** — it updates the view target's position/rotation/FOV each frame, and is the natural starting point for where this game's camera decision gets made before it ever reaches the renderer. `GetPlayerViewPoint` returns the actual point-of-view handed to rendering.
  - **Shader/renderer layer:** UE3's view-projection matrix is documented as living in **vertex shader constant register `c0`** (community-referred to as `VSR_ViewProjMatrix`) — directly answering this section's "exact constant-buffer slot" question via public documentation (D3D9 has no cbuffers, so this is a shader constant register, consistent with this dossier's existing D3D9 caveat). **`PreViewTranslation`** is UE3's documented technique of splitting the view matrix into a separately-tracked camera-relative translation component and a rotation matrix (`ViewMatrix = PreViewTranslation × ViewRotationMatrix`), to preserve floating-point precision in large worlds — a well-known UE-family pattern that persisted into UE4/5.
  - **This is public, generic UE3 knowledge, not yet verified against this specific game's binary** — treat as a real, testable starting hypothesis for live shader-reflection work (check `c0` first; look for a `PreViewTranslation`-style split), not a substitute for confirming it live.
- **⛔️ SUPERSEDED 2026-09-01 — DO NOT ACT ON THIS PARAGRAPH; see §6's static findings above. Kept only so the reasoning stays visible.** ~~Important correction from this portfolio's own sibling project (external-research, 2026-08-25): `c0` is probably NOT a simple shared view-projection register.~~ `[disproved 2026-09-01]` `enslaved-vr` (Enslaved: Odyssey to the West, this portfolio's own project, same engine generation and renderer — UE3 on D3D9) has a real, live-captured constant-register histogram from an actual gameplay frame: every 4×4 matrix upload was **per-object/per-draw** (at `c0`, `c6`, `c10`, and `c231`/`c235` for a skinned-character vertex factory) — **no register held a value shared across every draw in the frame.** Working conclusion there: the camera is very likely folded into a per-draw World×ViewProjection matrix, not delivered as one separately-uploaded shared VP register. **Don't assume `c0` holds a clean, isolated view-projection matrix for Alice just because generic UE3 docs describe it that way** — build (or adapt) the same "flag any register whose 4×4 value is identical across every draw in the frame" detection technique first; if nothing gets flagged, expect the harder per-object-WVP decomposition case instead.
- **A directly reusable D3D9 proxy blueprint exists in this portfolio already (`enslaved-vr`, external-research 2026-08-25)**: a fail-safe `d3d9.dll` proxy forwarding all real exports, intercepting `Direct3DCreate9`, then patching `IDirect3D9::CreateDevice` (**vtable slot 16**), and on the returned device patching `Present` (**17**), `Reset` (**16**), and `SetVertexShaderConstantF` (**94**) — logging `CreateDevice` params, a per-frame register-upload histogram, and an optional watched-register 4×4 dump. This is essentially the natural next build for this section — Enslaved's own vtable slots/hook points are simply facts about D3D9's interface layout that apply identically here (own logic to be written fresh, not copied). **Two-altitude framing for owning the camera (same source):** (1) RHI level — intercept `SetVertexShaderConstantF`/`SetTransform` in the proxy and re-derive/replace the view-projection per eye; (2) engine level — patch the UnrealScript/native camera path (`APlayerCamera::UpdateCamera` or a game-specific override) before the renderer ever consumes it. Worth deciding between these explicitly once live work starts.
- **UE3's stock default console key is Tilde (`~`), not F2** (external-research, 2026-08-25, confirmed via Enslaved's own shipping `BaseInput.ini`/`MonkeyInput.ini` — `ConsoleKey=Tilde`). Directly relevant to this dossier's own open §3/§9 question: if F2 turns out to be MadnessPatch-specific rather than stock, try Tilde on the unpatched game first.
- **Config methodology note (same source): UE3's authoritative runtime config often lives under `Documents\My Games\UnrealEngine3\<ProjectName>\Config\`, not the in-install-directory INI files** (which are just defaults) — check for an `AliceGame`-equivalent per-user config path before assuming edits to game-directory `.ini` files take effect. Also worth checking Alice's engine INI for a non-default `GameViewportClientClassName` (Enslaved has `NTEngine.NTReplayGameViewportClient`) — a cheap, config-only way to discover whether Spicy Horse layered custom camera/viewport logic on stock UE3, directly relevant given the native-stereo3D finding above already suggests real custom camera work happened here.
- **Camera smoothing is a known, already-solved problem (external-research, 2026-08-25, from MadnessPatch): the base game applies heavy mouse smoothing/negative acceleration and input deadzones** — exactly the kind of input-to-camera latency that reads as unacceptable lag in a headset with real head tracking. MadnessPatch neutralizes this via a simple `DisableMouseSmoothing = 1` config toggle — strong evidence the camera-update code path is a tractable, identifiable target. **This should be treated as a required setting for any VR head-tracking work here, not an optional nicety.**

## 7. Constant-buffer fill mechanism
- Map/DISCARD ring / UpdateSubresource / D3D11.1 offset / **persistent map +
  memcpy** (trap):
- Can source contents be read cheaply (captured CPU pointer) or need staging
  read-back?:
- The chosen override patch point and why:

## 8. Pass inventory (by render target)
- Main scene (res/formats):
- Shadow passes (depth-only sizes):
- Post / AA chain (SMAA/TAA/motion vectors; downscale sizes):
- UI / HUD (how it's kept separate):

## 9. cvar / console cheat sheet
| command / cvar | effect | use |
|---|---|---|
| `FOV <10-150>` | native UE3 field-of-view command | confirmed via two independent Nexus FOV/ultrawide mods, both `BaseInput.ini`-bound |
| `DisableMouseSmoothing = 1` (config, `BaseInput.ini`-style) | removes mouse smoothing/negative acceleration and deadzones | per MadnessPatch — VR-critical, removes input-to-camera latency |
| F2 — **PATCH-ONLY, settled 2026-09-03** | opens the developer console | MadnessPatch 3.0.0+ adds `EnableConsole` bound to F2 as its own feature `[reported]`; **not stock** |
| Tilde `~` | UE3's stock default console key | per enslaved-vr's own shipping config — try if F2 turns out patch-only |
| `Show <group>`, `ToggleDebugCamera`, `Stat FPS`, `Stat D3D9RHI`, `ViewMode <mode>`, `SloMo` | standard UE3 exec commands | per enslaved-vr's own testing; `ToggleDebugCamera` especially worth trying for §6/§10 (free/debug camera) |

### The game's own settings surface (NEW 2026-09-03, `/pd`, static) `[inferred-static 2026-09-03]`

Read from the Steamless-unpacked exe's UTF-16 string table. This answers most of the queued
"what does the `Stereo3D` video-option actually do" without a launch.

- **`UAliceGameEngine` exposes 23 native script functions**, and they are the settings menu's whole
  vocabulary: `DoesSupportMSAA`, `GetNumOfSupportedResolutions`, `GetSupportedResolutions`,
  **`EnableStereo3D`**, `SetNvPhysXLevel`, `GetShowPostprocess`, `SetSoundVolume`, `ExecConfigData`,
  `ExecRebindKey`, `ExecResetKeyBindings`, `GetAliceKeys`/`SetAliceKeys`/`GetAliceKeyIndex`,
  `GetCompatCompositeIndex`, `GetCurrentDeviceID`/`SetCurrentDeviceID`,
  `SaveCheckpoint`/`LoadCheckpoint`/`FindCheckpointData`/`DeleteCheckpoints`,
  `HasStorageDeviceBeenRemoved`, `GetDestructionMaxChunkCount`, `LaunchAlice1`.
- **A complete family of settings identifiers sits beside them, one per menu row:** `ExecAntiAlias`,
  `ExecAttackType`, `ExecControlLayout`, `ExecDifficulty`, `ExecDynamicShadows`, `ExecGamepadType`,
  `ExecGammaConfig`, `ExecGraphicsQuality`, `ExecInputAxis`, `ExecInputKey`, `ExecInvertY`,
  `ExecLowestDifficulty`, `ExecMotionBlur`, `ExecMouseSpeed`, `ExecMusicVolume`, `ExecPhysXLevel`,
  `ExecPostprocess`, `ExecScreenResolution`, `ExecSoundEffectVolume`, **`ExecStereo3D`**,
  `ExecSubtitles`, `ExecVoiceVolume`.
- The Scaleform menu inside `AliceGame.u` carries the same list in menu order (`Volume | Music |
  Voice | Subtitles | Gamma | GraphicsQuality | Resolution | AntiAlias | Stereo3D | Blur | Layout`)
  with matching accessors, so the three sources agree item for item.
- **⇒ The `Stereo3D` row is `ExecStereo3D`, routed through `ExecConfigData`, switching the native
  `EnableStereo3D`.** ⚠️ Held at two different strengths: `EnableStereo3D`'s **existence** is direct
  (the exe contains the UE3 native thunk name `intUAliceGameEngineexecEnableStereo3D`); the
  **routing through `ExecConfigData`** is an inference from the three lists agreeing, not a
  decompilation.
- **The engine gate is already open:** `AllowNvidiaStereo3d` is an `Engine.Engine` config property
  and is `True` in both `Engine/Config/BaseEngine.ini:193` (inside the vendor's own
  `; NVCHANGE_BEGIN: Jiayuan` markers) and the user config `AliceEngine.ini:168` `[measured 2026-09-03]`.
- ⚠️ **Not a shortcut to VR.** 3D Vision *Automatic* is a driver feature needing NVIDIA's stereo
  stack, deprecated on current drivers and normally gated on a 3D-capable display. What is useful to
  this project is the shader plumbing it left behind (`NvStereoEnabled`, `NvStereoFixTexture`, §6),
  which our proxy already reuses. **Unknown:** what `EnableStereo3D` does internally — the exe
  resolves NVAPI dynamically (`nvapi.dll`, `nvapi_QueryInterface`), but its call sites are not
  established.
- Evidence: `dev-archive/recon/2026-09-03-native-stereo3d-menu-path/`.

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used):
- In-process input / camera drive method that worked:
- Frame-capture method; where images land:

## 11. Dead ends & false leads (save future time)
- **✅ LIFTED 2026-09-03 — this dead end is CLEARED, and the method is recorded. Any static scan of `AliceMadnessReturns.exe`'s `.text`** — strings, immediates, xrefs. The section is encrypted at rest (entropy 8.00, entry point in `.bind`); a null result means nothing. **The wrapper is SteamStub v3.1, and unpacking a COPY with Steamless takes seconds and needs no launch — done 2026-09-03, `.text` entropy 8.00 → 6.71 and the NVAPI scan answered (§6).** Static scans of this exe ARE possible; just do them on an unpacked copy, and **always carry the `NvAPI_Initialize 0x0150E828` positive control**, because the packed file returns a clean zero for everything. The original text said: Needs a runtime dump first. `[measured 2026-09-02]`
- **Reading "no stereo strings in the exe" as "the integration lives in the engine layer"** (2026-09-01) — the premise is an artefact of that encryption. `[disproved 2026-09-02]`
- **Reading `SetActiveEye`'s absence from the NVAPI id table as "Automatic mode"** — the table is the linked SDK's fixed list, not the game's usage; `NvAPI_Initialize` is absent from it too. `[inferred-static 2026-09-02]`
- **Looking for `steam_api.dll` to confirm SteamStub** — it is absent from the import table, absent from the whole install, and there is **no "steam" string anywhere in the exe**, yet the binary *is* SteamStub-wrapped (§6). The game has no Steamworks *API* integration, only the DRM wrapper. **A negative here proves nothing; use the `0xC0DEC0DF` header magic instead.** `[measured 2026-09-03]`
- **Porting `alan-wake-vr`'s stereo edit into this project** — its matrices are `MATRIX_ROWS`, Alice's `ViewProjectionMatrix` is `MATRIX_COLUMNS`, so the two implementations are transposes. The Alan Wake form applied here mixes columns, corrupts `clip.w`, and still renders. `[verified-numerically 2026-09-03]` See §6.
- **Assuming `NvStereoFixTexture` is always sampler `s1`** — it is also `s3` (202), `s0` (46) and `s2` (10). `[verified-numerically 2026-09-02]`

## 12. Open risks toward the North Star
- **Framerate-dependent physics is a real, third-party-confirmed risk (external-research, 2026-08-25, from MadnessPatch's own fix list): hair/dress physics instability, projectile hitbox inconsistency, and general simulation behavior specifically at high framerates.** VR needs a high, stable frame rate (typically 90Hz+); this UE3-era game's physics were evidently tuned assuming a much lower framerate ceiling, and MadnessPatch had to fix exactly this class of bug. Running at VR framerates may re-expose the same issues — test explicitly once running at VR-target framerates, and treat MadnessPatch's own fix approach (understand, don't copy) as a reference point.
- **The strongest VR-feasibility signal of any project in this portfolio (external-research, 2026-08-25): vorpX delivers true Geometry 3D stereo AND working motion-controller emulation ("emulates a gamepad perfectly") for this exact game**, in both Immersive and Cinema modes. For comparison: Burnout Paradise's vorpX fails outright; Mad Max's vorpX works but third-person-only with no motion-controller mention; Prince of Persia has no vorpX profile at all. A third party has already solved, for this exact game, both the per-eye camera/projection override (§6's core problem) and mapping VR motion-controller input onto the game's own controls convincingly — neither reusable (closed-source), but both are strong existence proofs this engine doesn't resist full stereo + motion-input VR conversion. Treat vorpX's own default separation/convergence settings as a rough sanity-check reference once this project's own live camera work begins — not to copy, but to cross-check comfort. **Why vorpX does so well here specifically (this portfolio's own cross-engine library, external-research 2026-08-25): vorpX's Geometry 3D mode "works best on D3D9 games specifically"** — D3D9's older, simpler rendering model is exactly its best-case scenario (it works by rendering the scene twice, once per eye, at a real ~50% framerate cost). **A documented backup path exists if the from-scratch engine-level approach hits a wall**: `D3D9 game → dgVoodoo2 (wraps D3D9 onto D3D11) → geo-11 (free, D3D11-only stereo driver)`, optionally paired with a 3Dmigoto-class shader fix. Alice is unusually well-positioned for this specific backup, since it already has exactly the per-game shader-fix piece that route wants (the HelixMod fix, §6). **Scope reminder: both vorpX and geo-11 top out at seated/head-look experiences — no true 6DoF, no spatial motion-controller tracking** (vorpX's "motion controllers emulate a gamepad perfectly" is input-mapping, not hand presence) — this project's actual goal (full engine-level VR with real 6DoF) is a different category than either fallback, consistent with, not a substitute for, the primary plan.
