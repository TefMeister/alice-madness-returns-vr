# 2026-09-01 — The native-stereo lead holds up: NVIDIA's UE3 stereo changes are integrated and enabled by default

**Date:** 2026-09-01, dev machine. **The game was never launched** (a parallel session owns the
machine's one "game may run" slot). Static analysis of shipped files; nothing modified.

The queued next step was *"check for a native in-game 'Stereo 3D' toggle before any from-scratch
shader-reflection work"*. Partially answered statically, with a twist that changes where to look.

---

## The finding

`Engine/Config/BaseEngine.ini` contains, verbatim:

```
; NVCHANGE_BEGIN: Jiayuan -- Allow Stereo 3D by default
AllowNvidiaStereo3d=True
; NVCHANGE_END: Jiayuan -- Allow Stereo 3D by default
```

Those `NVCHANGE_BEGIN`/`NVCHANGE_END` markers are **NVIDIA's own convention for changes they made to
a licensee's UE3 branch** — the same file also carries `NVCHANGE_BEGIN: DJS - Add APEX LOD settings
to SystemSettings`, from the APEX/PhysX work this build is already known to include.

So: **Alice: Madness Returns ships an NVIDIA stereo-3D integration, and it is switched on by
default.** `[inferred-static 2026-09-01]` — a config entry and its NVIDIA-authored comment; nothing
observed running.

This **supports** the 2026-08-25 research lead ("a 2012 community fix implies Alice ships its own
working native stereoscopic-3D camera mode — the fix only had to correct flat 2D UI depth"). A
community fix that only had to repair UI depth is exactly what you would expect if the world
rendering was already correctly stereo, and this is the mechanism that made it so.

## The twist: it is config/engine-level, not an exe feature

A scan of `AliceMadnessReturns.exe` for stereo-related identifiers found **essentially nothing** —
two hits, both false positives (`ClipDepth`, and a random byte sequence). **So the search that would
naturally be run first — grep the executable — returns a false negative here.** The integration
lives in the UE3 engine layer and its configuration, not in game-side strings.

Worth recording as a method note: for a UE3 title, *"is feature X present?"* is a question about the
**INIs and the packages**, and an empty exe scan is not evidence of absence.

## ⚠️ What is NOT established

* **That the stereo path still works.** Like Alan Wake's, this is an **NVIDIA 3D Vision** era
  integration, and 3D Vision was discontinued. `AllowNvidiaStereo3d=True` grants permission; it does
  not prove the driver stack it talks to still exists. A modern machine may find the flag on and the
  feature inert.
* **That there is an in-game toggle.** The queued task assumed a UI option. What was found is a
  config default. No menu string was located this session.
* **What it does to the camera.** Whether this drives a genuine per-eye view-projection (usable) or
  a driver-side reprojection (much less usable) is not established, and that distinction decides
  whether this is a shortcut or a curiosity.

## Why it is still the right thing to chase first

The dossier called this "the strongest VR-feasibility case in the entire portfolio". If the engine
already produces a correct per-eye view, the project's hardest problem is solved and the work
becomes plumbing that view to a headset. The cost of checking is one config edit and one launch,
against a from-scratch shader-reflection effort measured in sessions. **The asymmetry justifies
checking first even though the odds are uncertain.**

## Next

1. **Static, no launch:** find what reads `AllowNvidiaStereo3d` and follow it — does it gate an
   NVAPI call (same shape as Alan Wake's `Activate Stereo`), or an engine-side per-eye render? That
   single question decides whether this is a shortcut or a dead end, and the answer is in the
   binary.
2. **Then, live:** confirm whether anything changes with it toggled, and look for the UI option the
   original lead implied.

Unchanged from before: `DisableMouseSmoothing` remains a likely VR prerequisite.

🤖 Static analysis of shipped configuration and binaries. The game was not launched, nothing was
modified, and no game content was copied here — only the three config lines quoted above, as
evidence.
