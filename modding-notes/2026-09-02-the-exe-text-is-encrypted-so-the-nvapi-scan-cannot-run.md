# 2026-09-02 — `.text` is encrypted at rest, so the NVAPI Direct-vs-Automatic scan cannot be run statically

**Date:** 2026-09-02, dev PC, `/pd` pass. **The game was never launched, nothing was run, nothing in
the game folder was modified.** Static reading of files already on disk.

The session set out to do the queued `[PD]` work: the NVAPI caller-count scan that `/gr` filed on
2026-09-02 as the way to settle Direct vs Automatic, then the per-eye maths, then the proxy. The scan
turned out to be **unrunnable on this binary**, for a reason that invalidates a broader class of
static work here, so that is the headline.

---

## 1. The load-bearing finding: `AliceMadnessReturns.exe`'s `.text` is encrypted on disk

| section | VA | raw size | entropy |
|---|---|---|---|
| **`.text`** | `00401000` | `0xc9f400` | **8.00** |
| `.textidx` | `010a1000` | `0x8ce00` | 6.03 |
| `.rdata` | `0112f000` | `0x26ac00` | 4.85 |
| `.data` | `0139a000` | `0x3e600` | 5.69 |
| `.reloc` | `01502000` | `0x15ee00` | 6.81 |
| **`.bind`** | `01661000` | `0x30b18` | 7.98 · **holds the entry point (`01661310`)** |

`[measured 2026-09-02]` — 8.00 bits/byte is the ceiling; `.text` is indistinguishable from random
data. Three independent corroborations that this is encryption and not a measurement artefact:

- **The entry point is not in `.text`.** It is at `01661310`, inside `.bind` — a wrapper section
  appended after `.reloc`. A normal PE enters its own code section.
- **`.text` does not disassemble.** Its first bytes (`63 23 f8 1b a1 d9 …`) and the region at the
  entry point decode to nonsense — `outsd`, `aad`, `in al, dx`, jumps to unmapped addresses.
- **`.text` contains zero `CC` padding runs.** Every MSVC-linked binary has thousands of `int3`
  alignment runs between functions. Their complete absence, in 13 MB of "code", is decisive.

So a wrapper decrypts `.text` into memory at load time. I did **not** establish which wrapper: the
strings `SteamStub`, `Steam`, `CEG` and `valve` do not appear anywhere in the file, and `.bind`
occurs only as the section name itself. `[inferred-static 2026-09-02]` The identity does not change
the consequence and is not worth chasing.

**This is a correction to dossier §4, which records "no DRM".** That claim came from searching for
*named* DRM (EA's Cuckoo, checked and genuinely gone) and is right about that; but the shipping
binary is nonetheless **wrapped**, and §4 read as "the exe is plain". It is not.

**It does not affect injection.** The `d3d9.dll` proxy is live-verified on this exact build
(2026-08-25, and the rescued log shows two `Direct3DCreate9` calls and a `D3DPERF_SetOptions`), and
a wrapper that decrypts at load has no bearing on DLL proxying. The damage is confined to *static
analysis of code*.

## 2. What that invalidates

**Every static scan of `.text` on this game is a guaranteed false negative — the test could not have
produced a positive result.** In particular:

- **The queued NVAPI caller-count scan cannot run.** `/gr`'s method — find `NvAPI_Stereo_SetActiveEye`
  (`0x96EEA9F8`) and `SetDriverMode` (`0x5E8F0BEC`) as `push imm32` operands, then count callers — is
  sound, and it is exactly right on Alan Wake's unencrypted binary. Here the operands are inside the
  encrypted section. Finding zero is what this binary returns for *everything*.
- **It also explains, and withdraws, an older inference.** The 2026-09-01 note observed the exe "has
  essentially no stereo strings" and concluded the integration "lives in the engine layer and its
  config". The premise is real but the conclusion does not follow: **the exe's strings are
  encrypted.** `/gr`'s topic anticipated the objection and answered "these are numbers, not names" —
  correct in principle, but numbers in `.text` are encrypted too. `[disproved 2026-09-02]` as an
  inference; the observation stands as an artefact of the wrapper.

## 3. What is still readable, and what it does and does not say

`.rdata` and `.data` are **not** encrypted, and they carry a real find: a **105-entry NVAPI interface
table** at `013d452c`, records of `{u32 slot; u32 slot; u32 interfaceId}`, ids matching NVIDIA's
published `nvapi_interface.h` (fetched this session, 518 ids). Full decode in
`dev-archive/recon/2026-09-02-text-is-encrypted-and-nvapi-table/alice-nvapi-table.tsv`.

**27 of the 105 are `NvAPI_Stereo_*`**: `Enable`/`Disable`/`IsEnabled`, `CreateHandleFromIUnknown`,
`DestroyHandle`, `Activate`/`Deactivate`/`IsActivated`, `Get`/`Set`/`Increase`/`DecreaseSeparation`,
the same four for `Convergence`, `GetEyeSeparation`, `Get`/`SetFrustumAdjustMode`,
`ReverseStereoBlitControl`, `SetNotificationMessage`, `CaptureJpegImage`/`CapturePngImage`, and the
four configuration-profile-registry calls. **`SetActiveEye` and `SetDriverMode` — the two Direct-mode
entry points — are absent from the table, as is `NvAPI_Initialize`.**

**⚠️ That absence is NOT evidence for Automatic, and must not be recorded as such.** The table also
contains `NvAPI_VIO_*` (Quadro SDI video I/O), `NvAPI_GPU_GetECC*`, `Mosaic`, `I2CRead/Write` and
OpenGL expert-mode calls — functions no game ever calls. It is therefore **a fixed table belonging to
the linked NVAPI SDK version, not a list of what this game uses.** Whether `SetActiveEye` is missing
because the game does not use it, or because it postdates the SDK Spicy Horse linked, is not
decidable from the table. `[inferred-static 2026-09-02]` The positive control makes the point on its
own: `NvAPI_Initialize` is missing too, and the game unquestionably calls it — the loader strings
`nvapi.dll` and `nvapi_QueryInterface` sit at `0131ba4c` in readable `.rdata`.

**So Direct vs Automatic remains open, and its cost has gone up:** it now needs a memory dump of
`.text` from a running process, which is a `[FLAT]` task, not a `[PD]` one. The toolkit already has
the mechanism — `static-disasm.py --raw`, the route that worked on Manhunt's packed build.

## 4. The shader-register facts, re-derived and slightly refined

Re-ran `d3d9-ctab.py` against `RefShaderCache-PC-D3D-SM3.upk` and a per-target histogram script of my
own (`ctab-per-target-histogram.py` in the recon folder). **Every published number reproduces**
`[verified-numerically 2026-09-02]`: 45,832 tables (43,025 `ps_3_0` + 2,807 `vs_3_0`);
`ViewProjectionMatrix` `vs_3_0` `c0 ×4` in 2,431 with **no exceptions**; `CameraPosition` `vs_3_0`
`c4` in 1,989; `PreViewTranslation` `vs_3_0` `c5` in 486; `NvStereoEnabled` `ps_3_0` `c3` in 28,017.

Two refinements worth having:

- **`ViewProjectionMatrix` `ps_3_0` is `c4 ×4` in 4,122** shaders and `c11 ×4` in 4 — the dossier's
  "c4 (and c11 ×4)" was right but did not separate the counts. The pixel copies still outnumber the
  vertex ones, so the both-stages requirement stands.
- **`NvStereoFixTexture` is not only `s1`.** It is `s1` in 14,221, **`s3` in 202, `s0` in 46 and `s2`
  in 10.** A proxy binding the stereo texture must therefore key off *which sampler each shader
  declares*, not assume `s1` — 258 shaders would silently read the wrong texture. That is new, and it
  is the kind of detail that produces a subtly wrong picture rather than an obvious failure.

Also visible for the first time: `WorldToViewMatrix` `ps_3_0` `c4 ×3` in 135 shaders — a 4×3 sharing
the `c4` slot with the 4×4 view-projection in other shaders, i.e. **`ps` `c4` is a reserved slot
whose meaning varies by shader.** Anything writing `ps c4` blind would corrupt those 135.

## 5. The per-eye maths: derived, NOT yet verified

The `c5` `PreViewTranslation` trap (a world-space eye offset drifts far from the origin) has a clean
escape that the notes had not recorded: **do the eye split in clip space, not world space.** For
`x_clip = row0·p` and `w_clip = row3·p`, NVIDIA's own stereo formula is
`x' = x + S·(w − C)` for separation `S` and convergence `C`, which is exactly

```
row0' = row0 + S * row3 ;  row0'[3] -= S * C
```

Because it acts on the matrix's *output*, it never touches world coordinates and is therefore
**immune to `PreViewTranslation` entirely.** Hand-derivation from a standard D3D perspective matrix
(eye translated by `t` in view X, film plane shifted so depth `C` has zero parallax) gives
`S = (f/aspect)·t/C`, reproducing the formula exactly.

**`[hypothesis]` — this is algebra I did on paper and have NOT tested numerically, and the
project's own rule is that untested maths is not a result.** The check to run: build ground truth
independently (explicit view-space translation plus asymmetric frustum), compare against the
row-operation, and compare *compiled shipped code* rather than a transcription. Queued as `[PD]`.

## 6. What did NOT get done

The proxy build (`[PD]`, the session's main target) **was not started** — the encryption finding and
its consequences took the session. The existing M0 proxy still builds clean (re-verified this
session: 32-bit PE, both exports correct). No proxy code was changed.

## 7. Evidence rescued

`dev-archive/recon/2026-09-02-text-is-encrypted-and-nvapi-table/` — section entropy table, the
105-entry NVAPI decode, the per-target register histogram and the script that produced it. Names,
ids, offsets and counts only; no game content.

🤖 Static analysis only. No launch, no debugger, nothing modified.
