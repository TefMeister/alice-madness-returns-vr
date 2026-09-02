# Direct or Automatic is a one-scan static question — Alan Wake's NVAPI caller count transfers to Alice's exe

**Status:** 🆕 new · **Priority:** ⭐ high — every note since 2026-09-01 calls this "the crux" and "the
same open question as Alan Wake's — worth answering once for both". Alan Wake answered it on
2026-09-01 by a static method; this topic supplies the two ids that make the same scan decisive here.

## The two readings, restated in one line each

- **Direct**: the *application* renders both eyes itself — it tells the driver so before creating the
  device, and tells it which eye it is drawing before each eye's draws. Epic's page for the UE3
  integration is titled *"…and NVIDIA 3D Vision **Direct**"*.
- **Automatic**: the *driver* duplicates every draw and applies the clip-space eye offset; the
  application at most corrects screen-space effects using a stereo-parameters texture. Alice's
  28,017 `NvStereoEnabled` pixel shaders and the 8×1 `NvStereoFixTexture` are exactly that
  correction machinery.

The `/gr` topic of 2026-09-01 left the tension open because both signatures are present. It does not
have to stay open: the two modes differ in **which NVAPI entry points the game calls**, and NVAPI
dispatches by numeric id, so the ids are `push imm32` operands in the binary whether or not any name
string survives.

## The contract, from NVIDIA's own material

`[reported 2026-09-02]` — NVAPI reference and the `nvapi_lite_stereo.h` header:

- `NvAPI_Stereo_SetDriverMode(NVAPI_STEREO_DRIVER_MODE_DIRECT)` **must be called before the D3D9
  device is created**; without it the driver stays in Automatic.
- In Direct mode the app calls **`NvAPI_Stereo_SetActiveEye(handle, LEFT | RIGHT | MONO)`** before
  each eye's rendering, having created a stereo handle from the device. Community Direct-mode
  samples (bo3b's) note the only other requirement is a double-width back buffer; the app then sets a
  per-eye projection and "rendering is done twice, once for each eye".
- Automatic needs neither call. It needs `Stereo_Activate`/`Enable` (turns the emitter on) and, for
  correction, the separation/convergence getters.

**So `SetActiveEye` is the discriminator: it has no purpose outside Direct mode.** `SetDriverMode` is
the second witness (Alan Wake's zero-caller result rested on it).

## The ids, read from NVIDIA's published `nvapi_interface.h` (663 lines, fully read)

| function | id | role |
| --- | --- | --- |
| **`NvAPI_Stereo_SetActiveEye`** | **`0x96EEA9F8`** | **Direct-only — the discriminator** |
| **`NvAPI_Stereo_SetDriverMode`** | **`0x5E8F0BEC`** | Direct requires it before device creation |
| `NvAPI_Stereo_CreateHandleFromIUnknown` | `0xAC7E37F4` | both modes |
| `NvAPI_Stereo_Activate` | `0xF6A1AD68` | both (emitter on) |
| `NvAPI_Stereo_IsActivated` | `0x1FB0BC30` | both |
| `NvAPI_Stereo_Enable` / `IsEnabled` | `0x239C4545` / `0x348FF8E1` | driver-wide setting |
| `NvAPI_Stereo_GetSeparation` / `SetSeparation` | `0x451F2134` / `0x5C069FA3` | the texture's `.r` source |
| `NvAPI_Stereo_GetConvergence` / `SetConvergence` | `0x4AB00934` / `0x3DD6B54B` | the texture's `.g` source |
| `NvAPI_Stereo_GetEyeSeparation` | `0xCE653127` | Automatic correction input |
| `NvAPI_Stereo_SetSurfaceCreationMode` | `0xF5DCFCBA` | Automatic: per-surface stereo policy |
| `NvAPI_Stereo_ReverseStereoBlitControl` | `0x3CD58F89` | Automatic: reading back both eyes |
| `NvAPI_Stereo_CreateConfigurationProfileRegistryKey` / `SetConfigurationProfileValue` | `0xBE7692EC` / `0x24409F48` | profile writes |
| `NvAPI_Initialize` | `0x0150E828` | the positive control — must have callers |

`[verified-static 2026-09-02, read directly from NVIDIA's public repository]`

## The scan, and how to read it

Alan Wake's recipe (its dossier §6, 2026-09-01): find each id as an immediate in the module, locate
the wrapper that pushes it into `nvapi_QueryInterface`, count **direct callers** of each wrapper. The
zero only counts against a contrast — four called, two uncalled — which is why `Initialize` is in
the table as the positive control. On Alice the module is **`AliceMadnessReturns.exe`** (UE3 is
monolithic; the `/pd` note that the exe "has essentially no stereo strings" is about *names*, and
these are numbers).

| result | meaning |
| --- | --- |
| `SetActiveEye` has callers (and `SetDriverMode` too) | **Direct.** The engine already renders two eyes per frame; the `c0` per-eye write already exists somewhere in the exe, and the stereo texture is a correction layer on top. The shortcut is real. |
| neither has callers, but `Activate`/`GetSeparation`/`GetConvergence` do | **Automatic.** Same verdict as Alan Wake: the driver made the eyes; the game's stereo symbols correct effects. The plan on file (render twice, write `c0` per eye, bind our own 8×1 texture per eye) is unchanged — this only says the engine will not do the second pass for us. |
| no stereo id has any caller | the integration is config-gated at a level the scan cannot see (e.g. a separate module or a data-driven dispatch) — unlikely for UE3, and a reason to look at the `Stereo3D` option's code path instead. |

Either answer settles the caveat carried in three topics, and it costs one static pass with the
tool Alan Wake already used.

## What the in-game `Stereo3D` toggle does, from players

The Steam thread "Stereo 3d refuses to work" `[reported 2026-09-02]`: switching the option on
**turns the NVIDIA emitter's green light on** — i.e. the game itself calls `Stereo_Activate` (or
`Enable`) — and even when no 3D effect appears "framerate seems to drop and the dynamic shadows seem
to be shifting into stereo mode". A framerate drop with no visible stereo is consistent with either
mode (the engine or the driver doing double work), so it does not decide the question; it does say
the toggle is live on modern drivers and that shadows are among the stereo-aware passes. Working
setups reported 3D "VERY good" with the Helix fix for crosshair depth, on 310.90/314.21-era drivers.

## A second, smaller answer: F2 is MadnessPatch's, not stock

MadnessPatch's releases since this lane last looked (3.0.0 on 2026-07-01 through 3.1.1 on 2026-07-26)
add **`EnableConsole`, "bound to F2"**, as a patch feature `[reported 2026-09-02, release notes]`.
That resolves the dossier's §3/§9 "F2 — stock or patch-only?" line: **patch-only**; the stock UE3
default remains Tilde (as Enslaved's config shows), and whether Alice's shipping build kept its
console class is still the live check it was. Nothing in those releases touches stereo, 3D Vision,
the camera or a D3D9 proxy.

## Concrete next steps

1. **Static, no launch:** run the id scan on `AliceMadnessReturns.exe` for `0x96EEA9F8` and
   `0x5E8F0BEC` with `0x0150E828` as the positive control; count direct callers of each wrapper.
2. Record the mode in dossier §6 in place of the "Direct vs Automatic" caveat, and retire the same
   caveat from the two `NvStereoFixTexture` topics.
3. If Direct: the next static target is the code between `SetActiveEye(LEFT)` and
   `SetActiveEye(RIGHT)` — that is where the engine writes its per-eye `c0`.

## Sources

- https://github.com/NVIDIA/nvapi/blob/main/nvapi_interface.h — the id table (public, read online)
- https://github.com/NVIDIA/nvapi/blob/main/nvapi_lite_stereo.h · https://docs.nvidia.com/nvapi/nvapi__lite__stereo_8h.html — `SetDriverMode` timing and `SetActiveEye` semantics
- https://github.com/bo3b/3D-Vision-Direct — a public Direct-mode sample's README (double-width back buffer, render twice)
- https://steamcommunity.com/app/19680/discussions/0/828925216495800901/ — what the in-game toggle does
- https://github.com/Wemino/MadnessPatch/releases — `EnableConsole` (F2) and the 3.x changes
- https://nvidianews.nvidia.com/_gallery/download_pdf/54481935f6091d2735000245/ — NVIDIA's 2010 GDC release (no technical detail; date 2010-03-11 and the licensee list only)
- https://docs.unrealengine.com/udk/Three/ThreeDVision.html — still 403 to automated fetch (EN and JP); title and two facts via search only
