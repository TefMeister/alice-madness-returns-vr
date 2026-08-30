# 2026-08-25 — First look: Unreal Engine 3, D3D9, no DRM

Session type: static file analysis (no game launch).

## What we know for sure

- **The engine is Unreal Engine 3** — the standard `Binaries\Win32\` + `Core\` folder layout
  confirms it independently of any string search, and "Spicy Horse Games" (the developer) is
  confirmed via an internal string.
- **The renderer is Direct3D 9.**
- **Physics is NVIDIA PhysX + APEX** (cloth and destructible-mesh extensions specifically),
  with CUDA present too — likely GPU-accelerated PhysX. This is UE3's well-known standard
  physics stack for this era.
- **No DRM found** — same clean picture as Prince of Persia. Worth noting specifically because
  this is an EA-published title, the same publisher as Burnout Paradise (which needed the EA
  App just to launch). This one evidently doesn't carry that requirement.

## What's next

A `d3d9.dll` proxy DLL (same pattern as Psychonauts and Prince of Persia) is the natural M0
injection foothold.

One honest gap: no public-research sweep has happened for this project yet. Community prior
art here is currently unknown.

Full technical detail: `alice-madness-returns-vr-dev-archive`, `recon/2026-08-25-m0-static-recon/`.
