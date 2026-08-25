# vorpX already delivers true Geometry 3D + working motion-controller emulation — the strongest VR feasibility precedent found across this whole portfolio

**Status:** 🆕 new · **Priority:** very high — directly seeds `ENGINE-DOSSIER.md` §4/§6/§12
(injection foothold, camera/projection feasibility, and North-Star risk).

## What was found

Alice: Madness Returns has a mature, actively-promoted **vorpX** profile, described in vorpX's own
community/marketing material as "a fantastic platform adventure built from the ground up to be
played in 3D." It appears on vorpX's curated **"Geometry VR Game List"** — the tier of vorpX support
reserved for games where true per-eye geometric stereo reconstruction (not a cheaper Z-buffer
approximation) is achieved — supporting both **Immersive and Cinema modes**, and, notably,
**motion controllers that "emulate a gamepad perfectly."**

## Why this is the strongest precedent found in this portfolio so far

Comparing directly against this portfolio's other fronts:
- **Burnout Paradise**: vorpX flatly fails to hook the Steam build at all.
- **Mad Max**: vorpX works with Geometry 3D and head tracking, but only in **third-person**, with no
  motion-controller support mentioned.
- **Prince of Persia (2008)**: no vorpX profile exists at all for this specific title.
- **Alice: Madness Returns**: true **Geometry 3D**, **both Immersive and Cinema modes**, and
  **working motion-controller emulation** — a materially more complete VR experience than any other
  front in this portfolio currently has third-party evidence for.

This means a third party has already solved, for this exact game: (1) finding and correctly
overriding the per-eye camera/projection math (Geometry 3D's core requirement — the same problem
this project's own §6 exists to solve), and (2) mapping VR motion-controller input onto the game's
own control scheme convincingly enough to be called "perfect" gamepad emulation. Neither is public/
reusable (vorpX is closed-source), but both are strong, concrete existence proofs that this exact
game, on this exact engine (Unreal Engine 3), does not present unusual resistance to full stereo +
motion-input VR conversion — the best evidence yet, in this portfolio, that the North Star is
realistically reachable here.

## Caveat

As with every vorpX-precedent finding elsewhere in this portfolio: this is a feasibility signal, not
a technical shortcut. vorpX's actual implementation isn't public, so this project's own §6/§7 camera/
projection investigation still needs to be done independently from the game's own D3D calls — but it
can proceed with real confidence rather than the usual "we hope this is possible" uncertainty.

## Concrete next step

Record this as the strongest available VR-feasibility signal in `ENGINE-DOSSIER.md` §12, and treat
vorpX's own in-game default settings (separation, convergence) as a rough sanity-check reference once
this project reaches its own live camera work — not to copy, but to cross-check "does our own
per-eye override produce a similarly comfortable result."

## Sources

- https://www.vorpx.com/forums/topic/a-masterpiece-is-back-alice-madness-returns/
- https://www.vorpx.com/forums/topic/geometry-vr-game-list/
- https://www.vorpx.com/forums/topic/alice-madness-returns/
