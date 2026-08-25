# Engine Dossier — Alice: Madness Returns (Unreal Engine 3)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 done — static recon complete, external research folded in. No DRM found (reconciled: EA Cuckoo DRM was present historically, removed via a Jan 2022 patch — a dated, documented history, not a lucky negative result). **This is the strongest VR-feasibility case in the whole portfolio: vorpX already delivers true Geometry 3D + working motion-controller emulation for this exact game**, plus a mature open-source community patch (MadnessPatch) that already exposes the console, disables VR-harmful mouse smoothing, and confirms a real framerate-dependent-physics risk. · **VR-readiness verdict:** genuinely the most promising front so far — no environmental blockers, no DRM, and the best third-party feasibility signal of any project here. A from-scratch `d3d9.dll` proxy is built and **deployed** (`alice-madness-returns-vr-staging/proxy-d3d9/`), not yet tested against a live launch.

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
- Developer console / cvar system present? how opened?: **Confirmed reachable (external-research, 2026-08-25): "Developer console access (F2)" is documented as an explicit feature by the MadnessPatch community patch.** Unconfirmed whether F2 works out-of-the-box on the stock game or only after the patch (worth testing both live) — many UE3 titles bind console to a key by default, so the patch may be restoring/fixing an existing binding rather than adding one from scratch.

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **No DRM found — reconciled with a real, dated history (external-research, 2026-08-25), not just a lucky static result.** The original 2011 release used **"EA Cuckoo"**, an online-authentication DRM tied to EA's own activation servers. EA delisted the game entirely in September 2016 after accidentally distributing already-used Steam keys (refunding affected buyers rather than replacing keys), leaving existing owners with server-dependent DRM on a no-longer-sold title. The game was later **relisted on Steam, and a January 14, 2022 patch removed EA Cuckoo authentication DRM entirely** from that build. Our own static recon (zero Denuvo/SecuROM/StarForce/Cuckoo/link2ea strings) is fully consistent with this — **this is a "DRM was present historically, current build is clean" case, same pattern as Prince of Persia (2008), not a lucky negative result.** Worth being glad about specifically given this is EA-published (same publisher as Burnout Paradise, which still needs the EA App) — this title evidently doesn't carry that requirement anymore. Not yet tested live.
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
  handedness, row/column convention: (D3D9 note: shader constant registers, not D3D11-style
  cbuffers — same caveat as Prince of Persia.)
- Where projection `P` / FOV comes from: **`FOV <10-150>` is a real, native, config-bindable console command (external-research, 2026-08-25)** — confirmed via two independent Nexus Mods ultrawide/FOV-fix mods, both of which work by binding a key in `BaseInput.ini` (`[Engine.PlayerInput]`) to issue this command. This is UE3's well-known generic built-in FOV command, not specific to this game. Low-risk way to probe camera/FOV behavior early, before any hooking work — bind a test key via `BaseInput.ini` and observe directly.
- The per-eye override maths (`K_eye = …`):
- **Camera smoothing is a known, already-solved problem (external-research, 2026-08-25, from MadnessPatch): the base game applies heavy mouse smoothing/negative acceleration and input deadzones** — exactly the kind of input-to-camera latency that reads as unacceptable lag in a headset with real head tracking. MadnessPatch neutralizes this via a simple `DisableMouseSmoothing = 1` config toggle — strong evidence the camera-update code path is a tractable, identifiable target. **This should be treated as a required setting for any VR head-tracking work here, not an optional nicety.**

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
| `FOV <10-150>` | native UE3 field-of-view command | confirmed via two independent Nexus FOV/ultrawide mods, both `BaseInput.ini`-bound |
| `DisableMouseSmoothing = 1` (config, `BaseInput.ini`-style) | removes mouse smoothing/negative acceleration and deadzones | per MadnessPatch — VR-critical, removes input-to-camera latency |
| F2 (unconfirmed if stock or patch-only) | opens the developer console | per MadnessPatch's documented feature list; test both with/without the patch |

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used):
- In-process input / camera drive method that worked:
- Frame-capture method; where images land:

## 11. Dead ends & false leads (save future time)
- <what looked true but wasn't, and why>

## 12. Open risks toward the North Star
- **Framerate-dependent physics is a real, third-party-confirmed risk (external-research, 2026-08-25, from MadnessPatch's own fix list): hair/dress physics instability, projectile hitbox inconsistency, and general simulation behavior specifically at high framerates.** VR needs a high, stable frame rate (typically 90Hz+); this UE3-era game's physics were evidently tuned assuming a much lower framerate ceiling, and MadnessPatch had to fix exactly this class of bug. Running at VR framerates may re-expose the same issues — test explicitly once running at VR-target framerates, and treat MadnessPatch's own fix approach (understand, don't copy) as a reference point.
- **The strongest VR-feasibility signal of any project in this portfolio (external-research, 2026-08-25): vorpX delivers true Geometry 3D stereo AND working motion-controller emulation ("emulates a gamepad perfectly") for this exact game**, in both Immersive and Cinema modes. For comparison: Burnout Paradise's vorpX fails outright; Mad Max's vorpX works but third-person-only with no motion-controller mention; Prince of Persia has no vorpX profile at all. A third party has already solved, for this exact game, both the per-eye camera/projection override (§6's core problem) and mapping VR motion-controller input onto the game's own controls convincingly — neither reusable (closed-source), but both are strong existence proofs this engine doesn't resist full stereo + motion-input VR conversion. Treat vorpX's own default separation/convergence settings as a rough sanity-check reference once this project's own live camera work begins — not to copy, but to cross-check comfort.
