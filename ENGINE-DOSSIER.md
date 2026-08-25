# Engine Dossier — Alice: Madness Returns (Unreal Engine 3)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 done — static recon complete, no external research yet (flagged as a gap). No DRM found — same clean picture as Prince of Persia. · **VR-readiness verdict:** TBD, but no environmental blockers found

## 1. Identity
- Game / build / version: Alice: Madness Returns (2011, Spicy Horse Games, published by Electronic Arts), Steam release. Exe: `Binaries\Win32\AliceMadnessReturns.exe` (17.4 MB).
- Platform & store; unofficial port? (extra fragility/legal notes): Steam (PC). No known unofficial-port concerns.
- Legitimacy: owned copy confirmed.

## 2. Engine lineage
- Family / base engine and how it was modified: **Unreal Engine 3, confirmed** — standard UE3 `Binaries\Win32\` + `Core\` folder layout, `Direct3DCreate9` present. Developer "Spicy Horse Games" confirmed via an internal string (`unlimited.ky.SpicyHorse.Alice2...`, likely a Steam stat/achievement key). Modification depth not yet investigated.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.): **NVIDIA PhysX + APEX** confirmed (`PhysXCore.dll`, `PhysXExtensions.dll`, `PhysXCooking.dll`, `PhysXDevice.dll`, `NxCharacter.dll`, `APEX_Clothing_x86.dll`, `APEX_Clothing_Legacy_x86.dll`, `APEX_Destructible_x86.dll`, `APEX_Destructible_Legacy_x86.dll`, `ApexFramework_x86.dll`) — cloth and destructible-mesh physics specifically called out, matching UE3's well-known standard PhysX/APEX integration of this era. **CUDA present** (`cudart.dll`, `cudart32_30_9.dll`) — likely GPU-accelerated PhysX. **Bink** for video (`binkw32.dll`, same middleware as Mad Max and Prince of Persia). **Ogg Vorbis** (`ogg.dll`, `vorbis.dll`, `vorbisenc.dll`, `vorbisfile.dll`) plus XAudio2-family (`X3DAudio1_7.dll`, `XAPOFX1_4.dll`) for audio — UE3's standard audio stack. Compiled with **VS2008** (`MSVCR90.dll`).
- Distinctive file formats / build tags / symbol naming: not yet investigated (UE3's standard `.upk`/`.u` package formats are a reasonable expectation but unconfirmed for this specific title).

## 3. Binary & memory
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): **32-bit** (PE32, `coff-i386`). Standard-ish section layout (`.text`/`.textidx`/`CONST`/`.rdata`/`.data`/`.rsrc`/`.reloc`/`.bind`) — `.textidx` is a known, benign UE3-toolchain section, not a red flag (no giant opaque blob, no Denuvo/anti-tamper-shaped structure). 17.4 MB.
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: **Direct3D 9 confirmed** — `d3d9.dll` statically imported, literal string `Direct3DCreate9` present.
- Developer console / cvar system present? how opened?: **Not yet confirmed via strings search, but UE3 ships a well-documented, near-universal built-in console** (public/general UE3 knowledge, not specific to this title) — conventionally opened with the tilde (`~`) key by default. Worth trying directly live rather than assuming a from-scratch discovery is needed.

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **No DRM found — same clean picture as Prince of Persia (2008).** Zero hits for Denuvo, SecuROM, StarForce, or any EA Origin/link2ea-style launcher-handoff string (the only "Origin" string hits are unrelated UV/texture-coordinate terminology — `uvOrigin.x`, `originalRect` — not EA's launcher). Worth being glad about specifically given this is EA-published (same publisher as Burnout Paradise, which needed the EA App) — this title evidently doesn't carry that requirement. Not yet tested live.
- Attach workflow that works: not yet tested live, but no static evidence predicts a block.
- Injection vector that works (proxy DLL name / injector / framework): not yet tested live. **Plan: a from-scratch `d3d9.dll` proxy**, matching this portfolio's Psychonauts and Prince of Persia precedent (D3D9 titles proxied directly). Given no DRM found, low risk expected.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)
- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**:
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention:
- Where projection `P` / FOV comes from:
- The per-eye override maths (`K_eye = …`):

## 7. Constant-buffer fill mechanism
- Map/DISCARD ring / UpdateSubresource / D3D11.1 offset / **persistent map +
  memcpy** (trap):
- Can source contents be read cheaply (captured CPU pointer) or need staging
  read-back?:
- The chosen override patch point and why:

## 8. Pass inventory (by render target)
- Main scene (res/formats):
- Shadow passes (depth-only sizes):
- Post / AA chain (SMAA/TAA/motion vectors; downscale sizes):
- UI / HUD (how it's kept separate):

## 9. cvar / console cheat sheet
| command / cvar | effect | use |
|---|---|---|
| | | |

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used):
- In-process input / camera drive method that worked:
- Frame-capture method; where images land:

## 11. Dead ends & false leads (save future time)
- <what looked true but wasn't, and why>

## 12. Open risks toward the North Star
- <what could still block VR + head tracking>
