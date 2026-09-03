# The `Stereo3D` menu entry is answered without a launch — it calls a native `EnableStereo3D`

**2026-09-03, dev PC, `/pd` (parallel development), second pass.**
**The game was not launched. Nothing here has been run against Alice.**

The board carried this as a `[FLAT]` row: *check the `Stereo3D` entry the game exposes in its own
video-options list (`AliceGame.u`, beside Gamma and Resolution) — the queued "is there a native
toggle" is a yes, but **what it actually does needs the game up**.*

Most of it did not. The row was an assumption, and the answer was in files already on disk.

---

## 1. What the menu row is wired to

Read from the **Steamless-unpacked** exe the earlier pass produced — its UTF-16 string table, which
survives intact. `[inferred-static 2026-09-03]`

**`UAliceGameEngine` exposes 23 native script functions**, and they are recognisably the settings
menu's whole vocabulary:

```
DoesSupportMSAA          GetNumOfSupportedResolutions   GetSupportedResolutions
EnableStereo3D           SetNvPhysXLevel                GetShowPostprocess
SetSoundVolume           ExecConfigData                 ExecRebindKey
ExecResetKeyBindings     GetAliceKeys / SetAliceKeys / GetAliceKeyIndex
GetCompatCompositeIndex  GetCurrentDeviceID / SetCurrentDeviceID
SaveCheckpoint / LoadCheckpoint / FindCheckpointData / DeleteCheckpoints
HasStorageDeviceBeenRemoved   GetDestructionMaxChunkCount   LaunchAlice1
```

Alongside them sits a complete family of **standalone settings identifiers**, one per menu row:

```
ExecAntiAlias      ExecGammaConfig      ExecMotionBlur       ExecScreenResolution
ExecAttackType     ExecGamepadType      ExecMouseSpeed       ExecSoundEffectVolume
ExecControlLayout  ExecGraphicsQuality  ExecMusicVolume      ExecStereo3D
ExecDifficulty     ExecInputAxis        ExecPhysXLevel       ExecSubtitles
ExecDynamicShadows ExecInputKey         ExecPostprocess      ExecVoiceVolume
ExecInvertY        ExecLowestDifficulty
```

And the Scaleform side agrees. The compressed ActionScript inside `AliceGame.u` carries the settings
list in menu order — `Volume | Music | Voice | Subtitles | Gamma | GraphicsQuality | Resolution |
AntiAlias | **Stereo3D** | Blur | Layout` — plus accessor calls (`setAntiAlias`, `setScreen(`,
`GetNumOfSupportedResolutions`, `PhysXLevel`, `DynamicShadow`, `PostProcess`) that match the native
list one for one.

**So: the `Stereo3D` row is `ExecStereo3D`, handled through `ExecConfigData`, and the thing it
switches is the native `AliceGameEngine.EnableStereo3D`.**

### How strongly is that held?

The **existence** of `EnableStereo3D` as a native script function on `AliceGameEngine` is direct —
the exe contains the thunk name `intUAliceGameEngineexecEnableStereo3D`, which is exactly how UE3
names the native call thunk for a script-callable native. That part is not an inference.

The **linkage** — that the menu row drives it via `ExecConfigData` — is an inference from three
things agreeing: the `Exec*` identifier family is complete and one-per-menu-row; `ExecConfigData` is
itself one of the 23 natives; and the Scaleform menu list matches the native list item for item. I
have **not** decompiled `ExecConfigData`, so this is `[inferred-static 2026-09-03]`, not proven.

## 2. The engine-level gate is already open

`AllowNvidiaStereo3d` is a config property of **`Engine.Engine`** — in the exe it sits in a run of
config names each followed by its class (`AllowTargetingSM2` / `Engine.Engine`,
`AllowScreenDoorFade` / `Engine.Engine`, `AllowNvidiaStereo3d` / `Engine.Engine`).

It is **already `True`** in two places on this machine `[measured 2026-09-03]`:

- `Engine/Config/BaseEngine.ini:193`, wrapped in the vendor's own markers —
  `; NVCHANGE_BEGIN: Jiayuan -- Allow Stereo 3D by default`
- the user config, `Documents\My Games\Alice Madness Returns\AliceGame\Config\AliceEngine.ini:168`

Those `NVCHANGE` markers matter: they show this stereo support is an **NVIDIA-supplied patch to
UE3**, which is consistent with everything the earlier pass found — `NvStereoEnabled` in 28,017 of
43,025 pixel shaders, `NvStereoFixTexture`, and the NVAPI scan coming back **Automatic**.

## 3. What this does and does not change

**Does:** the `[FLAT]` row shrinks from "find out what the toggle does" to one narrow question that
genuinely needs the game — *does flipping it visibly change anything on this machine* — and the
answer is now predictable enough to pre-commit. It also means the engine gate is not what would stop
it: `AllowNvidiaStereo3d` is on.

**Does not:** it does not give us VR, and it should not be mistaken for a shortcut. 3D Vision
*Automatic* is a driver feature that renders two views by transforming vertex output; it needs
NVIDIA's stereo driver stack, which is deprecated on current drivers and normally refuses without a
3D-capable display. Nothing here suggests the native path can be made to drive a headset. **Its
value to this project is what the earlier pass already established** — the shipped shaders' stereo
plumbing (`NvStereoEnabled`, `NvStereoFixTexture`) is the thing our proxy reuses, and that is
unchanged by this.

### What is NOT established

- That `ExecConfigData` is what actually consumes `ExecStereo3D` (see §1 — inference, not
  decompilation).
- What `EnableStereo3D` does internally. It may call `NvAPI_Stereo_*` (the exe resolves NVAPI
  dynamically — `nvapi.dll` / `nvapi_QueryInterface` are present as ASCII), or it may only set the
  shader flag. **Not determined**, and worth not guessing at: the earlier pass's NVAPI scan
  established the *mode*, not the call sites.
- Whether the menu row is even selectable without a 3D Vision-capable setup. Some UE3 NVIDIA patches
  grey the row out when the driver reports no stereo.

### The diagnostic that would show this reading is wrong

If the game is launched and the video options list has **no `Stereo3D` row at all**, then either it
is gated on driver support (likely) or the identifier family is not the menu's source (which would
make the whole §1 inference wrong). The tell between those two: if the row is absent but other
`Exec*` rows in the same family are present, it is gating; if the menu looks nothing like that
identifier list, the inference is wrong.

## 4. Housekeeping checked, not assumed

The unpacked exe this pass read lives **only** in a previous session's temp scratchpad, which is the
shape of problem §7 exists for. It is **not** at risk: it is game content and must not be committed
anyway, and the method to regenerate it is already recorded in
`dev-archive/recon/2026-09-03-steamstub-and-matrix-layout/nvapi-direct-vs-automatic-scan.txt`
(Steamless v3.1.0.5, SteamStub Variant 3.1 x86) together with the validation numbers that say the
unpack worked. Nothing to rescue.

## Files

- `dev-archive/recon/2026-09-03-native-stereo3d-menu-path/2026-09-03-native-settings-surface.txt` —
  the 23 natives, the 22 `Exec*` identifiers, and every "Stereo" string in the exe. Interface
  metadata only; no game code is committed.
