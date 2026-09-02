# `NvStereoFixTexture`'s exact size, format, and who actually writes it

**Date:** 2026-09-02
**Closes the remaining gap in:** `topics/2026-09-01-nvstereofixtexture-layout-is-documented-no-disassembly-needed.md`
(that pass got the channel semantics from NVIDIA's docs but not the numeric `StereoTexWidth` /
`StereoTexHeight` / `StereoTexFormat`, which the doc page names but never prints)

## The two things that were still open

1. **Exact dimensions and pixel format.** NVIDIA's prose page names the constants but not their
   values.
2. **Who fills the texture each frame** — the driver, or the app? This matters for a proxy: if the
   driver silently populates it, a proxy has to fight the driver for write access; if the app
   populates it, a proxy just needs to control the same inputs the app already controls.

## The answer, from NVIDIA's own `nvstereo.h` (the header the prose docs are built on)

| Constant | Value |
|---|---|
| `StereoTexWidth` | **8** |
| `StereoTexHeight` | **1** |
| `StereoTexFormat` | **`D3DFMT_A32B32G32R32F`** (D3D9 — this game's API; `DXGI_FORMAT_R32G32B32A32_FLOAT` for D3D10/11) |

`[reported 2026-09-02]` — straight from the published header, an 8×1 four-float-per-pixel render
target. Small enough that a proxy substituting its own copy costs nothing measurable.

**The texture carries a signature, not just data.** `PopulateTextureData()` writes
`NVSTEREO_IMAGE_SIGNATURE` (`0x4433564E`, ASCII `"NV3D"`) into the texture's header region. This is
the marker that tells the driver "this specific texture is the stereo parameters texture" — it is
how the mechanism is identified at all, distinct from any other render target the game owns.

**And the app writes it, not the driver.** `ParamTextureManager`'s population code pulls the current
separation and convergence via NVAPI calls (`GetEyeSeparation`/`GetSeparation`/`GetConvergence`) and
writes them into the texture itself, per eye, once per frame — `UpdateStereoTexture` runs "at the
beginning of the frame," per the prose docs already on file. **The driver's role is reading the
signature and reacting to the values that show up there — not writing them.** `[reported 2026-09-02]`

## Why the "who writes it" answer doesn't change the plan — but does make it more concrete

The existing topic's plan already assumed a proxy could bind its own version of this texture. This
confirms *why that works cleanly*: the game itself is not passively consuming driver-pushed values,
it is actively calling NVAPI each frame and writing the result. **A proxy that intercepts those NVAPI
calls (`Stereo_GetSeparation`/`GetConvergence`) — or simply intercepts the texture write/bind that
follows them — controls every one of the 14,479 sampling shaders without needing driver cooperation
at all**, because the game was never depending on the driver to write this resource in the first
place.

Concretely, for the build plan already on file: an 8×1 `D3DFMT_A32B32G32R32F` staging texture with
`.r`/`.g`/`.b` set to our own separation/convergence/eye-sign, tagged with `0x4433564E` so anything
that checks for the signature (unlikely here since it's app-owned, but cheap insurance), is a
five-minute D3D9 resource to construct — no capture needed to know its shape.

## Sources

- NVIDIA / `nvstereo.h` (as vendored in the open-source `3Dmigoto` project — the header itself, not a
  third-party reimplementation): https://github.com/bo3b/3Dmigoto/blob/master/nvstereo.h
- Prior pass's sources (channel semantics, per-frame update cadence): see the topic this one closes.
