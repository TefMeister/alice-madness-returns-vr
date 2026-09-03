# The game ships its own native stereoscopic-3D camera system — and it already works correctly, except for the UI layer

**Status:** 🆕 new · **Priority:** very high — potentially the single most important finding for
`ENGINE-DOSSIER.md` §6/§7: this game may not need its per-eye projection math discovered from
scratch at all.

## What was found

Following up the companion vorpX topic (previous sweep) with a search specifically for a HelixMod/
3Dmigoto fix turned up **[Helix Mod: Alice: Madness Returns](https://helixmod.blogspot.com/2012/02/alice-madness-returns-written-by-chiz.html)**
(by "Chiz" — the same author credited for the original Prince of Persia 2008 fix elsewhere in this
portfolio's research). The critical detail is in the fix's own framing: **"Even though it comes with
Stereoscopic support it wasn't 100% but Your fixes made 100%."**

This means **Alice: Madness Returns ships with a real, built-in stereoscopic-3D rendering mode** —
not something added by a mod, but a feature the developers themselves implemented (very plausibly
using NVIDIA's official 3D Vision SDK integration path, common for UE3 titles of this era targeting
"NVIDIA 3D Vision Ready" certification). The HelixMod fix's job was narrow and specific: it **"push[es]
2D UI to 3D depths making crosshair and enemy icons accurate and usable in 3D Vision"** — i.e. the
native implementation got the actual 3D world geometry/camera right, and only left the 2D UI overlay
(crosshair, enemy icons) rendering flat at screen depth, which the fix corrects. Per the fix's own
description, this was a **shader-level UI-layer intervention only** — not a camera or world
projection matrix change.

## Why this is potentially huge for this project

If the native stereoscopic mode's core camera/projection handling was already correct enough that a
third-party fix only needed to touch UI depth, that implies **this game's own shipped code already
contains a working per-eye camera/projection override mechanism** — exactly the thing `ENGINE-DOSSIER.md`
§6 exists to reverse-engineer. Possibilities worth investigating live, roughly most-to-least
promising:
1. **A native in-game "Stereo 3D" toggle/setting might exist and be directly usable or inspectable**
   — the companion PCGamingWiki-talk-page search (blocked by this pass's tooling, worth revisiting)
   suggests players have discussed this option specifically, which means it's likely exposed
   somewhere in-game or via a config value, not just an internal, inaccessible code path.
2. **If reachable, toggling it live and observing behavior (with a debugger or memory scanner
   attached) could reveal the actual per-eye projection mechanism directly** — watching what changes
   in the constant-register/matrix data between mono and native-stereo rendering would be far more
   direct than reverse-engineering the mono path alone and guessing at a per-eye override scheme.
3. Even if the native mode turns out to be NVIDIA-3D-Vision-specific (e.g. gated behind detecting
   3D Vision hardware/driver flags, or only active via a specific launch condition) rather than a
   generic engine capability, understanding *how* it's gated is itself valuable — it may be possible
   to force-enable it without actual 3D Vision hardware for inspection purposes.

## Caveat

This is a strong, concrete lead, not a confirmed shortcut. This research pass could not directly
confirm (PCGamingWiki blocked automated access) exactly how the native option is exposed/enabled, or
whether it's still functional on the current Steam build (game settings/features sometimes get
stripped in later patches). Live investigation should verify this exists and is reachable before
building a plan around it.

## Concrete next step

Before starting shader-reflection work on the mono rendering path from scratch, check whether
Alice: Madness Returns has a native "Stereo 3D" setting (in-game options menu or a config/`.ini`
value) and whether it's still functional on the current build. If it exists and can be toggled live,
that's very plausibly the fastest route to understanding §6/§7's actual answer for this game.

## Sources

- https://helixmod.blogspot.com/2012/02/alice-madness-returns-written-by-chiz.html

## Addendum 2026-09-03 — what the menu's `Stereo3D` row is wired to (from the modding side, static)

**Answered without a launch, from the unpacked exe's string table** `[inferred-static 2026-09-03]`:
`UAliceGameEngine` exposes 23 native script functions including **`EnableStereo3D`** (the exe carries
UE3's own native-thunk name `intUAliceGameEngineexecEnableStereo3D`, so its *existence* is direct);
22 standalone `Exec*` settings identifiers include **`ExecStereo3D`**; and the Scaleform menu in
`AliceGame.u` lists the same rows in menu order. So the `Stereo3D` row goes `ExecStereo3D` →
`ExecConfigData` → native `EnableStereo3D`. The *routing* is an inference from three lists agreeing
item-for-item, not a decompilation, and is held at that strength.

The engine gate `AllowNvidiaStereo3d` is already `True` in `BaseEngine.ini` — inside the vendor's own
`; NVCHANGE_BEGIN: Jiayuan -- Allow Stereo 3D by default` markers — and in the user's
`AliceEngine.ini` `[measured 2026-09-03]`. Those markers date the stereo support as an
**NVIDIA-supplied patch to UE3**, consistent with `NvStereoEnabled` appearing in 28,017 of 43,025
pixel shaders and with the NVAPI scan returning Automatic.

**Do not research** what the toggle is wired to or whether the engine gate is on — both are settled.
What the modding side *did* ask for is whether NVIDIA 3D Vision Automatic is reachable at all on a
current driver — see the 2026-09-03b topic. Full write-up on the modding side:
`modding-notes/2026-09-03b-the-stereo3d-menu-entry-answered-without-a-launch.md`.
