# Research index

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **reviewed** — a modding session has read it and factored it into a decision, but nothing shipped from it yet.
- ✅ **incorporated** — directly led to a real change (code, a test, a note) in one of the other five repos; linked below.
- ❌ **dead end** — checked out, didn't pan out; kept for the record so it isn't re-investigated from scratch.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-08-25 | [Native stereo3D mostly works, only UI is broken](topics/2026-08-25-native-stereo3d-mostly-works-only-ui-broken.md) | 👀 reviewed | HelixMod's fix reveals the game ships its OWN built-in stereoscopic-3D camera system that's already correct except for flat UI depth — potentially means the per-eye projection work is already solved by the developers, not something to reverse-engineer from scratch. Factored into ENGINE-DOSSIER.md §6/§12. |
| 2026-08-25 | [UE3 public camera architecture documentation](topics/2026-08-25-ue3-public-camera-architecture-documentation.md) | 👀 reviewed | Unlike every other proprietary-engine front in this portfolio, UE3's camera system is publicly documented end-to-end: PlayerController/UpdateViewTarget at the gameplay layer, and the view-projection matrix in shader constant register c0 (with a PreViewTranslation split) at the shader layer. Factored into ENGINE-DOSSIER.md §6. |
| 2026-08-25 | [vorpX Geometry 3D + motion controllers — strongest precedent](topics/2026-08-25-vorpx-geometry3d-motion-controllers-strongest-precedent.md) | 👀 reviewed | vorpX already delivers true Geometry 3D stereo AND working motion-controller emulation for this exact game — the best VR-feasibility signal found anywhere in this portfolio so far. Factored into ENGINE-DOSSIER.md §12. |
| 2026-08-25 | [MadnessPatch — comprehensive prior art](topics/2026-08-25-madnesspatch-comprehensive-prior-art.md) | 👀 reviewed | An open-source community patch by a known modder (EchoPatch/MarkerPatch) already exposes the dev console (F2), disables camera smoothing (VR-critical), fixes framerate-dependent physics, and confirms PhysX — touches nearly every open dossier section at once. Factored into ENGINE-DOSSIER.md §3/§6/§8/§9/§12. |
| 2026-08-25 | [Native FOV console command confirmed](topics/2026-08-25-native-fov-console-command-confirmed.md) | 👀 reviewed | `FOV <10-150>` is a real, config-bindable native console command (via BaseInput.ini), confirmed by independent Nexus ultrawide mods — a low-risk starting point for early camera probing. Factored into ENGINE-DOSSIER.md §9. |
| 2026-08-25 | [DRM history: EA Cuckoo removed 2022](topics/2026-08-25-drm-history-ea-cuckoo-removed-2022.md) | ✅ incorporated | EA's "Cuckoo" authentication DRM (tied to the 2016 delisting saga) was removed from the relisted Steam build via a January 2022 patch — explains why our own M0 static recon found no DRM. Factored into ENGINE-DOSSIER.md §4. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
