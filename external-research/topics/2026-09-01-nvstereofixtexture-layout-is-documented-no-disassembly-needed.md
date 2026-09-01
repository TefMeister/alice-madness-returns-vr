# `NvStereoFixTexture`'s layout is documented by NVIDIA — the open question needs no disassembly

**Status:** 🆕 new · **Priority:** ⭐ high — it closes the single open question the modding side left
open on 2026-09-01, and it closes it from a first-party source rather than by reverse-engineering.

## The open question

`status/alice-madness-returns-vr.md`, 2026-09-01:

> **Not established:** the exact layout `NvStereoFixTexture` is expected to hold. **Next, still no
> launch:** disassemble one of the 28,017 shaders that sample it and read the formula.

`NvStereoFixTexture` is not a Spicy Horse invention and not an Epic one. It is **NVIDIA's
`StereoParmsTexture`**, from the freely-published `nvstereo.h` header that accompanied 3D Vision, and
NVIDIA documents its layout.

## The layout, from NVIDIA's own documentation

The texture holds **per-eye constant data**, and the channels are `[reported 2026-09-01, NVIDIA's own
published 3D Vision developer documentation]`:

| channel | contents |
| --- | --- |
| `pixel(0,0).r` | *"Eye-specific separation"* |
| `pixel(0,0).g` | *"Covergence"* (NVIDIA's own spelling) |
| `pixel(0,0).b` | *"Unit Vector identifying the current eye"* — **left eye = −1, right eye = +1** |

Its dimensions and format come from `StereoTexWidth` / `StereoTexHeight` / `StereoTexFormat` in the
header; **the documentation page names those constants but does not print their values**, so the exact
size and format still have to come from the header or from observing the game's own
`CreateTexture` call. The *semantics* — which is what the open question was about — are settled.

Two mechanical details that matter for anyone driving it:

- `ParamTextureManager::UpdateStereoTexture` *"Updates an app-provided texture with per-eye constant
  data"*, and is called **once per frame, at the beginning of the frame — "even while the device is
  lost."** So the game's own update cadence is per-frame-at-start, and there is a documented
  expectation that it keeps happening through device loss.
- The texture is **app-provided**. The application creates it; the manager fills it.

## Why this is the good news it looks like

The status note already reached the right conclusion — *"both inputs are ordinary D3D9 state a proxy
owns — `SetPixelShaderConstantF` and `SetTexture`"*. Knowing the layout makes that concrete:

**A proxy can create a texture with those three channels set to values of its choosing and bind it in
place of the game's.** All 14,479 shaders that sample `NvStereoFixTexture` will then read *our*
separation, *our* convergence, and *our* eye sign — with no NVIDIA driver, no 3D Vision, and no
shader patching. The `.b` channel being an explicit ±1 eye selector is the useful part: it is the
mechanism by which the same shader, unmodified, behaves differently per eye. That is exactly the
control a per-eye render needs, sitting in a resource we own.

Paired with this build's already-located camera registers — **`ViewProjectionMatrix` at `c0` ×4** —
the shape of a stereo implementation here is now fully specified without a single launch:

1. render the frame twice;
2. per eye, write the eye's view-projection to `c0`;
3. per eye, bind a stereo texture whose `.b` matches that eye's sign, with matching separation and
   convergence in `.r`/`.g`;
4. leave all 28,017 shaders exactly as shipped.

That is not a plan this pass invented — it is the division of labour NVIDIA designed, with **us in
the driver's role**.

## ⚠️ One tension this pass could not resolve, stated rather than smoothed over

Epic's own UDK page for this integration is titled **"Unreal Engine 3 and NVIDIA 3D Vision *Direct*"**
`[reported 2026-09-01]`, and 3D Vision *Direct* is the mode in which **the application** renders both
eyes itself, rather than the driver duplicating draw calls. If that is what UE3 shipped, the status
note's optimistic reading is right on the nose: the engine already contains a two-eye render path.

Pulling the other way: a **`.b` channel that tells the shader which eye it is in** is the signature of
the *Automatic* correction pattern. An application rendering in Direct mode already knows which eye it
is drawing and does not need to be told by a texture. That is an argument that the shaders sampling
this texture are doing **screen-space correction** over a driver-duplicated frame, not producing the
eye split themselves.

**Both readings are `[reported]`/`[hypothesis]`, and the evidence genuinely points both ways.**
Fortunately the plan above does not depend on which is true — it works either way, because in both
cases the texture is the thing the shaders read and the proxy is the thing that binds it.

**Fetch caveat:** the Epic page is known only by title and by two facts search reports from it
(`AllowNvidiaStereo3d=True` in the engine ini; **stereo works in fullscreen only and not in the
editor**) — every direct fetch of `docs.unrealengine.com/udk/*` returned **HTTP 403** this session.
The fullscreen-only restriction is worth noting on its own: it is a real constraint on any live test,
and it would explain a windowed test showing nothing.

## Sources

- https://archive.docs.nvidia.com/gameworks/content/technologies/desktop/nv3dva_using_nvstereoh.htm
- https://archive.docs.nvidia.com/gameworks/content/technologies/desktop/nv3dva_stereoscopic_issues.htm
- https://archive.docs.nvidia.com/gameworks/content/technologies/desktop/nv3dva_background.htm
- https://docs.unrealengine.com/udk/Three/ThreeDVision.html (403 on fetch; title and two facts via search)
- https://nvidianews.nvidia.com/_gallery/download_pdf/54481935f6091d2735000245/
