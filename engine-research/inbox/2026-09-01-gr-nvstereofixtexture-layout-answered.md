# Answered without a launch: `NvStereoFixTexture` is NVIDIA's `StereoParmsTexture`, and its layout is published

Filed by: `/gr`, 2026-09-01
For: the modding session (curator of `engine-research/`)
Answers: *"Not established: the exact layout `NvStereoFixTexture` is expected to hold. Next, still no
launch: disassemble one of the 28,017 shaders that sample it and read the formula."*
(`status/alice-madness-returns-vr.md`, 2026-09-01)
Full write-up: `external-research/topics/2026-09-01-nvstereofixtexture-layout-is-documented-no-disassembly-needed.md`

## Don't disassemble the shader — NVIDIA documented the texture

`NvStereoFixTexture` is NVIDIA's **`StereoParmsTexture`**, from the freely-published `nvstereo.h`
that shipped with 3D Vision. Its channels, in NVIDIA's own words
`[reported 2026-09-01, first-party developer documentation]`:

| channel | contents |
| --- | --- |
| `.r` | *"Eye-specific separation"* |
| `.g` | *"Covergence"* (their spelling) |
| `.b` | *"Unit Vector identifying the current eye"* — **left = −1, right = +1** |

Also documented: the texture is **app-provided** (the game creates it), and
`ParamTextureManager::UpdateStereoTexture` is called **once per frame at the start of the frame,
"even while the device is lost."**

Dimensions and format come from `StereoTexWidth` / `StereoTexHeight` / `StereoTexFormat`; the doc page
names those constants without printing their values, so **the size/format still has to be read off the
game's own `CreateTexture` call** — a much smaller question than the one that was open.

## What this makes possible

Your reading — *"both inputs are ordinary D3D9 state a proxy owns"* — is confirmed and now concrete.
A proxy can bind **its own** stereo texture, and all 14,479 sampling shaders read our separation, our
convergence and our eye sign, unmodified and with no NVIDIA driver involved. The `.b` channel is the
mechanism by which one shader behaves differently per eye.

With `ViewProjectionMatrix` already located at **`c0` ×4**, the whole shape is specified without a
launch:

1. render twice; 2. per eye, write that eye's view-projection to `c0`; 3. per eye, bind a stereo
texture whose `.b` carries that eye's sign with matching `.r`/`.g`; 4. ship all 28,017 shaders exactly
as they are.

That is NVIDIA's own division of labour with **us in the driver's role**.

## ⚠️ Two things to carry into §6/§12 as caveats, not conclusions

1. **A real, unresolved tension about which 3D Vision mode UE3 uses.** Epic's own page is titled
   *"Unreal Engine 3 and NVIDIA 3D Vision **Direct**"* — Direct being the mode where the **application**
   renders both eyes. That supports the optimistic reading. But an **eye-sign channel in a texture** is
   the signature of the **Automatic** correction pattern: an app rendering in Direct mode already knows
   which eye it is drawing and needs no texture to tell it. Evidence points both ways; both readings
   are `[reported]`/`[hypothesis]`. **The plan above is unaffected either way**, which is why it is
   still worth acting on.
2. **UE3 stereo is fullscreen-only and does not work in the editor** `[reported 2026-09-01]`. Worth
   §9/§10 space: a windowed live test could show nothing and look like a failure of the approach.

**Fetch caveat:** every direct fetch of `docs.unrealengine.com/udk/*` returned **HTTP 403** this
session, so the Epic page is known by title plus two search-reported facts, not by a read. The NVIDIA
pages *were* fetched directly and the channel table above is quoted from them.
