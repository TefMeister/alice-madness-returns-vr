# Engine Dossier — Alice: Madness Returns (Unreal Engine 3)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 done — static recon complete, external research folded in. No DRM found (reconciled: EA Cuckoo DRM was present historically, removed via a Jan 2022 patch — a dated, documented history, not a lucky negative result). **This is the strongest VR-feasibility case in the whole portfolio: vorpX already delivers true Geometry 3D + working motion-controller emulation for this exact game**, plus a mature open-source community patch (MadnessPatch) that already exposes the console, disables VR-harmful mouse smoothing, and confirms a real framerate-dependent-physics risk. · **VR-readiness verdict:** genuinely the most promising front so far — no environmental blockers, no DRM, the best third-party feasibility signal of any project here, AND a real chance the developers' own shipped code already solves the hard per-eye camera problem (see §6). Proxy `d3d9.dll` is built, **deployed, and live-verified** (2026-08-25) — see §4.

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
- Injection vector that works (proxy DLL name / injector / framework): **✅ LIVE-VERIFIED (2026-08-25), a from-scratch `d3d9.dll` proxy**, matching this portfolio's Psychonauts and Prince of Persia precedent. **First deploy attempt failed the game outright** — see `staging/alice-madness-returns-vr/proxy-d3d9/README.md` for the full story: `AliceMadnessReturns.exe` statically imports *two* functions from `d3d9.dll` (`Direct3DCreate9` and `D3DPERF_SetOptions`, a real D3D9 perf-marker export), not just one — a proxy exporting only `Direct3DCreate9` left Windows' loader unable to resolve the exe's import table at all, so the process exited before running any code (zero log output, "ran ~2 seconds then stopped"). Isolated via a clean control test (DLL removed → game launched fine), fixed by adding the second forwarding wrapper, redeployed — **confirmed working cleanly on the retest**: `Direct3DCreate9` called twice (SDKVersion=0x20 both times), `D3DPERF_SetOptions` called once (dwOptions=0x1), game ran for ~5 minutes of real play. **Lesson for future D3D9 proxies in this portfolio: check the exe's actual per-function import list for the target DLL, not just whether the DLL name appears in the import table** — Prince of Persia's exe only needed `Direct3DCreate9`, but that isn't guaranteed for every D3D9 title.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)

### ✅ SETTLED STATICALLY, 2026-09-01 — the registers are read out of the game's own shipped shaders

*Discovered by the `/pd` pass at 14:29 (`modding-notes/2026-09-01b-…`), which recorded it in the notes
and on the status board but not here; folded into the dossier, with the vertex/pixel split added, by
the later `/pd` pass (`modding-notes/2026-09-01c-…`).*

**The game was never launched.** This came from `AliceGame\CookedPC\RefShaderCache-PC-D3D-SM3.upk`,
a file that ships with the game, read with `flat-to-vr-RE-toolkit/tools/d3d9-ctab.py`. Compiled D3D9
shaders carry a `CTAB` block naming every constant and its register, so this is plain data on disk —
no capture, no debugger. The cache holds **45,832 constant tables (43,025 `ps_3_0`, 2,807 `vs_3_0`)**.

| Constant | Target | Register | Shaders | Distinct layouts | Exceptions |
|---|---|---|---|---|---|
| `ViewProjectionMatrix` | `vs_3_0` | **`c0`, 4 regs (4×4)** | 2,431 | 576 | **none** |
| `CameraPosition` | `vs_3_0` | **`c4`** | 1,989 | 473 | **none** |
| `PreViewTranslation` | `vs_3_0` | **`c5`** | 486 | 195 | **none** |
| `NvStereoEnabled` | `ps_3_0` | `c3` | 28,017 | 11,004 | none |
| `ViewProjectionMatrix` | `ps_3_0` | `c4` (and `c11` ×4) | 4,126 | 1,723 | — |

`[inferred-static 2026-09-01]` — every vertex shader in the shipped cache that references the
view-projection puts it at `c0`, across 576 independent layouts, with no counter-example. 2,431 of
the 2,807 vertex shaders (87%) carry it.

**⭐ The useful split: VIEW constants are fixed, PER-OBJECT constants are not.** The three registers
above never move. The per-object matrices move with the vertex factory, and a hook must not assume
them:

| Constant | Registers seen (`vs_3_0`) |
|---|---|
| `LocalToWorld` | `c6` (1,761 shaders), `c231` (468 — the skinned/GPU-skin factory), `c10` (228) |
| `LocalToView` | `c10` (154), `c14` (114) |
| `InstancedPreViewTranslation` | `c6` (46), `c10` (28) — a **separate constant** from `PreViewTranslation`, used by the instanced factory |

`[inferred-static 2026-09-01]` This is why a per-eye override belongs at `c0`: it is the one place the
camera arrives at a fixed address regardless of which factory drew the object. It also explains the
early Enslaved histogram that started the per-object-WVP scare — `c6`/`c10`/`c231` genuinely do change
per draw; they are just not where the camera lives.

**⚠️ Vertex and pixel registers are different spaces — do not merge them.** The same name sits at
`c0` in a vertex shader and `c4` in a pixel shader. Reading the two together is what makes `c0` look
like a minority case; split by target and the vertex side is unanimous.

**And the pixel-shader copies are not a footnote: they outnumber the vertex ones (4,126 vs 2,431).**
A per-eye offset written only at vertex `c0` would leave every one of those pixel shaders reading an
un-offset view-projection — the shape of bug that yields correct geometry with wrong screen-space
effects (reflections, fog, SSAO, decals). Plan for both from the start. (Related display trap: the
CTAB tool prints *sampler* registers with a `c` prefix too, so `NvStereoFixTexture sampler c1` is
`s1` and does **not** collide with `ScreenPositionScaleBias` at float4 `c1`.)

### ⛔️ This supersedes the "c0 is probably NOT a shared view-projection" warning below

That warning was inherited from `enslaved-vr`, whose early gameplay histogram showed only per-draw
4×4 uploads and no frame-constant register. **It was withdrawn at the source on 2026-09-01**
(`enslaved-vr/modding-notes/2026-09-01-shared-viewprojection-confirmed-at-c0.md` — Enslaved's own
shipped `.usf` sources put the shared view-projection at `c0`). Alice now agrees from a completely
different kind of evidence: Enslaved from shader *source*, Alice from compiled shader *reflection*.
**Both UE3/D3D9 games independently land on `c0` = ViewProjection, `c4` = CameraPosition,
`c5` = PreViewTranslation.** Treat the paragraph below as history, not as guidance.

**What this does NOT establish:** that writing `c0` steers the picture. The register is where the
matrix *arrives*; nothing here proves the engine does not also fold a camera term into per-object
matrices for some passes, and the `ps_3_0` copies at `c4` mean at least some screen-space work
re-reads it. The diagnostic that would show the *derivation* is wrong rather than a value needing
tuning: override `c0` with a deliberate large yaw and check whether **all** opaque geometry rotates
together. If some passes rotate and others do not, the shared-VP model is incomplete for this game.

### 🪤 The `c5` trap: a per-eye offset that ignores `PreViewTranslation` drifts

From `/sr`'s inbox drop, 2026-09-01. `PreViewTranslation` at `c5` means vertices arrive in
**translated world space** — UE3's precision trick for large levels. **A per-eye offset that ignores
`c5` looks correct near the world origin and drifts as you move away from it.** `[reported]`

That failure mode is nastier than a wrong-looking picture: it **passes its first test** and fails
later, far from where it was written. Given Alice's level sizes this is a real risk, not a footnote.
Any stereo maths written here must account for `c5` from the start.

**The clean injection point,** same source: `SetVertexShaderConstantF` filtered on
`StartRegister == 0 && Vector4fCount == 4` is where the view-projection arrives — one intercept, per
eye. The camera position comes free at `c4` rather than being solved out of a matrix. `LocalToWorld`
and friends are compiler-allocated per vertex factory (see the table above) and are not in the way.

**Also worth keeping — why the old warning was wrong.** The pessimistic reading came from a live
capture showing `c0` receiving **47 uploads per frame**, which looked like per-draw traffic. UE3's
D3D9 RHI **re-applies the reserved view registers around bound-shader-state changes**, so those were
47 writes of *the same value*. The count was real; the inference from it was not — "counting events
is not measuring content", now written up as a named failure mode in the cross-engine library.
**And the dossier's own suggested test (flag any register whose 4×4 value is identical across every
draw) would have got it right.**

**Status of the verification `/sr` asked for:** the drop was `[inferred-static, n=1]` from *Enslaved's*
shader sources and asked that it be confirmed on Alice before being built on. **That is now done** —
the CTAB reflection above is Alice's own shipped data, and it agrees on all three registers.

### ⭐ The native stereo path is real, and it is compiled into the shipping shaders

`NvStereoEnabled` is present in **28,017 pixel shaders (65% of all of them), always at `ps_3_0` `c3`**,
with `NvStereoFixTexture` as a companion sampler. `[inferred-static 2026-09-01]` This is much harder
evidence than the config key `AllowNvidiaStereo3d=True` or the HelixMod author's remark: the stereo
path is not a menu option bolted on, it is **branch logic baked into the majority of the game's
shipped pixel shaders**. It corroborates the "this game ships real stereo-3D support" lead below and
promotes it from a strong lead to a static fact about the shaders.

**Careful about what it buys us:** this is *NVIDIA 3D Vision* support — a driver-era stereo path.
Its presence proves per-eye rendering was designed for, and `c3` is a live switch worth probing, but
it is not an OpenXR submission path and it does not by itself give us head tracking.

#### ✅ `NvStereoFixTexture`'s layout is documented — no disassembly needed (`/gr`, 2026-09-01)

It is NVIDIA's **`StereoParmsTexture`** from the freely published `nvstereo.h` that shipped with 3D
Vision. Channels, in NVIDIA's own wording `[reported]`:

| channel | contents |
|---|---|
| `.r` | eye-specific **separation** |
| `.g` | **convergence** |
| `.b` | **unit vector identifying the current eye — left = −1, right = +1** |

The texture is **app-provided** (the game creates it) and updated once per frame. Dimensions and
format come from `StereoTexWidth`/`StereoTexHeight`/`StereoTexFormat`, whose values the doc names but
does not print — **so the size/format still has to be read off the game's own `CreateTexture` call.**
That is a much smaller open question than the one it replaces.

**Why this matters more than it looks:** a proxy can bind **its own** stereo texture, and all 14,479
sampling shaders then read *our* separation, *our* convergence and *our* eye sign — unmodified, with
no NVIDIA driver involved. The `.b` channel is the mechanism by which one shader behaves differently
per eye. With the view-projection at `c0`, the whole shape is specified without a launch: render
twice; per eye write that eye's view-projection to `c0`; per eye bind a stereo texture carrying that
eye's sign; ship all 28,017 shaders exactly as they are. **That is NVIDIA's division of labour with us
in the driver's role.**

**⚠️ Two caveats, both unresolved:**
1. **Which 3D Vision mode UE3 actually uses is genuinely ambiguous.** Epic's page is titled *"UE3 and
   NVIDIA 3D Vision **Direct**"* (Direct = the application renders both eyes, the optimistic reading),
   but an **eye-sign channel in a texture is the signature of the Automatic pattern** — an app
   rendering in Direct mode already knows which eye it is drawing. Evidence points both ways;
   `[reported]` / `[hypothesis]`. The plan above is unaffected either way, which is why it is still
   worth acting on.
2. **UE3 stereo is reported fullscreen-only** `[reported]` — a windowed live test could show nothing
   and be misread as the approach failing.

- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**:
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention: (D3D9 note: shader constant registers, not D3D11-style
  cbuffers — same caveat as Prince of Persia.)
- Where projection `P` / FOV comes from: **`FOV <10-150>` is a real, native, config-bindable console command (external-research, 2026-08-25)** — confirmed via two independent Nexus Mods ultrawide/FOV-fix mods, both of which work by binding a key in `BaseInput.ini` (`[Engine.PlayerInput]`) to issue this command. This is UE3's well-known generic built-in FOV command, not specific to this game. Low-risk way to probe camera/FOV behavior early, before any hooking work — bind a test key via `BaseInput.ini` and observe directly.
- The per-eye override maths (`K_eye = …`):
- **Potentially the single most important finding in this project so far (external-research, 2026-08-25): this game may ship its own native, already-working stereoscopic-3D camera system.** The HelixMod fix for this game (by "Chiz," the same author credited for Prince of Persia 2008's fix) describes its own job in a very specific way: *"Even though it comes with Stereoscopic support it wasn't 100% but Your fixes made 100%."* That means Alice: Madness Returns **ships a real, built-in stereo-3D mode** (very plausibly targeting official "NVIDIA 3D Vision Ready" certification, common for UE3 titles of this era) — and the third-party fix's job was narrow: it *"push[es] 2D UI to 3D depths"* only, a **shader-level UI-layer intervention, not a camera or world-projection change.** If the native mode's core per-eye camera/projection handling was already correct enough that a third party only needed to fix flat UI, **this game's own shipped code may already contain a working per-eye projection override mechanism** — exactly what this section exists to reverse-engineer. **Concrete next step, before any from-scratch shader-reflection work:** check for a native in-game "Stereo 3D" setting (options menu or a config/`.ini` value) and whether it's still functional on the current build — if reachable and toggleable live, watching what changes in the constant-register/matrix data between mono and native-stereo rendering would be far more direct than reverse-engineering the mono path alone. Not yet confirmed to exist/work on the current build — a strong lead, not a confirmed shortcut.
- **UE3's camera architecture is publicly documented (external-research, 2026-08-25) — a real advantage no other project in this portfolio has** (every other front runs a fully proprietary, undocumented engine). Two levels, from Epic's own UDK docs and the community BeyondUnreal wiki:
  - **Gameplay/UnrealScript layer:** `PlayerController` owns the camera (`PlayerCamera`, `CameraClass`, `ViewTarget` properties); FOV lives on the controller too (`FOVAngle`, `DefaultFOV`). **`UpdateViewTarget` is the documented per-frame function to look for/override** — it updates the view target's position/rotation/FOV each frame, and is the natural starting point for where this game's camera decision gets made before it ever reaches the renderer. `GetPlayerViewPoint` returns the actual point-of-view handed to rendering.
  - **Shader/renderer layer:** UE3's view-projection matrix is documented as living in **vertex shader constant register `c0`** (community-referred to as `VSR_ViewProjMatrix`) — directly answering this section's "exact constant-buffer slot" question via public documentation (D3D9 has no cbuffers, so this is a shader constant register, consistent with this dossier's existing D3D9 caveat). **`PreViewTranslation`** is UE3's documented technique of splitting the view matrix into a separately-tracked camera-relative translation component and a rotation matrix (`ViewMatrix = PreViewTranslation × ViewRotationMatrix`), to preserve floating-point precision in large worlds — a well-known UE-family pattern that persisted into UE4/5.
  - **This is public, generic UE3 knowledge, not yet verified against this specific game's binary** — treat as a real, testable starting hypothesis for live shader-reflection work (check `c0` first; look for a `PreViewTranslation`-style split), not a substitute for confirming it live.
- **⛔️ SUPERSEDED 2026-09-01 — DO NOT ACT ON THIS PARAGRAPH; see §6's static findings above. Kept only so the reasoning stays visible.** ~~Important correction from this portfolio's own sibling project (external-research, 2026-08-25): `c0` is probably NOT a simple shared view-projection register.~~ `[disproved 2026-09-01]` `enslaved-vr` (Enslaved: Odyssey to the West, this portfolio's own project, same engine generation and renderer — UE3 on D3D9) has a real, live-captured constant-register histogram from an actual gameplay frame: every 4×4 matrix upload was **per-object/per-draw** (at `c0`, `c6`, `c10`, and `c231`/`c235` for a skinned-character vertex factory) — **no register held a value shared across every draw in the frame.** Working conclusion there: the camera is very likely folded into a per-draw World×ViewProjection matrix, not delivered as one separately-uploaded shared VP register. **Don't assume `c0` holds a clean, isolated view-projection matrix for Alice just because generic UE3 docs describe it that way** — build (or adapt) the same "flag any register whose 4×4 value is identical across every draw in the frame" detection technique first; if nothing gets flagged, expect the harder per-object-WVP decomposition case instead.
- **A directly reusable D3D9 proxy blueprint exists in this portfolio already (`enslaved-vr`, external-research 2026-08-25)**: a fail-safe `d3d9.dll` proxy forwarding all real exports, intercepting `Direct3DCreate9`, then patching `IDirect3D9::CreateDevice` (**vtable slot 16**), and on the returned device patching `Present` (**17**), `Reset` (**16**), and `SetVertexShaderConstantF` (**94**) — logging `CreateDevice` params, a per-frame register-upload histogram, and an optional watched-register 4×4 dump. This is essentially the natural next build for this section — Enslaved's own vtable slots/hook points are simply facts about D3D9's interface layout that apply identically here (own logic to be written fresh, not copied). **Two-altitude framing for owning the camera (same source):** (1) RHI level — intercept `SetVertexShaderConstantF`/`SetTransform` in the proxy and re-derive/replace the view-projection per eye; (2) engine level — patch the UnrealScript/native camera path (`APlayerCamera::UpdateCamera` or a game-specific override) before the renderer ever consumes it. Worth deciding between these explicitly once live work starts.
- **UE3's stock default console key is Tilde (`~`), not F2** (external-research, 2026-08-25, confirmed via Enslaved's own shipping `BaseInput.ini`/`MonkeyInput.ini` — `ConsoleKey=Tilde`). Directly relevant to this dossier's own open §3/§9 question: if F2 turns out to be MadnessPatch-specific rather than stock, try Tilde on the unpatched game first.
- **Config methodology note (same source): UE3's authoritative runtime config often lives under `Documents\My Games\UnrealEngine3\<ProjectName>\Config\`, not the in-install-directory INI files** (which are just defaults) — check for an `AliceGame`-equivalent per-user config path before assuming edits to game-directory `.ini` files take effect. Also worth checking Alice's engine INI for a non-default `GameViewportClientClassName` (Enslaved has `NTEngine.NTReplayGameViewportClient`) — a cheap, config-only way to discover whether Spicy Horse layered custom camera/viewport logic on stock UE3, directly relevant given the native-stereo3D finding above already suggests real custom camera work happened here.
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
| Tilde `~` | UE3's stock default console key | per enslaved-vr's own shipping config — try if F2 turns out patch-only |
| `Show <group>`, `ToggleDebugCamera`, `Stat FPS`, `Stat D3D9RHI`, `ViewMode <mode>`, `SloMo` | standard UE3 exec commands | per enslaved-vr's own testing; `ToggleDebugCamera` especially worth trying for §6/§10 (free/debug camera) |

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used):
- In-process input / camera drive method that worked:
- Frame-capture method; where images land:

## 11. Dead ends & false leads (save future time)
- <what looked true but wasn't, and why>

## 12. Open risks toward the North Star
- **Framerate-dependent physics is a real, third-party-confirmed risk (external-research, 2026-08-25, from MadnessPatch's own fix list): hair/dress physics instability, projectile hitbox inconsistency, and general simulation behavior specifically at high framerates.** VR needs a high, stable frame rate (typically 90Hz+); this UE3-era game's physics were evidently tuned assuming a much lower framerate ceiling, and MadnessPatch had to fix exactly this class of bug. Running at VR framerates may re-expose the same issues — test explicitly once running at VR-target framerates, and treat MadnessPatch's own fix approach (understand, don't copy) as a reference point.
- **The strongest VR-feasibility signal of any project in this portfolio (external-research, 2026-08-25): vorpX delivers true Geometry 3D stereo AND working motion-controller emulation ("emulates a gamepad perfectly") for this exact game**, in both Immersive and Cinema modes. For comparison: Burnout Paradise's vorpX fails outright; Mad Max's vorpX works but third-person-only with no motion-controller mention; Prince of Persia has no vorpX profile at all. A third party has already solved, for this exact game, both the per-eye camera/projection override (§6's core problem) and mapping VR motion-controller input onto the game's own controls convincingly — neither reusable (closed-source), but both are strong existence proofs this engine doesn't resist full stereo + motion-input VR conversion. Treat vorpX's own default separation/convergence settings as a rough sanity-check reference once this project's own live camera work begins — not to copy, but to cross-check comfort. **Why vorpX does so well here specifically (this portfolio's own cross-engine library, external-research 2026-08-25): vorpX's Geometry 3D mode "works best on D3D9 games specifically"** — D3D9's older, simpler rendering model is exactly its best-case scenario (it works by rendering the scene twice, once per eye, at a real ~50% framerate cost). **A documented backup path exists if the from-scratch engine-level approach hits a wall**: `D3D9 game → dgVoodoo2 (wraps D3D9 onto D3D11) → geo-11 (free, D3D11-only stereo driver)`, optionally paired with a 3Dmigoto-class shader fix. Alice is unusually well-positioned for this specific backup, since it already has exactly the per-game shader-fix piece that route wants (the HelixMod fix, §6). **Scope reminder: both vorpX and geo-11 top out at seated/head-look experiences — no true 6DoF, no spatial motion-controller tracking** (vorpX's "motion controllers emulate a gamepad perfectly" is input-mapping, not hand presence) — this project's actual goal (full engine-level VR with real 6DoF) is a different category than either fallback, consistent with, not a substitute for, the primary plan.
