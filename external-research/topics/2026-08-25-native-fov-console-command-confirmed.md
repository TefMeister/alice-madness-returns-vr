# FOV is a native, config-bindable console command (`FOV <10-150>`) — confirmed via community ultrawide mods

**Status:** 🆕 new · **Priority:** medium — a small, concrete confirmation for `ENGINE-DOSSIER.md`
§6/§9, consistent with (and corroborating) the companion MadnessPatch topic.

## What was found

Multiple independent Nexus Mods entries for Alice: Madness Returns — **"alice32-9-ultrawide"** and
**"UltraWide And 60FPS Fix"** — both work the same way: they add a keybinding in the game's own
`BaseInput.ini` config file (under `[Engine.PlayerInput]`) that issues the game's **native `FOV`
console command** on a keypress, e.g. binding a key to run `FOV 106`. The `FOV` command itself
accepts values from **10 to 150**, acting as a straightforward camera zoom/field-of-view control —
this is Unreal Engine 3's well-known, generic built-in console command, not something specific to
this game or added by a mod.

## Why this matters

- **Directly confirms `ENGINE-DOSSIER.md` §9 (cvar/console cheat sheet) has at least one immediately
  known entry**: `FOV <value>`, config-bindable via `BaseInput.ini` without needing the console open
  live — useful both as a documented starting cvar and as independent confirmation (alongside the
  companion MadnessPatch topic's "F2 console access" finding) that this game's console/cvar system
  is real, reachable, and not obscured.
- Because this is a config-file-level integration (not a runtime memory patch), it's a low-risk way
  for this project to test/tune FOV during early live investigation, before any camera-hooking work
  begins — bind a test key to `FOV <value>` via `BaseInput.ini` and observe behavior directly.

## Concrete next step

Record `FOV <10-150>` in `ENGINE-DOSSIER.md` §9 as a confirmed, low-risk starting cvar, and consider
using the same `BaseInput.ini` keybinding approach as an easy way to probe camera/FOV behavior in the
first live session, before committing to any hooking approach.

## Sources

- https://www.nexusmods.com/alicemadnessreturns/mods/53
- https://www.nexusmods.com/alicemadnessreturns/mods/16
