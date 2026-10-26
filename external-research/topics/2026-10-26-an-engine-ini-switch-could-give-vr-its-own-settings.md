# An engine-ini switch on the command line could give VR its own settings file

*For the board's `[PD]` row "VR screen effects off when OpenXR is on" (2026-10-26): `AliceEngine.ini` in My Games has
`MotionBlur=True` and `DepthOfField=True`; the VR rule wants every blur off in VR while flat play stays untouched, and
Unreal Engine 3 reads the ini at start, before our Direct3D hooks run.*

## What was found `[reported 2026-10-26]`

- The Unreal command-line argument list published on Epic's documentation, as mirrored in ikrima's *Gamedev Guide*,
  has an "override INI" group: `ENGINEINI=<file>`, `GAMEINI=<file>`, `INPUTINI=`, `UIINI=`, `COMPATINI=`,
  `LIGHTMASSINI=`, `EDITORUSERSETTINGSINI=` and their `DEF...` forms. Note: these are written **without** the leading
  `-`. The set (Compat, Lightmass, EditorUserSettings, UI) is the Unreal Engine 3 family of config files.
- A forum report on Epic's old answers site says the trick worked for starting an Unreal Engine 3 server with specific
  ini values, and no longer worked on Unreal Engine 4 (search result summary only; the page itself was not opened).
- Epic's own UE3 command-line page (UDK docs) refused automated fetches (HTTP 403), so the exact UE3 wording is not
  confirmed here.

## Why it matters for Alice `[hypothesis]`

If Alice's UE3 build honours `ENGINEINI=`, the VR launch can point at a **second engine ini** (a copy of
`AliceEngine.ini` with `MotionBlur=False`, `DepthOfField=False` and any other screen-painted effect off), while the
flat launch keeps the normal file. That is the "VR-only copy of the setting" the row asks for, chosen by the launcher,
with no write to the player's own file and nothing for the proxy to do before the engine reads its config.

Risks to check: Unreal Engine 3 rebuilds missing or outdated user ini files from the `Default*.ini` files, and may
write settings back on exit, so the VR copy could be overwritten or regenerated; the switch may be stripped from a
shipping build.

## The concrete next step

One flat launch with `ENGINEINI=<path to a test copy>` in which one visible setting differs (for example
`MotionBlur=False`), then read the game's log for the config files it loaded and look for the setting change. If the
log names the test copy, the route is live. If not, fall back to the launcher writing the setting before start and
putting it back after.

## Sources

- ikrima, *Gamedev Guide*, "Useful command line arguments" (override INI table, citing Epic's command-line docs),
  https://ikrima.dev/ue4guide/wip/useful-command-line-arguments/
- Epic Games, UDK "Command-line Arguments" (UE3), https://docs.unrealengine.com/udk/Three/CommandLineArguments.html
  (not readable by automated fetch on 2026-10-26).
- Epic Games forum (answers.unrealengine.com), "Launching a server with specific ini values",
  https://answers.unrealengine.com/questions/707407/view.html (search summary only).
