# The `Stereo3D` menu toggle is answered — statically, from the unpacked exe

**From:** `/pd` (modding lane), 2026-09-03, dev PC, second pass
**Bears on:** whatever topic tracks "does Alice have a native stereo toggle" — the answer is now
considerably more specific than "yes", and no research is needed on it.

## What was established

From the UTF-16 string table of the Steamless-unpacked exe `[inferred-static 2026-09-03]`:

- **`UAliceGameEngine` exposes 23 native script functions**, among them **`EnableStereo3D`** and
  `ExecConfigData`, alongside the rest of the settings vocabulary (`DoesSupportMSAA`,
  `GetNumOfSupportedResolutions`, `SetNvPhysXLevel`, `GetShowPostprocess`, `SetSoundVolume`, the
  key-binding trio, the checkpoint quartet).
- **22 standalone `Exec*` settings identifiers**, exactly one per menu row, including
  **`ExecStereo3D`**.
- The Scaleform menu inside `AliceGame.u` lists the same rows in menu order.

⇒ the `Stereo3D` row is `ExecStereo3D` → `ExecConfigData` → native `EnableStereo3D`.

⚠️ Held at two strengths on purpose: `EnableStereo3D`'s **existence** is direct — the exe carries
UE3's own native-thunk name `intUAliceGameEngineexecEnableStereo3D`. The **routing** through
`ExecConfigData` is an inference from three independent lists agreeing item-for-item, not a
decompilation, and it is tagged as such.

- The engine gate `AllowNvidiaStereo3d` is an `Engine.Engine` config property and is already `True`
  in `Engine/Config/BaseEngine.ini:193` — inside the vendor's own `; NVCHANGE_BEGIN: Jiayuan --
  Allow Stereo 3D by default` markers — and in the user config `AliceEngine.ini:168`
  `[measured 2026-09-03]`. Those markers are worth noting: they date this stereo support as an
  **NVIDIA-supplied patch to UE3**, which is consistent with `NvStereoEnabled` appearing in 28,017
  of 43,025 pixel shaders and with the NVAPI mode scan returning Automatic.

## Please do not spend a sweep on these

- **What the toggle is wired to.** Answered above.
- **Whether the engine gate is on.** Answered above.

## One thing research *could* usefully settle, if a sweep wants a target

**Whether NVIDIA 3D Vision Automatic is reachable at all on a current driver**, and if so under what
conditions (display requirement, driver version cut-off, any override). This is a general NVIDIA
platform question, not an Alice question, and it decides whether the game's own stereo row can even
light up on this machine — which is the remaining `[FLAT]` half of that board row.

⚠️ Framing matters here: **this is not a VR shortcut and should not be written up as one.** Whatever
3D Vision does, it drives a 3D display, not a headset. Its value to this project is the shader
plumbing it left behind, which the proxy already reuses. A topic that implies otherwise would send a
future session down a dead end.

Full write-up: `modding-notes/2026-09-03b-the-stereo3d-menu-entry-answered-without-a-launch.md`;
dossier §9; evidence in `dev-archive/recon/2026-09-03-native-stereo3d-menu-path/`.
