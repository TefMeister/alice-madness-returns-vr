# Unreal Engine 3's camera/projection architecture is publicly documented — from the UnrealScript camera-actor layer down to the shader constant register

**Status:** 🆕 new · **Priority:** very high — directly targets `ENGINE-DOSSIER.md` §6 (camera &
projection delivery, "the crucial section") with something none of this portfolio's other
proprietary-engine fronts have: real, official, public engine documentation.

## Why this is different from every other project in this portfolio

Every other front here (Burnout Paradise, Mad Max, Prince of Persia, Manhunt) runs on a fully
proprietary, undocumented in-house engine — camera/projection work has to be discovered entirely
from scratch via live shader reflection and disassembly. **Alice: Madness Returns runs on Unreal
Engine 3**, which Epic Games licensed broadly and partially documented publicly (and later released
much of, source-available, as the free Unreal Development Kit, UDK) — meaning a real, official
technical reference for how UE3's camera system works exists, independent of this specific game's
binary. This won't replace live verification (this specific title's build could deviate), but it
gives §6 a genuine head start no other project here has.

## What's documented, at two levels

**Gameplay/UnrealScript layer** (`docs.unrealengine.com`'s UDK Camera Technical Guide, and the
community-maintained BeyondUnreal wiki's `UE3:Camera` page, which typically mirrors/expands the
official docs):
- The `PlayerController` owns the camera: key properties are `PlayerCamera` (the active camera
  object), `CameraClass`, and `ViewTarget` (what the camera is currently looking at/through).
- FOV lives on the controller too: `FOVAngle` (current) and `DefaultFOV`.
- **`UpdateViewTarget` is the key per-frame function** — described as the one to override for custom
  camera behavior, updating the view target's position/rotation/FOV each frame. This is the natural
  starting point for understanding *where in the frame* this game's camera decision gets made,
  before it ever reaches the renderer.
- `GetPlayerViewPoint` returns the actual point-of-view (position + rotation) ultimately handed off
  to rendering.

**Shader/renderer layer** (Epic developer forums, UDK material/shader documentation):
- **UE3's view-projection matrix is documented as living in vertex shader constant register `c0`**
  (referred to as `VSR_ViewProjMatrix` in community/forum discussion), used to transform from world
  space to projection space — this is exactly the "exact constant-buffer slot" question §6 asks,
  answered by public documentation rather than needing to be discovered from a cold disassembly.
  D3D9 doesn't have D3D11-style constant buffers, so this is a **shader constant register**, not a
  cbuffer slot — consistent with the dossier's existing D3D9 caveat.
- **`PreViewTranslation`** is UE3's documented technique for splitting the view matrix into a
  translation component and a separate rotation matrix (`ViewMatrix = PreViewTranslation *
  ViewRotationMatrix`), specifically to preserve floating-point precision in large worlds — vertex
  positions get shifted into camera-relative ("Translated") space before the rotation/projection is
  applied. This is directly relevant to §6's "handedness/row-column convention" question, and is a
  well-known UE-family pattern (it persisted conceptually all the way into modern UE4/5, per Epic's
  current documentation, which is why current-day Epic docs and forum threads about it are still
  findable and applicable to this 2011-era UE3 title).

## Why this matters concretely

This gives `ENGINE-DOSSIER.md` §6 a genuine hypothesis to test against the live binary, rather than
starting from zero: expect the game's `PlayerController`/camera-actor UnrealScript logic to compute
position/rotation/FOV once per frame via something resembling `UpdateViewTarget`, and expect the
resulting view-projection matrix to reach the D3D9 vertex shaders via constant register `c0`, built
from a separately-tracked camera-relative translation (`PreViewTranslation`) and rotation. Live
shader-reflection work should confirm or correct this against the actual binary — this is public,
generic UE3 knowledge, not something verified against this specific game's build yet — but it's a
real, testable starting point instead of a blank page.

## Concrete next step

When shader-reflection work on `AliceMadnessReturns.exe` begins, check constant register `c0` first
for the view-projection matrix, and look for a `PreViewTranslation`-style split (a separately-fed
camera-position vector distinct from the rotation/projection data) — confirm or correct against this
project's own findings, and update §6 with live-verified specifics either way.

## Sources

- https://docs.unrealengine.com/udk/Three/CameraTechnicalGuide.html
- https://wiki.beyondunreal.com/UE3:Camera_(UDK)
- https://forums.unrealengine.com/t/bound-shader-view-matrix/451510
- https://forums.unrealengine.com/t/using-the-view-projection-matrix-in-compute-shaders/274999
