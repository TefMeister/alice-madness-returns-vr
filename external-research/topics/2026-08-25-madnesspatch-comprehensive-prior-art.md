# MadnessPatch (Wemino, open-source): a mature community patch that already exposes the dev console, disables camera smoothing, and fixes framerate-dependent physics — touches nearly every open dossier section

**Status:** 🆕 new · **Priority:** very high — directly informs `ENGINE-DOSSIER.md` §3 (console),
§4 (injection), §6 (camera), §8/§9, and §12 (framerate-dependent physics risk).

## What it is

**[MadnessPatch](https://github.com/Wemino/MadnessPatch)** is an open-source, actively-maintained
C++ patch for the PC port of Alice: Madness Returns, by **Wemino** — a modder with an established
track record on this portfolio's radar already: the same author built **EchoPatch** (F.E.A.R.) and
**MarkerPatch** (Dead Space 2), both well-regarded community rendering/input patches for other
titles. PC Gamer covered this patch's release directly, calling it a "huge fanmade patch" fixing the
PC port's long-standing janky-ness. Installation is a drop-in: extract into the game's `Win32` folder
alongside `AliceMadnessReturns.exe` (this research pass did not confirm the exact proxy-DLL name/hook
point from the README alone — worth checking the release archive's file listing directly once live
investigation starts).

## Why this is unusually valuable prior art — it answers several open dossier questions at once

- **§3 (developer console): "Developer console access (F2)" is an explicit, documented feature.**
  This game's built-in UE3 console is reachable via a normal, publicly-documented hotkey once this
  patch is applied — directly parallel to how MMConsole solved the equivalent problem on the Mad Max
  front, and Psychonauts' dormant dev-menu discovery elsewhere in this portfolio. Worth checking
  whether F2 works out-of-the-box (many UE3 titles bind console to a key by default; the patch may
  simply be *restoring* or *fixing* an existing binding rather than adding one from scratch) before
  assuming the patch itself is required just to reach the console.
- **§6 (camera): "Optional camera smoothing disablement"** is a directly-relevant, already-solved
  problem. Per the patch's own issue description, the base game applies **heavy mouse
  smoothing/negative acceleration and input deadzones** — exactly the kind of camera-response lag
  that would be actively harmful for VR head tracking (any smoothing/interpolation between input and
  camera update reads as unacceptable latency in a headset). A third party has already found and
  neutralized this, via a simple `DisableMouseSmoothing = 1` config toggle — strong evidence the
  camera-update code path is a tractable, identifiable target, not buried in something inscrutable.
- **§8/§12 (framerate-dependent physics — a real VR risk, not yet in the dossier)**: the patch fixes
  **hair/dress physics instability, projectile hitbox inconsistency, and general simulation
  behavior specifically at high framerates**. This is a genuinely important, portfolio-relevant
  finding: VR requires a high, stable frame rate (typically 90Hz+), and this UE3-era game's physics
  were evidently tuned assuming a much lower framerate ceiling. This should be recorded as an open
  risk in §12 — running this game at VR framerates may re-expose the same class of bugs this patch
  already had to fix, and the patch's own fix approach (worth understanding, not copying) is a real
  reference point.
- **Aspect-ratio/FOV/pillarboxing fixes** corroborate the companion Nexus-mods topic (this same
  sweep) that FOV is config/console-exposed (`FOV <value>`, 10–150 range) rather than buried in
  compiled shader code — consistent with UE3's well-known built-in `FOV` console command pattern.
- Miscellaneous but relevant: **PhysX CPU-mode crash elimination** confirms PhysX is the physics
  middleware (fills an open §2 blank); **XAudio2 upgrade** and **SDL3-based controller input**
  (overriding XInput, adding PlayStation/Switch controller support) are useful context for this
  project's own eventual input-handling work, though not camera/projection-relevant.

## Concrete next step

When live investigation starts: try the F2 console hotkey early (with or without the patch applied,
to determine whether it's native-UE3-default or patch-added) per §3/§9; treat
`DisableMouseSmoothing`-equivalent behavior as a required setting/patch for any VR head-tracking
work, not an optional nicety; and record the framerate-dependent-physics risk in §12 as something to
test explicitly once running at VR-target framerates. As with all prior-art tools in this portfolio,
read MadnessPatch's public documentation and release notes for mechanism understanding only — never
copy its code or redistribute it inside this project.

## Sources

- https://github.com/Wemino/MadnessPatch
- https://github.com/Wemino/MadnessPatch/releases
- https://www.pcgamer.com/games/action/the-sequel-to-one-of-my-favorite-3d-platformers-always-had-a-janky-pc-port-but-a-huge-fanmade-patch-just-dropped-in-hopes-to-fix-it/
- https://www.resetera.com/threads/alice-madness-returns-pc-version-gets-long-standing-issues-fixed-by-mod-by-echopatch-fear-markerpatch-dspace2-modder-wemino.1356358/
