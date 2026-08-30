# This portfolio's own cross-engine VR library explains exactly why vorpX works so well here, and flags a viable backup route

**Status:** 🆕 new · **Priority:** medium — context/validation for the existing vorpX topic, plus a
concrete backup plan if the from-scratch engine-level approach hits a wall.

## What was found

This portfolio maintains its own public, engine-agnostic knowledge library,
[`flat-to-vr-cross-engine-research`](https://github.com/TefMeister/flat-to-vr-cross-engine-research)
(not specific to this game — a shared resource read for context). Its `docs/generic-drivers/README.md`
documents exactly the class of tool this project's own vorpX precedent (previous sweep) belongs to,
with detail worth folding in:

- **vorpX's Geometry 3D mode "works best on D3D9 games specifically"** — direct confirmation, from
  this portfolio's own accumulated knowledge, of *why* Alice's vorpX result (true Geometry 3D, not
  just Z-Buffer) is unsurprising and credible: D3D9's older, simpler rendering model is exactly
  vorpX's best-case scenario. Geometry 3D works by rendering the scene twice, once per eye — real
  stereoscopic depth, at a real cost (~50% framerate).
- **A documented alternative/backup path**: `D3D9 game → dgVoodoo2 (wraps D3D9 calls onto D3D11) →
  geo-11 (free, D3D11-only stereo driver) → stereo 3D`, optionally paired with a `3Dmigoto`-class
  per-game shader fix for sharper results than vorpX's cheaper Z-Buffer fallback would give. The
  library notes roughly half of D3D9 games wrap cleanly through dgVoodoo2 — not guaranteed, but a
  real, documented fallback category if needed.
- **Alice already has exactly the per-game shader-fix piece this alternate path wants**: the
  companion HelixMod topic (previous sweep) found a mature, working stereo-3D fix for this exact
  game. Per the library's own guidance ("games with existing geo-11/3Dmigoto fixes" → favor the
  geo-11 route), Alice is unusually well-positioned for this backup path specifically, should the
  primary from-scratch engine-level VR conversion hit a wall worth falling back from.
- **An important scope reminder, not a limitation specific to Alice**: the library is explicit that
  both vorpX and geo-11 (the *generic-driver* category) top out at seated/head-look experiences —
  no native 6DoF, no true positional motion-controller tracking in world space. (vorpX's own
  "motion controllers emulate a gamepad perfectly" claim, per the companion vorpX topic, is about
  *input mapping* — using motion-controller buttons/sticks as a virtual gamepad — not spatial 6DoF
  hand presence; worth being precise about that distinction so it isn't over-read.) This project's
  actual goal (full engine-level VR with real 6DoF) sits in the library's separate "engine adapter"
  category, which vorpX/geo-11 aren't examples of — consistent with, not a contradiction of, this
  project's existing ambitions.

## Why this matters

Mostly confirmatory/context-building rather than a new lead: it explains the mechanism behind an
already-strong signal, and formalizes a genuine backup plan (dgVoodoo2 → geo-11 + the existing
HelixMod-class fix) that's worth keeping in mind if the primary engine-level approach (informed by
the companion `enslaved-vr` findings) proves harder than expected.

## Concrete next step

No immediate action — record the geo-11/dgVoodoo2 backup path in `ENGINE-DOSSIER.md` §12 as a
fallback option, not a plan to pursue now.

## Sources

- https://github.com/TefMeister/flat-to-vr-cross-engine-research (`docs/generic-drivers/README.md`, this user's own portfolio resource)
