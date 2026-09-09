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
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): **32-bit** (PE32, `coff-i386`). Standard-ish section layout (`.text`/`.textidx`/`CONST`/`.rdata`/`.data`/`.rsrc`/`.reloc`/`.bind`) — `.textidx` is a known, benign UE3-toolchain section, not a red flag (no giant opaque blob, no Denuvo/anti-tamper-shaped structure). **`.bind` is NOT a UE3 artefact: it is the SteamStub v3.x DRM stub section, and it holds the entry point** (§4, §6). 17.4 MB.
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: **Direct3D 9 confirmed** — `d3d9.dll` statically imported, literal string `Direct3DCreate9` present.
- Developer console / cvar system present? how opened?: **Confirmed reachable (external-research, 2026-08-25): "Developer console access (F2)" is documented as an explicit feature by the MadnessPatch community patch.** ✅ **Settled 2026-09-03 (`/gr`): F2 is PATCH-ONLY.** MadnessPatch 3.0.0+ adds `EnableConsole` "bound to F2" as its own feature `[reported, release notes]`. **On the stock game try Tilde (`~`)**, UE3's shipping default. So the old "worth testing both live" is resolved without a launch.

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **⚠️ READ NARROWLY — "no DRM" means EA's Cuckoo is gone; the shipping binary IS wrapped in Valve's own SteamStub.** Corrected 2026-09-03: `.bind` holds the entry point and `.text` is encrypted at rest, and the **SteamStub v3.x header magic `0xC0DEC0DF` is verified inside the stub's own validating `cmp`** (§6). That is a **packaging wrapper, not an anti-tamper system** like Denuvo — it does not fight a debugger, and a public open-source unpacker (Steamless) restores `.text` for static analysis without running the game. Injection is unaffected: the `d3d9.dll` proxy is live-verified on this build. `[inferred-static 2026-09-03]` The Cuckoo history below remains accurate and is unchanged. **No DRM found — reconciled with a real, dated history (external-research, 2026-08-25), not just a lucky static result.** The original 2011 release used **"EA Cuckoo"**, an online-authentication DRM tied to EA's own activation servers. EA delisted the game entirely in September 2016 after accidentally distributing already-used Steam keys (refunding affected buyers rather than replacing keys), leaving existing owners with server-dependent DRM on a no-longer-sold title. The game was later **relisted on Steam, and a January 14, 2022 patch removed EA Cuckoo authentication DRM entirely** from that build. Our own static recon (zero Denuvo/SecuROM/StarForce/Cuckoo/link2ea strings) is fully consistent with this — **this is a "DRM was present historically, current build is clean" case, same pattern as Prince of Persia (2008), not a lucky negative result.** Worth being glad about specifically given this is EA-published (same publisher as Burnout Paradise, which still needs the EA App) — this title evidently doesn't carry that requirement anymore. Not yet tested live.
- Attach workflow that works: not yet tested live, but no static evidence predicts a block.
- Injection vector that works (proxy DLL name / injector / framework): **✅ LIVE-VERIFIED (2026-08-25), a from-scratch `d3d9.dll` proxy**, matching this portfolio's Psychonauts and Prince of Persia precedent. **First deploy attempt failed the game outright** — see `staging/alice-madness-returns-vr/proxy-d3d9/README.md` for the full story: `AliceMadnessReturns.exe` statically imports *two* functions from `d3d9.dll` (`Direct3DCreate9` and `D3DPERF_SetOptions`, a real D3D9 perf-marker export), not just one — a proxy exporting only `Direct3DCreate9` left Windows' loader unable to resolve the exe's import table at all, so the process exited before running any code (zero log output, "ran ~2 seconds then stopped"). Isolated via a clean control test (DLL removed → game launched fine), fixed by adding the second forwarding wrapper, redeployed — **confirmed working cleanly on the retest**: `Direct3DCreate9` called twice (SDKVersion=0x20 both times), `D3DPERF_SetOptions` called once (dwOptions=0x1), game ran for ~5 minutes of real play. **Lesson for future D3D9 proxies in this portfolio: check the exe's actual per-function import list for the target DLL, not just whether the DLL name appears in the import table** — Prince of Persia's exe only needed `Direct3DCreate9`, but that isn't guaranteed for every D3D9 title.
- **⚠️ PROXY ROBUSTNESS — the proxy never frees the real `d3d9.dll`, so a reload walks past it** `[inferred-static 2026-09-04, /sr inbox, read directly]`. `proxy-d3d9/src/proxy.c:97` does `LoadLibraryA(sysdir)` and there is **no `FreeLibrary` anywhere**. If the game ever `FreeLibrary`s our proxy (a startup capability probe, a renderer restart, an options change), the system `d3d9.dll` stays resident under that base name and the game's next `LoadLibrary("d3d9.dll")` matches it by name — **the app directory is never searched, our proxy never reloads, and the game runs perfectly without the mod.** This is the same defect ReShade fixed for Alan Wake (commit `74347b91d`, 4.5.2). **Latent, not yet observed live on Alice.** ⚠️ **It is the interpretation key for the launch's "outcome 1":** the signature is a load + one or two export calls + an unload within ~100 ms in `alice_vr_proxy_log.txt`, then silence *while the game reaches gameplay* — that is "reloaded past", NOT "the wrapper crashed the game". **Fix (one line): `FreeLibrary(real_d3d9)` in `DLL_PROCESS_DETACH`**; ready to apply and redeploy if that signature appears. Cross-engine write-up: `flat-to-vr-cross-engine-research` techniques README. **✅ Did NOT bite on the 2026-09-04 launch** `[verified-live 2026-09-04]`: the proxy stayed resident the whole session including the settings screens (which can Reset the device), so the bug remains latent on Alice — fix it before it can, not because it has.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)

### ⭐⭐ SETTLED 2026-09-09b (`/lm`, live) — THE MYSTERY `c0` WRITE WAS NEVER A MATRIX, AND THE SHEAR WAS CORRUPTING IT

Write-up: `modding-notes/2026-09-09b-the-mystery-write-was-never-a-matrix-and-added-key-binds-are-ignored.md` §1.

The once-per-frame non-camera write at `c0` arrives with **`Vector4fCount = 8`**, so it is not a
4×4 matrix at all. Its values are exact whole-texel offsets for the running 1280×720 backbuffer —
`0.00078125 = 1/1280`, `0.0015625 = 2/1280`, `0.00138889 = 1/720`, `0.00277778 = 2/720` — i.e. a
filter/blur pass uploading **`SampleOffsets` as an eight-register array**, precisely what the
shipped `GlobalShaderCache` said was the only non-view constant bound at vertex `c0`.
`[verified-numerically 2026-09-09, n=1 launch, 24,484 c0 writes]`

**The census is total, with no residue:** `4=23372 8+=1112` against
`camera=23352 affine=20 skewed=1112`. Two independent counters, and every skewed write is an
8-register one. There is no leftover mystery matrix. `[verified-numerically 2026-09-09]`

**⭐ THE DEFECT THIS EXPOSED, now fixed.** The interception test was `start == 0 && count >= 4`,
which a four-register ViewProjection satisfies **and so does the eight-register blur array**. So
whenever stereo was on, the shear rewrote registers 0..3 of a blur pass's sample offsets every
frame. It had never been seen because it only fires with stereo enabled, and a wrongly-filtered blur
reads as ordinary stereo weirdness. The fix is `count == 4` — a ViewProjectionMatrix is exactly four
registers — with the classification and census still seeing every write, because that census is what
found this.

**Verified both ways:** the shear can no longer reach a non-4 write `[compile-verified 2026-09-09]`,
and the camera shear is unchanged — stereo off → on measured **−5 px before the fix and −6 px
after**, on the same scene, the 1 px being framing noise between two launches
`[measured 2026-09-09, n=1 scene each]`.

⚠️ **NOT established: whether the corruption was ever VISIBLE.** The defect is proven by
construction, not by a before/after artefact — Whitechapel at rest does not obviously run a blur
pass. Do not describe it as "a bug we could see".

### ⭐ WHAT FIRST PERSON SURVIVES (2026-09-09b, live)

`p00cam` is a free first/third-person detector — **≈1.5697 in first person, ≈1.4281 in third** — so
the state can be read from the log without a screenshot.

| action | result |
| --- | --- |
| jump, and run-then-jump | **stays in first person** `[verified-live 2026-09-09, n=1 each]` |
| walking (12 taps) | stays in first person `[verified-live 2026-09-09, n=1]` |
| weapon switch (`One`) | **exits to third person** `[verified-live 2026-09-09, n=1]` |

The weapon-switch exit had been `[inferred-static]` from `QuitFPS` in that key's command list; it is
now live. That raises confidence in the rest of that list without proving it.

⚠️ **Combat is untested** (Chapter 1's opening has no enemies) and **eye height is unmeasured** —
and harder than it looked, because it wanted `BugIt`, which §9 now shows cannot be reached by
rebinding.


### ⛔️ CORRECTED 2026-09-09c (live) — THE BUILT-IN FIRST PERSON IS GATED BY THE **LEVEL**, AND IS NOT THE VR ROUTE

Write-up: `modding-notes/2026-09-09c-the-built-in-first-person-is-gated-by-the-level.md`.
**This supersedes the "what first person is like" table in the sub-section below** — everything
measured there is still correct **for Whitechapel**, and does not generalise.

| where | state | `T` |
| --- | --- | --- |
| Whitechapel (London hub) | idle, no enemies | **first person** ✅ |
| Wonderland | enemy engaged, moving | third person ❌ |
| Wonderland | **idle, no enemy, full stop** | **third person** ❌ |

`[verified-live 2026-09-09, n=4 presses in the idle enemy-free state]` The last row eliminates
combat, motion and an aggroed enemy in one measurement. **The gate is the level.**

⇒ It is a **London-hub look-around mode**, absent from the Wonderland levels that are most of the
game. **A VR mod cannot be built on it.** First person for this project has to be built from the
matrices we already control, which is what the North Star always assumed.

⚠️ `n=1` level each side. **NOT established:** why, and whether the split is really "London vs
Wonderland". One launch touching a second area on each side would settle it.

⚠️ **`T` fires TWO actions** — `EnterFPSByRS | OnRelease ToggleCloseFollowCamera`. When first person
is refused the close-follow half still fires and the camera visibly pulls in, so **"the key did
something" is not "first person engaged"**. That is how it was nearly misread.

⚠️ **`p00cam` IS NOT A GENERAL FIRST/THIRD-PERSON DETECTOR** — retracting the claim in the
sub-section below. Whitechapel third person 1.428148, first person 1.569685, **Wonderland third
person 1.010590** (hfov 89.4°). The field of view is scene-dependent, so those thresholds hold only
within one scene. Judge by eye: is Alice in the frame. `[measured 2026-09-09]`

⚠️ **And third-person pitch is NOT always 0** — it read **−8.59°** in Wonderland. The Whitechapel
follow camera happens to be level; the camera in general is not. `[measured 2026-09-09]`

### ⚠️ [PARTLY SUPERSEDED 2026-09-09c — Whitechapel only] THE GAME SHIPS A FIRST-PERSON CAMERA, AND IT IS ALREADY ON THE `T` KEY (2026-09-09, `/lm`, live)

Write-up: `modding-notes/2026-09-09-the-c0-census-answers-itself-and-alice-ships-a-first-person-camera.md` §3.
Evidence: `dev-archive/recon/2026-09-09-c0-census-camera-yaw-and-the-built-in-first-person-camera/`.

**Press `T` in gameplay. Alice leaves the frame and the camera drops to eye level.**
`[verified-live 2026-09-09, n=1 launch]` No mod, no rebind, no console. The shipped
`Documents\My Games\Alice Madness Returns\AliceGame\Config\AliceControlLayout.ini` carries

```
KeyBindArray1=(Name="T",Command="EnterFPSByRS | OnRelease ToggleCloseFollowCamera")
KeyBindArray1=(Name="XboxTypeS_RightThumbstick",Command="ToggleGhost | OnRelease ToggleCloseFollowCamera |EnterFPS")
```

and `AliceInput.ini` carries dedicated first-person look scales, `LookRightScaleForFP=500` and
`LookUpScaleForFP=-350`.

⚠️ **Why this took so long to find, and the lesson to carry.** The action's primary home is a
**controller chord** (right-stick click), which is exactly the case the toolkit's PLAYBOOK warns
pressing keys will never discover. The project had read `AliceInput.ini` several times and had never
opened `AliceControlLayout.ini`. **On a UE3 title, read every `*Input*` and `*ControlLayout*` ini
before concluding a feature is absent.**

> ⚠️ **CORRECTED 2026-09-09c (`/pd`).** The clause that used to end this paragraph said
> `AliceControlLayout.ini` "is where this game keeps its *action* bindings" and that
> "`AliceInput.ini` holds only axes and aliases". **Both halves are wrong.** `AliceInput.ini`
> carries **`[Engine.KeyCommands]`**, the 33-entry action→command table; `AliceControlLayout.ini`
> binds nothing at runtime. See §6c. The `T` observation above is unaffected — it was
> `[verified-live]`; only the explanation of *why* it works was wrong.

## 6d. ⭐⭐ THE EYE POINT IS IN THE MATRIX — camera position out, head offset in (2026-09-09d, `/pd`, no launch)

Write-up: `modding-notes/2026-09-09d-the-eye-point-was-in-the-matrix-all-along.md`.
Evidence: `dev-archive/recon/2026-09-09d-the-eye-point-is-in-the-matrix/`.

**The `BugIt` pose dump was never needed.** The 2026-09-09 retraction removed the only known route
to camera position and eye height. The position is recoverable from the ViewProjection alone —
three dot products out of register 3, from quantities this project already reads.

With `column_j` = `(regs[0][j], regs[1][j], regs[2][j])`, for `VP = V·P` with a symmetric
projection over a rigid view:

| | |
| --- | --- |
| `column_3` | `forward`, unit — what `row3_len` reads as 1 |
| `column_0` | `p00 · right` — its length is what `recover_p00` returns |
| `column_1` | `p11 · up` |
| `regs[3][j]` | `-(eye · column_j)` |

⇒ `eye.right = -regs[3][0]/p00`, `eye.up = -regs[3][1]/p11`, `eye.forward = -regs[3][3]`, and
`eye` follows because the basis is orthonormal.

**Moving the eye** by a world offset `d` is translating the world by `-d`:
`regs[3][j] -= dot(d, column_j)` for `j = 0..3`. Four dot products, exact, and correct for any
offset — **including a forward component, which a shear cannot express at all.**

⚠️ **All three functions are gated on `alice_stereo_is_camera_vp()`, and that is load-bearing.**
The recovery is valid only for an orthonormal basis, which is exactly what that function's two
tests establish — and it means **a matrix we have already sheared is refused**, because the shear
adds `S·column_3` into `column_0`. **Read and offset BEFORE `alice_state_observe_vp()`, never
after.** Applied after, it is refused every frame, the camera never moves, and nothing says why;
the proxy counts refusals (`refused=` in `camtrace`) so that cannot stay silent.

### ⚠️⚠️ DO NOT PUT THE IPD IN THE HEAD OFFSET

The per-eye separation is **already** inside `alice_stereo_apply_viewproj()` — its one-element part
"alone reproduces a parallel (on-axis) eye translation", with `column_0 += S·column_3` making it
off-axis. Passing an eye separation as `dx` as well translates the eye **twice**: wrong by exactly
one IPD, invisible in a static test, obvious only in a headset.

**Pinned by test, not by warning:** a pure eye translation touches **register 3 only**; the shear
also rewrites **column 0**. The two are distinguishable in the matrix itself. The IPD stays in the
shear; the head/body offset stays in `alice_stereo_apply_eye_offset()`.

### Verified, and the tests were checked against themselves

Ground truth is built the other way round — a VP constructed from an explicit awkward pose (no axis
world-aligned, eye at `(1234.5, −678.25, 90.125)`, aspect ≠ 1), then read back.
`[verified-numerically 2026-09-09]`: basis, position, an offset landing exactly where asked, the
inverse returning to the original, a zero offset **bit-identical**, and a sheared matrix refused by
both reader and writer.

⚠️ **Mutation-checked:** flipping one sign in the recovery produces **63 failures**; restoring it
gives all-pass. A suite that cannot fail is not evidence.

### Where the head offset comes from — the honest answer

**A tuned constant, for now.** There is no head tracker in this loop and nothing in the game reports
where a head would be, so it is three numbers dialled by eye; later the same three arrive from an
HMD pose and the function does not change. Tuning is by **hotkey**, because this proxy has no ini at
all: **F3** selects an axis, **F4/F5** step it by ∓5 units. All three default to **0**, so an untuned
build takes the previous path. ⚠️ F1–F5 were the only F-keys the proxy was not already using; the
game may bind some itself, and that collision is untested.

`[compile-verified 2026-09-09]`, exports unchanged, full suite green.

## 6c. ⭐⭐ HOW KEY BINDING ACTUALLY WORKS — two files, and neither is `ControlLayout` (2026-09-09c, `/pd`, no launch)

Write-up: `modding-notes/2026-09-09c-the-key-layout-lives-in-two-files-and-neither-is-controllayout.md`.
Evidence: `dev-archive/recon/2026-09-09c-how-key-binding-actually-works/`.
Tool: `dev-archive/tools/parse_gameconfig_cfg.py`.

| half | where | what it holds |
| --- | --- | --- |
| **the command** | `[Engine.KeyCommands]` in **`AliceInput.ini`** | 33 `Key_<Action> = <command string>` entries |
| **the key** | **`CheckPoint\<profile>\GameConfig_PC.CFG`** | a FIXED array of **33 × 2 = 66** key-name strings — primary for actions 1..33, then secondary for actions 1..33 |

`[measured 2026-09-09]` — 66 length-prefixed strings parsed from the 2,148-byte profile against 33
ini entries; the counts match exactly and **the profile holds no command text anywhere**.

**The anchor that makes the pairing more than arithmetic:** slot 5 reads `T` / `Key_AimingMode` /
`EnterFPSByRS`, and "`T` enters first person" is the one binding verified live here. Slots 1–4 are
`W`/`S`/`A`/`D` against the four movement actions, 11 `SpaceBar` against `Key_Jump`, 12/13 the mouse
buttons against melee/range.

**⇒ The bindable action set is FIXED AT 33.** No ini edit can create a 34th, because the key for
action *n* comes from a fixed-size array with no slot 34. `T` works because it *ships* in slot 5.
That is the mechanism behind the 2026-09-09 retraction.

⚠️ **`ControlLayout` was being reloaded the whole time** — the user copy's `[IniVersion]` stamp went
from `1787589835` to `1788952193` after the edit, i.e. UE3 regenerated it from the modified default
exactly as designed `[measured 2026-09-09]`. The file was read; it is simply not what binds keys.

**Corroboration from the exe** (`.rdata` is not encrypted by the SteamStub wrapper): `CheckPoint\` +
`GameConfig_PC` + `.CFG` appear three times with the section name **`Engine.KeyCommands`** adjacent
in the same string block; and the native thunks are all index-based — `execGetAliceKeys`,
`execSetAliceKeys`, `execGetAliceKeyIndex`, `execExecRebindKey`, `execExecResetKeyBindings`,
`execExecControlLayout`. A getter, a setter and an *index*, and no "add a binding" call.
⚠️ `KeyBindArray` appears nowhere in the exe in either encoding, but that carries no weight on its
own — UE3 config property names come from the script packages, not the exe.

### ⭐ What this unblocks: repoint an EXISTING action

Eight of the 33 actions have **no key at all** `[measured 2026-09-09]`:
`Key_SwitchLockedTargetRight`, `Key_PCAttackType`, `Key_ChangeWeaponGroup`, `Key_VorpalBladeAttack`,
`Key_PepperGrinderAttack`, `Key_HobbyHorseAttack`, `Key_ArmTeapotCannonAttack`, `Key_Attack`. And
three actions (`Key_LockOn`, `Key_LockOn1`, `Key_LockOn2`) all sit on `CapsLock` with near-identical
commands, so at least two are redundant.

So an arbitrary command CAN be run — not by adding a binding, but by **changing what an existing
action does**, in `AliceInput.ini`. That restores the route to `BugIt`, and with it camera position
and eye height, which the retraction had stranded.

- **Cheapest test:** repoint `Key_LockOn2` (already on `CapsLock`) and press it. Needs only an ini
  edit and no key assignment, and it answers whether commands are read from the ini at all.
- **Cleaner but costlier:** repoint a keyless action such as `Key_PCAttackType`, then give it a key
  via the CONTROLS UI or by writing a key name into its profile slot.

⚠️ `[inferred-static 2026-09-09]` — **not run.** The result that would show the derivation is wrong
rather than a detail needing tuning: repointing `Key_LockOn2` and pressing `CapsLock` produces the
old lock-on behaviour and nothing else, which would mean commands are not read from the ini either.

| measured in first person | value |
| --- | --- |
| hfov | ≈ 65.1° (`p00cam` 1.569685) vs 70.0° third person `[measured 2026-09-09]` |
| yaw per numpad press | roughly 20°, but **not a constant** — −21.13 / −21.16 / +5.78÷2 / −12.44÷4. Still far finer than third person's 94° `[measured 2026-09-09, n=4 bursts]` |
| pitch per numpad press | moves, and **clamps at about ±90°** (straight up / straight down); the per-press amount is not constant `[measured 2026-09-09, n=4 bursts]` |
| survives walking | yes, 12 forward taps `[verified-live 2026-09-09, n=1]` |
| what leaves it | `QuitFPS` is bound alongside attack, weapon switch and most context actions `[inferred-static 2026-09-09]` |

**The camera is far more finely aimable in first person than in third**, and that — not the FOV — is
why this matters for the VR work: every camera experiment so far has had a 94°-per-press control.
⚠️ **But the first-person step is not a constant**, so a session that needs a KNOWN angle should
still drive the third-person camera, whose −94.2° repeats to 1%. Aiming in first person is a
look-and-adjust loop against the `camtrace` line, not a calculation.

**More of the same vocabulary is in that file and NONE of it has been tried:** `EnterFPS`,
`QuitFPS`, `ChangeCameraMode`, `ToggleCloseFollowCamera`, `TogglePOI`, `ToggleGhost`,
`togglephysicsmode`, `BugItForGameController`, `StatUnitAndStatFPS`. `[reported 2026-09-09]`
`BugItForGameController` is the one to try first — 2026-09-08 settled that the console is not
exposed in this retail build, and this reaches the same `BugIt` pose dump without one.

### ⭐⭐ WHAT ELSE WRITES `c0`? NOTHING *BINDS* IT — AND THE MYSTERY WRITE MAY NOT BE A MATRIX (2026-09-09b, `/pd`, no launch)

Write-up: `modding-notes/2026-09-09b-nothing-else-binds-c0-and-the-mystery-write-may-not-be-a-matrix.md`.
Evidence: `dev-archive/recon/2026-09-09b-what-else-writes-c0/`. Tool: `dev-archive/tools/c0_constant_census.py`.

**Nothing but `ViewProjectionMatrix` is bound to vertex `c0` by any material shader**
`[measured 2026-09-09]` — 2,431 of 2,807 `vs_3_0` tables carry it there and the other 376 bind
*nothing* at c0. So the once-per-frame non-camera write is not some other named constant sharing
the register.

⚠️ **Every earlier pass read only `RefShaderCache`.** UE3 keeps its post-process, filter and
fullscreen shaders in **`GlobalShaderCache-PC-D3D-SM3.bin`** — the passes that run *last* in a
frame, which is exactly what the census says the mystery write is. It had never been examined.

⭐ **And it holds exactly ONE vertex shader binding a non-view constant at `c0`: `SampleOffsets`,
an `c0 ×8` array, declaring no other constants at all** `[measured 2026-09-09]` — the shape of a
UE3 filter/blur vertex shader.

**The proxy intercepts on `start == 0 && count >= 4`.** A 4×4 satisfies that with `count == 4`;
so does an 8-register array. That single fact fits every measured property of the mystery write
without a second *view* having to exist at all:

| census observation | fits a blur pass? |
| --- | --- |
| exactly one non-camera write per frame | a single post-process filter setup |
| always the LAST write of the frame | post-processing runs last |
| never camera-shaped | sample offsets are not a projection |
| `p00 = 0.0022`, three orders below the camera's | ≈ one texel of UV at a reduced-resolution target |

⚠️ **`[hypothesis]`, not a finding** — a mechanism derived from what the game *ships*, not a
measurement of what it *does*. Either of two observations kills it: the write arriving with
`count == 4`, or the dumped rows looking like a projection.

⚠️ **If it holds it is a DEFECT, not a curiosity:** the proxy shears every qualifying `c0` write,
so with stereo on it has been writing a shear into a blur's sample offsets. The fix would be to
tighten the interception to `count == 4`.

#### The instruments that settle it (built, tested, deployed, NEVER RUN)

- **`alice_stereo_classify_vp()`** — replaces the 0/1 of `is_camera_vp()` with the *reason*:
  `CAMERA` / `AFFINE-ORTHO` (|row3|≈0, i.e. shadow, light or 2D canvas) / `SCALED-PERSP`
  (perspective × a uniform scale — the case a scale factor *would* fix, and the one 2026-09-08c
  wrongly assumed) / `SKEWED` (row0 not ⊥ row3) / `DEGENERATE`. It reports the raw `p00`,
  `|row3|`, `perp` and `c3.w` **beside** the verdict, because this project has already been burnt
  by a diagnostic printing *"uniformly scaled by ~1× … CONFIRMED"* for `|row3| = 1.0`.
  9 checks against ground truth built in the test `[verified-numerically 2026-09-09]`.
  ⚠️ **Known limit, kept deliberately visible by its own test:** `AFFINE-ORTHO` cannot separate a
  2D canvas from a shadow volume. Only the backbuffer width can, so the proxy now records it and
  prints `extent = 2/p00` next to it.
- **The same-frame `c0dump`** — camera matrix and the frame's last non-camera matrix, in full, on
  one frame, with both verdicts. Capped at 6, at frame 150 and every 1800 after.
- **⭐ `Vector4fCount`, which was never recorded at all** — the cheapest discriminator there is.
- ⚠️ **A gap closed on the way:** the old census ran *inside* the `is_perspective()` gate, so an
  orthographic write at `c0` was not merely unclassified, it was **invisible**. Every `c0` write is
  now classified.

`[compile-verified 2026-09-09]`, `-Wall -Wextra` clean, exports intact, existing suite still green.

### ⭐⭐ THE `c0` CENSUS, READ LIVE (2026-09-09, `/lm`) — CONFIRMS THE CORRECTION BELOW

`range=[0.002210 .. 2.747477]` across 5400 frames: **the spread is three orders of magnitude, so
more than one matrix reaches `c0`** `[measured 2026-09-09, n=1 launch]`. The `/pd` correction
immediately below was right, and this is the live evidence it asked for.

Three things the census added that the correction could not:

1. **The non-camera matrix is written EXACTLY ONCE PER FRAME, and it is the LAST write of the
   frame.** Non-camera-shaped writes rise by exactly 900 per 900-frame interval, three intervals
   running. `[verified-numerically 2026-09-09, n=3 intervals]` That is the whole mechanism behind
   the 2026-09-08 `p00=0.0022` reading — a one-field report shows the last writer.
2. **About 38 camera-shaped writes per frame, and they all carry ONE heading** (`spread` reads
   0.000 in every trace line of two launches) `[measured 2026-09-09, n=2 launches]`. So "the
   camera's matrix" is well defined within a frame.
3. **The camera's `p00` is scene-dependent, not a constant:** 2.747477 in menus (hfov 39.9°),
   1.428148 in Whitechapel (70.0°), 1.569685 in first person (65.1°). The 1.112762 the
   first-perspective diagnostic prints (83.9°) is simply whichever camera was up at that moment.
   `[measured 2026-09-09]`
4. **The classifier's documented limit does not bite on this game.** A tiny-`p00` matrix of the
   right shape *would* be accepted, but Alice's actual 0.0022 matrix is **rejected** — it is the one
   non-camera write per frame. `[measured 2026-09-09, n=1 launch]`

### ⭐ THE CAMERA'S HEADING IS NOW AN INSTRUMENT (2026-09-09, `/lm`)

`alice_stereo_camera_angles()` — row 3 of a camera-shaped VP produces `clip.w` and has unit length,
so it **is** the camera's forward axis; UE3 is X-forward, Y-right, Z-up, so
`yaw = atan2(row3.y, row3.x)`, `pitch = asin(row3.z)`. Nothing calibrated, no convention guessed.
Nine host checks. `[compile-verified 2026-09-09]` The proxy logs a `camtrace` line every 30 frames
carrying `yaw`, `pitch`, an **unwrapped cumulative `total`**, `dmax` (largest single-frame step —
the accumulation is only trustworthy while this stays well under 180) and `spread`.

- **⭐ SIGN CONVENTION, the thing the board has wanted written down since 2026-09-07: POSITIVE PITCH
  IS UP.** Verified by eye at two angles — −30.15° is the cobbles, +60.27° is the sky.
  `[verified-live 2026-09-09, n=2 angles]`
- ⚠️ **`aLookUp` with a POSITIVE `Speed` pitches the view DOWN.** The axis name and its sign
  disagree, and nothing errors.
- **Third-person turn rate: one 80 ms press = −94.2°, and presses compose linearly**
  (−94.20, −94.17, −188.33/2, −380.57/4) `[verified-numerically 2026-09-09, n=4, spread ~1%]`.
  This is why 2026-09-08b's screenshot method failed: its 10-to-100-press sweep was 2.6 to 26 full
  revolutions, so there was no return-to-start to find.
- ⚠️ **Hold duration is NOT a dial:** 20 ms → −5.31°, 40 ms → −168.69°, 80 ms → −94.20°,
  160 ms → +75.39°. Not monotonic, not proportional. Unexplained. `[measured 2026-09-09, n=1 each]`
- **Pitch is exactly 0.000 in third person** — the follow camera is level, which is why the sign
  convention could not be settled before first person was found.

### One crash, not reproduced (2026-09-09)

First launch of the session died in the level load: `AliceMadnessReturns.exe` + `0x00067d48`,
`c0000005`, faulting module the exe rather than `d3d9.dll`. Three further launches across three
proxy builds loaded the same save cleanly. `n=1`, cause not established.
`[measured 2026-09-09, n=1]`


### ⭐⭐ CORRECTION 2026-09-09 (`/pd`, no launch) — THE 505.8× SCALE FACTOR IS A PHANTOM: TWO MATRICES SHARE `c0`

Write-up: `modding-notes/2026-09-09-the-505x-scale-factor-is-a-phantom-two-matrices-share-c0.md`.
Deployed `d3d9.dll` md5 `1d534f20...`, 706,560 B, backup `d3d9.dll.bak-2026-09-09`. **Not run.**

**This supersedes the two sub-sections below it** (the 09-08d reading of the diagnostic, and
09-08c's "the amplitude is 380× wrong"). Their arithmetic is sound; their premise is not.

`c0..c3` is **not written by the camera alone.** The 2026-09-08 launch logged two real numbers
twenty seconds apart, from two different matrices:

| where | value | what it is |
| --- | --- | --- |
| `VP DIAGNOSTIC (first perspective VP)` | `\|row0.xyz\| = 1.112762`, `\|row3.xyz\| = 1.000000` | the **camera's** matrix — an ordinary 83.9° projection over a rigid view |
| every periodic report, 24,300 frames | `p00 = 0.0022` | whatever wrote `c0..c3` **last** in the frame |

The 09-08c derivation compared the measured disparity against `0.0022` as if it were the camera's
projection scale. It never was. **`|row3.xyz| = 1.000000` exactly ⇒ the camera's matrix carries no
uniform scale ⇒ `convergence` IS in its `clip.w` units and nothing needs multiplying.**
`[measured 2026-09-08]`

And the shear was never computed from `0.0022` for the camera's matrix: `device.cpp` recovers
`p00` from a write and applies the shear **to that same write**. That ordering now lives in one
shipped function, `alice_state_observe_vp()`, and is **tested** — camera → other → camera returns
the camera's shear both times. `[verified-numerically 2026-09-09]` It has been that way since the
original interception (`6f16757`, 2026-09-03; the only later change ungated the recovery from
`g_st.enabled`), which is what stops the 380× gap from having been real for the older measurements.
`[inferred-static 2026-09-09]`

**The measurements fit the camera's own `p00` with no scale factor**, all driven through the shipped
`stereo_ue3.c` (23 checks, 0 failures):

- model slope cap at C=300 is **2.374 px/unit ipd**; measured was **1.7833** — inside range, fitting
  at **z = 171.3 units**, in front of the convergence plane, which is why the readings were negative;
- the whole ipd sweep reproduces at that one depth: **−11.59 / −22.29 / −43.69 px** vs measured
  **12 / 22 / 44**;
- ⭐ **09-08c's own "the `p00` that would fit is 0.836" is a LOWER BOUND** (it assumes `z ≫ C`), and
  the camera's measured **1.112762 is 1.33× that minimum**. The requirement was always satisfied —
  this is the cheapest way to see the error. `[verified-numerically 2026-09-09]`

⚠️ **What is still open.** What the `0.0022` matrix *is* is **not established** — a post-process or
2D pass is a guess. It matters, because the proxy **shears it too**: any perspective write at `c0`
gets a shear, and whether that is harmless or a real defect is unknown. `[hypothesis]`

⚠️ **How the diagnostic said the opposite.** It branched on the ratio and printed, for
`|row3.xyz| = 1.0`, *"the matrix is uniformly scaled by ~1x ... the unit-mismatch hypothesis is
CONFIRMED"* — a sentence that contradicts itself, since "scaled by ~1×" **is** "not scaled". "Is this
matrix scaled?" is answered by `|row3.xyz|` **alone**, and the branch now tests that. **The general
trap:** a diagnostic printing a number *and* its interpretation is far more useful than one printing
only the number, and far more dangerous — the interpretation gets read and the number does not.

**New instruments (all ungated, so one launch with stereo OFF reads them):**

- `alice_stereo_is_camera_vp()` — `|row3.xyz| == 1` and `row0.xyz ⊥ row3.xyz`. A **uniformly scaled**
  camera matrix fails deliberately: that is the case a scale factor would genuinely fix, and it must
  stay visible. ⚠️ **Known limit:** a tiny-`p00` matrix of the right *shape* is a valid narrow-FOV
  camera and **is accepted**. The classifier narrows; the **range** settles.
- The **c0 census** in the periodic line: `p00 camera=... last=... range=[min .. max]` plus a count
  of camera-shaped writes, replacing the single `p00=` field that silently meant "last writer".

### ⚠️ [SUPERSEDED 2026-09-09 — see the correction above] THE ONE NUMBER THAT SETTLES IT IS SCALE-FREE, AND IT IS NOW LOGGED (2026-09-08d, `/pd`, no launch)

> **The scale-free ratio itself is still correct and still logged.** What is superseded is the
> reading of the result: `|row3.xyz| = 1.0` means the matrix is **not** scaled, so the branch below
> that concluded "the unit-mismatch hypothesis is confirmed" had it backwards.

Write-up: `modding-notes/2026-09-08d-the-scale-free-p00-and-a-build-that-could-not-be-checked.md`.
Deployed `d3d9.dll` md5 `37293f99...`, 704,512 B, dated backup kept. **Not run.**

**`|row0.xyz| / |row3.xyz|` is `p00` whatever units the matrix is in.** Row 0 produces `clip.x`,
row 3 produces `clip.w`; a uniform scale `k` multiplies both, so it cancels. That property is a
HOST TEST, not an assumption: `stereo_ue3_test.c` builds a matrix with `p00 = 0.836`, multiplies the
whole thing by **1/380**, and checks the raw `p00` is dragged down while **the ratio is unchanged**;
it also refuses an orthographic matrix instead of dividing by zero. `[verified-numerically
2026-09-08]` Had the ratio not been scale-free, the number logged in-game would have been
uninterpretable and the launch wasted.

The proxy now logs mathematical **row 0** and **row 3** in full, their xyz lengths, and the ratio -
**and states what the reading means**, so it does not depend on having the 09-08c note open. It
fires on the **first perspective ViewProjection** (a launch that never touches a hotkey still
answers the question) and again on **every F9** (the FOV changes in cutscenes and on aiming). Cost:
one 64-byte memcpy on a path that already copies the same bytes, no I/O except on those events.

- ratio ~ **0.3-3** => ordinary projection scale (it reports the implied hfov): the matrix IS
  uniformly scaled, `p00_cached` is not the projection scale, `convergence` is not in `clip.w`
  units, and the unit-mismatch hypothesis is **confirmed**.
- ratio ~ **0.0022** => `p00` really is tiny, the hypothesis is **disproved**, and what produced the
  measured screen motion becomes the next question.

### ⛔️ AND THIS BUILD COULD NEVER HAVE BEEN HASH-CHECKED (found the same session)

`build.sh` had no `-Wl,--no-insert-timestamp`, so the PE TimeDateStamp changed on every link: two
builds of **identical** source hashed `56fe72c6...` then `f4fee746...` back to back
`[verified-numerically 2026-09-08]`. CONVENTIONS.md's "rebuild and compare the hash" check therefore
**silently could not work here**, and a session doing it properly would have concluded the deployed
DLL was stale when it was not.

Checked the way that does work - a byte diff: the deployed DLL differed from a build of its own
committed source in **exactly six bytes**, at offsets 129-131 and 249861-249863, the PE header and
debug-directory timestamps. **The stamp was honest; only the proof was missing.** The flag is now in
and reproducibility is verified by the check that could not have passed before - two builds now hash
identically. ⚠️ **Fifth project found with this defect**; treat it as a default for any new proxy.

### ⚠️ [PARTLY SUPERSEDED 2026-09-09] disparity(z) DERIVED: the SHAPE is an off-axis frustum, the AMPLITUDE is 380x wrong (2026-09-08c, `/pd`, no launch)

> **The SHAPE half stands** — `disparity(z) = p00·ipd·W/2·(1/C − 1/z)`, verified to 6e-8 px against
> the shipped shear, is unaffected. **The AMPLITUDE half is withdrawn:** it compares the measurement
> against `p00 = 0.0022`, which belongs to a different matrix. See the correction at the top of §6.

Write-up: `modding-notes/2026-09-08c-the-disparity-shape-is-right-and-the-amplitude-is-380x-wrong.md`.
Tool: `proxy-d3d9/test/disparity_model.c`, which **links the shipped `stereo_ue3.c`** and drives a
point through the real `alice_stereo_apply_viewproj()`; it runs on every `build-stereo-test.sh`.
**17 checks, 0 failures.**

**The closed form**, verified against the shipped shear to 6e-8 px over 45 `(ipd, C, z)` points
`[verified-numerically 2026-09-08]`:

> `disparity(z) = p00 * ipd * W / 2 * (1/C - 1/z)`

with `eye_dx = +-ipd/2`. Two structural consequences: disparity is **exactly zero at z = C**, and
there is a **finite ceiling** `p00*ipd*W/(2C)` that **does not depend on depth at all**.

- **✅ THE SHAPE IS CONFIRMED, from a sweep that needs no depth estimate.** Alice at three
  convergences (`98 -> +78`, `300 -> -1`, `915 -> +26`): fitting `K` and `z` to the first two
  predicts the third at **-26.8 px vs 26 measured (97%)**, and the fitted depth lands at **292
  units**, on the convergence that measured ~0. The `1/C - 1/z` form describes this field.
  ⚠️ It **requires** the conv-915 disparity to be NEGATIVE - eyes reversed relative to conv 98.
  No capture has confirmed that sign. `[verified-numerically 2026-09-08]`
- **❌ THE AMPLITUDE CANNOT COME FROM `p00 = 0.0022`.** At ipd 6.5, W 1280, C 300 the largest
  disparity this code can produce **at any depth** is **0.0305 px**; +34 and +60 px were measured.
  **+60 px is 1,967x the ceiling, and no depth closes that gap because the ceiling is
  depth-independent.** Independently, the measured ipd slope **1.7833 px/unit** (R^2 0.99948, n=4)
  is **380x** the model's maximum slope of 0.00469. `[verified-numerically 2026-09-08]`
- **⭐ The p00 that WOULD fit is 0.836 - `1/tan(hfov/2)` for a 100 degree horizontal FOV**, an
  entirely ordinary projection scale. So **`p00 = 0.0022` is almost certainly not the projection
  x-scale it is documented as**, even though it is real and stable to four decimals across 33,300
  frames.
- **The reconciling hypothesis, arithmetically exact but unproven:** `clip.w` and the `convergence`
  slider are **not in the same units**. When `w << C` the `C` cancels and the shift tends to
  `-p00*(ipd/2)/w`. Solving for the `w` that gives the measured 12 px yields **w = 0.763**, so
  **C/w = 393** - the same factor, from a different measurement - and feeding that `w` back through
  the shipped code reproduces the whole ipd sweep (12.0 / 23.0 / 45.1 vs 12 / 22 / 44).
  `[hypothesis]`
- **⚠️ A sign convention is now load-bearing and is recorded nowhere.** Solved for implied `w`,
  the two positive populations have **no physical solution** (w comes out negative); reading them as
  magnitudes rescues those two and **breaks Alice**, whose value is already negative. **No single
  convention makes all three physical**, so the gap is not a sign artefact - it is the amplitude.
- **⭐ THE ONE CHEAP TEST:** log the full mathematical **row 0 and row 3** of the ViewProjection
  once beside the recovered `p00`, on the existing F9 path. `|row0.xyz| ~ 0.0022` with a unit-ish
  `row3.xyz` => the matrix really is world-to-clip and the screen motion did **not** come from our
  `S`; a uniformly scaled matrix => the unit mismatch is confirmed and the fix is one scale factor.
  **Until then, treat the convergence numbers as dimensionless knob positions, not distances** -
  which is how they have actually been used.


### ⛔️ THE EXE'S `.text` IS ENCRYPTED AT REST — NO STATIC CODE SCAN ON THIS BINARY CAN RETURN A TRUE NEGATIVE (2026-09-02, `/pd`, no launch)

**Read this before planning any static work on `AliceMadnessReturns.exe`.** `.text` measures
**entropy 8.00** (the ceiling), the **entry point is at `01661310` inside a `.bind` wrapper section**
(entropy 7.98) rather than in `.text`, `.text` does not disassemble, and it contains **zero `CC`
padding runs** — impossible for a real MSVC code section. `[measured 2026-09-02]` A wrapper decrypts
it at load.

> #### ✅ THE WRAPPER IS IDENTIFIED: **SteamStub v3.x**, and unpacking is a STATIC step (2026-09-03)
>
> `/gr` proposed SteamStub from the section signature; this session confirmed it **in the stub's own
> code**. The v3.x header magic **`0xC0DEC0DF`** is present at `.bind + 0x4A0` (VA `0x016614A0`), and
> the surrounding instructions are the stub validating it:
> `mov ecx,[ebp-8]` / `cmp dword [ecx+4], 0xC0DEC0DF` / `je …`. The entry point at `0x01661310` is a
> textbook stub prologue (`call $+5`, push-all, `and esp,-16`). `[inferred-static 2026-09-03]`
>
> ⚠️ **The cheap second witness `/gr` suggested — `steam_api.dll` in the import table — FAILED, and
> should not be re-run.** There is no `steam_api.dll` in the import table, no `steam_api.dll`
> anywhere in the install, and **no "steam" string anywhere in the exe**. That is not evidence
> against SteamStub: it means the game has no Steamworks *API* integration at all, only Valve's DRM
> wrapper applied at upload — plausible for an EA-published title on Steam. The header magic is the
> witness that actually carries the claim. `[measured 2026-09-03]`
>
> **Consequence: `.text` can be decrypted without running the game.** Public open-source unpackers
> cover SteamStub v3.x — [Steamless](https://github.com/atom0s/Steamless) (this exe is PE32, in
> range) and [Steamstub-v3-Unpacker](https://github.com/GHFear/Steamstub-v3-Unpacker). **Work on a
> COPY; never overwrite the shipped exe**, and expect the unpacked binary **not to launch** (it still
> wants the environment the stub set up) — that is the expected outcome, not a failed unpack.
> `[reported 2026-09-03]`

- **Consequence:** strings, `push imm32` operands and xrefs in `.text` are all unreadable off disk.
  A scan that finds nothing has found nothing *about the game* — the test could not have produced a
  positive result.
> ### ✅✅ SETTLED 2026-09-03 — **THE MODE IS AUTOMATIC.** The scan ran, on an unpacked copy, with the game never launched.
>
> A **copy** of the exe was unpacked with Steamless v3.1.0.5, which independently identified it as
> **SteamStub Variant 3.1 (x86)** — matching the static call above. Unpack validated before trusting
> anything from it: `.text` entropy **8.00 → 6.71**, `CC` padding **0 → 1** run, `.bind` removed,
> entry point moved `0x01661310` (`.bind`) → **`0x00FAEF67`** (the original OEP in `.text`), and
> `.text` now disassembles as clean MSVC code. `[measured 2026-09-03]`
>
> | function | id | unpacked | **still-packed control** |
> | --- | --- | --- | --- |
> | `NvAPI_Initialize` | `0x0150E828` | **1** ✅ positive control | 0 |
> | **`Stereo_SetActiveEye`** | `0x96EEA9F8` | **0** | 0 |
> | **`Stereo_SetDriverMode`** | `0x5E8F0BEC` | **0** | 0 |
> | `Stereo_CreateHandleFromIUnknown` | `0xAC7E37F4` | 1 | 0 |
> | `Stereo_Activate` | `0xF6A1AD68` | 1 | 0 |
> | `Stereo_GetSeparation` | `0x451F2134` | 1 | 0 |
> | `Stereo_GetConvergence` | `0x4AB00934` | 1 | 0 |
> | `Stereo_GetEyeSeparation` | `0xCE653127` | 1 | 0 |
> | `Stereo_Enable` / `SetSeparation` / `SetSurfaceCreationMode` | — | 0 | 0 |
>
> **The packed column is all zero including the positive control** — that scan could not have
> produced a positive, which is precisely the false negative the 2026-09-02 note warned about, now
> demonstrated side by side rather than argued.
>
> **All six live references sit in ONE 825-byte function** (`0x00E65663`–`0x00E6599C` in the
> unpacked image): init → create handle → activate → **read** separation, convergence and eye
> separation. **Three getters and no setters at all** — `SetSeparation` is 0 here where Alan Wake
> had 1, so Alice is even more purely a consumer. `[inferred-static 2026-09-03]`
>
> **⛔️ Consequence — the same verdict as `alan-wake-vr`, reached independently: the game never takes
> the eyes off the driver.** It activates 3D Vision and reads back what the driver decided.
> `NvStereoEnabled` (`ps c3`, 28,017 shaders) and `NvStereoFixTexture` (14,479) are therefore
> **consumers of driver-published values, not producers of an eye offset**.
>
> ✅ **This CONFIRMS the existing plan rather than changing it** — exactly the outcome `/gr`
> pre-committed to: *"no callers on either, with callers on Activate/getters ⇒ Automatic (same as
> Alan Wake; the render-twice + own-texture plan is unchanged)."* And it is better news than it
> sounds: because the game *reads* separation and convergence and feeds them to its own shaders, a
> proxy that supplies those values itself — writing `ps c3` and binding its own stereo texture —
> drives a stereo path the shipping shaders already implement. The discontinued NVIDIA driver is not
> required. Evidence: `dev-archive/recon/2026-09-03-steamstub-and-matrix-layout/nvapi-direct-vs-automatic-scan.txt`.
>
> ⚠️ **The unpacked binary is GAME CONTENT and is deliberately not committed.** Regenerate in one
> command when needed; work on a copy, never the shipped exe.

- **🚦 The scan's history, kept because the gating lesson is the point (re-gated `[FLAT]` → `[PD]` 2026-09-03, then answered the same day).** `/gr`'s method
  (`SetActiveEye` `0x96EEA9F8`, `SetDriverMode` `0x5E8F0BEC`, control `NvAPI_Initialize`
  `0x0150E828`) is sound and works on Alan Wake's unencrypted exe. It was gated `[FLAT]` on
  2026-09-02 because the remedy looked like a runtime memory dump; **it is not — unpack a copy with
  Steamless first, statically.** The runtime dump (`static-disasm.py --raw`, the Manhunt route) is
  now only the fallback if the variant is unrecognised.
  - **The discriminator ids are already settled and need no re-checking**: `0x96EEA9F8` →
    `NvAPI_Stereo_SetActiveEye`, `0x5E8F0BEC` → `NvAPI_Stereo_SetDriverMode`, read out of NVIDIA's
    published `nvapi_interface.h` three times by two session types, with two positive controls inside
    the query. `[reported 2026-09-03, n=3 independent reads]` — first-party, from NVIDIA's own
    published header, but a document read rather than a measurement.
  - ⚠️ **Re-run the positive control on the unpacked file before believing any result**:
    `NvAPI_Initialize` `0x0150E828` must be found. That control is what stopped the 2026-09-02 scan
    being misread as a clean "Automatic", and it is what will stop a *partial* unpack being misread
    the same way.
- **It also withdraws an inference:** the 2026-09-01 "the exe has essentially no stereo strings, so
  the integration lives in the engine layer" reasoning. The premise is an artefact of encryption.
  `[disproved 2026-09-02]` as an inference.
- **`.rdata`/`.data` are NOT encrypted** and stay fully readable — which is where the table below
  came from, and why the shader-cache work is unaffected.
- **Injection is unaffected** — the `d3d9.dll` proxy is live-verified on this build.
- ⚠️ **§4's "no DRM" needs reading narrowly:** EA's Cuckoo really is gone, but the shipping binary is
  **wrapped**. Correction, not contradiction.

#### The NVAPI interface table is readable — and it does NOT decide Direct vs Automatic

A **105-entry** table at `013d452c` (`{u32; u32; u32 interfaceId}`), ids matching NVIDIA's published
`nvapi_interface.h`. **27 are `NvAPI_Stereo_*`** (Enable/Disable/IsEnabled, CreateHandleFromIUnknown,
DestroyHandle, Activate/Deactivate/IsActivated, Get/Set/Increase/Decrease Separation and Convergence,
GetEyeSeparation, Get/SetFrustumAdjustMode, ReverseStereoBlitControl, SetNotificationMessage,
Capture{Jpeg,Png}Image, and the four configuration-profile-registry calls). **`SetActiveEye` and
`SetDriverMode` are absent.**

**⚠️ Do not read that absence as "Automatic".** The same table carries `NvAPI_VIO_*` (Quadro SDI),
`GPU_GetECC*`, `Mosaic` and `I2CRead/Write` — functions no game calls — so it is **the linked NVAPI
SDK's fixed table, not this game's usage.** The positive control settles it: **`NvAPI_Initialize` is
missing from the table too**, and the game certainly calls it (`nvapi.dll` and
`nvapi_QueryInterface` sit in readable `.rdata` at `0131ba4c`). `[inferred-static 2026-09-02]`
Full decode: `dev-archive/recon/2026-09-02-text-is-encrypted-and-nvapi-table/`.

#### Register facts re-derived 2026-09-02, with two refinements

Every published number reproduces `[verified-numerically 2026-09-02]` (45,832 tables = 43,025
`ps_3_0` + 2,807 `vs_3_0`; `ViewProjectionMatrix` `vs_3_0` `c0 ×4` in 2,431, no exceptions;
`CameraPosition` `vs_3_0` `c4` 1,989; `PreViewTranslation` `vs_3_0` `c5` 486; `NvStereoEnabled`
`ps_3_0` `c3` 28,017). Two things the earlier pass did not separate:

- **`NvStereoFixTexture` is not only `s1`:** `s1` 14,221, **`s3` 202, `s0` 46, `s2` 10.** A proxy
  binding a stereo texture must key off the sampler each shader declares — assuming `s1` silently
  mis-feeds 258 shaders.
- **`ps_3_0` `c4` is a slot with two meanings:** `ViewProjectionMatrix` `c4 ×4` in 4,122 shaders, but
  **`WorldToViewMatrix` `c4 ×3` in 135**. Writing `ps c4` blind corrupts those 135.

#### ✅ Per-eye maths: VERIFIED 2026-09-03 — and the matrix is stored TRANSPOSED from Alan Wake's

NVIDIA's `x' = x + S·(w − C)` with `S = (f/aspect)·t/C` is confirmed correct, over **54
configurations** against ground truth built the other way (explicit asymmetric frustum + a
physically translated eye), with the thing under test evaluated by simulating the shader's own
accumulation. `[verified-numerically 2026-09-03, n=54 configurations]` Code:
`staging/alice-madness-returns-vr/proxy-d3d9/src/stereo_ue3.{h,c}`.

**✅ The `c5` immunity is demonstrated, not assumed.** Every case runs at `PreViewTranslation` of
**0, 1,000 and 250,000 units** and agrees at all three — so the drift trap below genuinely cannot
bite the clip-space form.

⚠️ **BUT THE IMPLEMENTATION IS A TRANSPOSE OF `alan-wake-vr`'s, AND COPYING THAT CODE HERE PRODUCES
GARBAGE.** Alice's `ViewProjectionMatrix` is **`D3DXPC_MATRIX_COLUMNS`** (Alan Wake's matrices are
`MATRIX_ROWS`), established two ways: the CTAB type metadata, and the shipped bytecode, whose
simplest vertex shader carrying it is

```
mul r0, c1, v0.y  ;  mad r0, c0, v0.x, r0  ;  mad r0, c2, v0.z, r0
mad r0, c3, v0.w, r0  ;  mov o0, r0
```

— i.e. `clip = c0·v.x + c1·v.y + c2·v.z + c3·v.w`, the row-vector form `mul(v, M)`, with **no `dp4`
against `c0` anywhere**. `[inferred-static 2026-09-03, two independent reads]` So **`clip.x` is the
`.x` LANE across all four registers, not `dot(c0, v)`**, and the edit is:

```
for i in 0..3:  c[i].x += S · c[i].w        then        c3.x -= S · C
```

against Alan Wake's `c0 += S·c3` then `c0.w -= S·C`. **The wording "row0' = row0 + S·row3" used here
before is correct as MATHEMATICS and misleading as INSTRUCTIONS** — in this layout the mathematical
row 0 is a lane, not a register. The test suite transplants the Alan Wake implementation verbatim
and shows it diverges (`ndc.x +0.355` vs `+0.324`) **and corrupts `clip.w`**, so the distinction is
falsifiable rather than asserted. Six mutants, all caught, control passes.

**✅ THE PIXEL STAGE IS ANSWERED 2026-09-03 — and NOT the way it was queued.** The plan was to
extend the matrix edit to `ps c4`. **Do not.** Two measured reasons:

1. **`ps c4` is wildly overloaded** — far worse than this dossier previously warned. Occupants
   include `UniformPixelVector_1` (14,557 shaders), `UniformPixelVector_0` (5,080),
   `WorldIncidentLighting` (4,130), `ViewProjectionMatrix` (4,122),
   `LightColorAndFalloffExponent` (2,843), `LightMapScale` (2,348)… **A blind `ps c4` write corrupts
   roughly 33,000 shaders, not the 135 recorded here before.** `[inferred-static 2026-09-03]`
2. **The shipped pixel shaders ALREADY apply the shear themselves.** From the bytecode:
   ```
   mad   r0.xyz, c4.xyww, v2.x, r0   ; clip = ViewProjectionMatrix * worldpos
   ifc   c3., -c3.x                  ; if (NvStereoEnabled)
     texld r1, c0.yzzw, s1           ;   read NvStereoFixTexture
     add   r1.y, r0.w, -r1.y         ;   w - convergence
     mad   r0.z, r1.x, r1.y, r0.x    ;   x + separation*(w - convergence)
   ```
   That is NVIDIA's `x' = x + S·(w − C)`, compiled into retail. **Shearing `ps c4` too would
   DOUBLE-APPLY it.** `[inferred-static 2026-09-03]`

**The stages are asymmetric, and that is the whole design.** `NvStereoEnabled` is in **28,017 of
43,025 pixel shaders, always at `ps c3`, zero exceptions** — and in **0 of 2,807 vertex shaders**.
Breakdown of the 28,017: 13,454 use it as a bare branch selector; **10,437 apply a screen-space fix**
(same formula, on an interpolated position); **4,042 apply the clip-space fix** above; 84 have the
matrix but no fix texture.

| stage | built-in stereo? | what we do |
| --- | --- | --- |
| vertex (2,807) | **none** | shear `vs c0` ourselves |
| pixel (43,025) | **yes, 28,017** | set `ps c3`, bind the fix texture — **never touch `ps c4`** |

⚠️ **THE COUPLING INVARIANT:** the pixel side must get **the same S and C** as the vertex shear, and
the flag must be non-zero whenever the matrix is sheared. Flag off ⇒ geometry moves while every
screen-space effect stays put; different S ⇒ they disagree by a constant. Both look like "broken
stereo" and neither is a maths error. `alice_stereo_fix_texel()` routes through the same
`alice_stereo_shear()` so they cannot drift apart.

**`NvStereoFixTexture` is bound per shader**, not at a fixed `s1`: `s1` (14,221), `s3` (202), `s0`
(46), `s2` (10) — hence `shadermap.c`, a CTAB parser plus a pointer-keyed registry.
**Validated against the game's own 45,832 shaders** against an independent Python pass; every bucket
agrees, including `NvStereoEnabled` never appearing outside `ps c3` and `PreViewTranslation` never
outside `vs c5`. `[verified-numerically 2026-09-03, n=45832 shaders]` Plus 36 configurations proving
the two stages land in the same place, and a falsifiability check that they diverge with the flag
off. Code and full account: `staging/alice-madness-returns-vr/proxy-d3d9/README-stereo.md`.

**Still open on this front:** nothing in the shader maths. What remains is the proxy plumbing.
The superseded note read: the pixel-stage half. `ViewProjectionMatrix` is also `ps_3_0 c4 ×4` in
4,122 shaders and needs the same treatment, but **`ps c4` is `WorldToViewMatrix` (4×3) in 135 other
shaders**, so a blind `ps c4` write corrupts those — it needs a per-shader register map, not a fixed
register. And `p00` recovery from the matrix assumes nothing non-rigid is baked in after the
projection (true for Alice's `c0`; not for a fused local-to-clip).

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

> **LIVE, 2026-09-04b (`/lm`) — RESOLVED: the vertex-c0 shear REACHES THE SCREEN (outcome 3).** The morning run read inconclusive; a same-day F9 double-toggle retest settled it. After enabled frames run, the F9 log reports `p00=known`, so the game DOES write the view-projection to vertex c0 and the proxy recovers it. Saturating the parameters (ipd 6.5→26.5 via F12, convergence 300→20.6 via F7) slid the WHOLE scene HORIZONTALLY (Alice centre→far left); restoring them (ipd→6.5, conv→300) recentred it exactly `[verified-live 2026-09-04, reversible]`. Proportional + reversible + horizontal (not vertical) = the shear lever works and the math lane is right. The default ipd 6.5/conv 300 shift was simply sub-visible. Still open: outcome 4 (does HUD/screen-space follow, i.e. the pixel-c4 concern) — needs a HUD/combat scene; and per-eye two-eye rendering. ⚠️ F12 is ALSO Steam's screenshot key (harmless; proxy sees it via GetAsyncKeyState too). Notes: modding-notes/2026-09-04b-f9-double-toggle-shear-reaches-the-screen.md.
> The M0 proxy wrapped the device and registered 6,725 shaders `[verified-live 2026-09-04]`, but the
> F9 shear test could not be read: the one-shot stats line fired before F9, the `vp_writes` counter
> is gated behind `g_st.enabled`, and the F9 log samples `p00` at the toggle instant — so
> `p00=NOT SEEN YET` is by construction, not measurement, and the before/after frame diff (mean ~5,
> no coherent horizontal shift) is scene animation, not a shear. **This neither validates nor
> disproves the c0 delivery below.** Cheap no-rebuild retest: F9 on → wait → F9 off → F9 on, read the
> SECOND `stereo ON` line's `p00`. `[PD]` fix: ungate `vp_writes`, log `have_p00` continuously, add a
> saturating shear mode. Notes: `modding-notes/2026-09-04-first-proxy-launch-interception-live-stereo-test-inconclusive.md`.
>
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
1. **✅ RESOLVED 2026-09-03 — the mode is AUTOMATIC.** This was recorded as genuinely ambiguous:
   Epic's page is titled *"UE3 and NVIDIA 3D Vision **Direct**"* (the optimistic reading), but an
   **eye-sign channel in a texture is the signature of the Automatic pattern** — an app rendering in
   Direct mode already knows which eye it is drawing. **The texture reading was right.** The caller
   scan on an unpacked copy (§6) finds **zero** references to both `Stereo_SetActiveEye` and
   `Stereo_SetDriverMode`, against live references to `Initialize`, `CreateHandleFromIUnknown`,
   `Activate` and three getters. `[inferred-static 2026-09-03]` Epic's *page title* describes what
   UE3 can support, not what this title shipped. **The plan above was unaffected either way, which
   is why it was still worth acting on — and it now stands confirmed rather than merely unblocked.**
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

### ⭐ THE TWO-EYE PATH IS BUILT (2026-09-04c, `/pd`, no launch), and the `/sr` one-element lead was already our own constant term

**Two-eye.** The mono shear was proven to reach the screen on 2026-09-04b, but it moves **one** view:
`alice_stereo_state.eye` existed and only F10 ever changed it, so both eyes had never actually been
drawn. A `wiggle` mode now alternates the eye **in `Present`, at the frame boundary** — never
mid-frame, because the vertex shear and the pixel stage's fix texture both read `g_st.eye` and must
agree within a frame. Each frame is therefore still exactly the single-eye path the 54-configuration
suite verifies, and the fix texture is re-uploaded once per frame (`applyPixelStereo()` already
caches on the eye). **F6** toggles it; while it is on, F10 is refused with a log line rather than
fighting it; a `wiggle flips` counter separates "not alternating" from "alternating and nothing
moved". `[compile-verified 2026-09-04]`, deployed (`d3d9.dll` 702,976 B; previous kept as
`d3d9.dll.bak-2026-09-04c-pre-twoeye`). **Not run.**

**Diagnostics ungated, which is why the 2026-09-04 morning launch was inconclusive.** `vp_writes`
and the `p00` recovery were gated behind `g_st.enabled`, and the summary line was one-shot at 2,000
shaders — which fired *before* stereo was ever enabled, reported zeros, and never printed again.
Counting and recovery are now unconditional (read-only; nothing reaches the device unless the shear
fires) and the line is periodic at frame 120 then every 900, carrying enabled/wiggle/eye/ipd/
convergence/`p00`/`S`/flips. **One launch now reads cleanly with stereo never enabled at all**, and
the F9 double-toggle dance is retired.

**The `/sr` one-element lead: declined, with the numbers.** `[verified-numerically 2026-09-04]`
`/sr` generalised `mad-max-vr`'s result — a per-eye offset is one matrix element — and correctly
warned it is the transposed element here. Re-derived: in this layout it is `c3.x -= p00 · eye_dx`,
and `alice_stereo_apply_viewproj()`'s second line is `regs[3][0] -= S * C` with
`S = p00 · eye_dx / C`, so **`S · C == p00 · eye_dx` identically — the one-element edit is already
the constant term of our shear.** Measured over six vertices from 12 to 8,000 units, the full shear
and the one-element edit alone differ in NDC x by **exactly `S`, a constant**, and not at all in `y`
or `clip.w`. Generally:

```
our shear = one-element edit + a constant NDC shift = parallel eye translation + convergence
          = off-axis (asymmetric-frustum) stereo
```

⇒ **Adopting the lead would delete the off-axis term, and that is not available to us.** The pixel
stage implements NVIDIA's two-parameter form in 28,017 shipped shaders we cannot modify, so the
vertex stage must use the same formula or the two disagree by a constant — geometry moves, every
screen-space effect stays put. See the coupling invariant in `stereo_ue3.h`. Verdict filed back to
`flat-to-vr-cross-engine-research/inbox/` so the technique page gains the condition; the
generalisation itself is sound and reproduces here exactly. Write-up: `modding-notes/2026-09-04c-the-two-eye-path-is-built-and-the-one-element-lead-was-already-in-our-code.md` §1.

### ⭐ CONFIRMED LIVE 2026-09-07 (`/lm`, one flat launch) — BOTH EYES REACH THE SCREEN, AND THE BASELINE IS PROPORTIONAL

The two-eye `wiggle` path built on 2026-09-04c was run for the first time. It works, and the
evidence is quantitative rather than "it looked like it moved".

**Method.** `F9` (stereo) then `F6` (wiggle) alternates the eye at the `Present` boundary; bursts of
screen captures are then correlated by column-mean profile. A stereo shear is a *coherent horizontal
translation*, which that measures directly; scene animation is not, and does not register.

**The control is the load-bearing part.** Stereo OFF, 16 captures of the live animated Whitechapel
scene (walking NPCs, fog, idle animation): **spread 0 px, every frame dx = +0**, corr 0.984–1.000.
The noise floor is zero, so any non-zero reading is signal `[verified-live 2026-09-07]`.

**Result.** Frames split into **exactly two clusters** at every setting, and the separation is
proportional to ipd `[verified-numerically 2026-09-07, n=4 ipd settings, 60 frames]`:

| ipd | 6.5 | 12.5 | 18.5 | 24.5 |
| --- | --- | --- | --- | --- |
| separation | 12 px | 22 px | 33 px | 44 px |

```
separation = 1.7833 * ipd + 0.108 px      R^2 = 0.99948      max |residual| = 0.40 px
```

Proportional, through the origin, sub-pixel residuals — a real baseline, not a shoved mono image.
`p00 = 0.0022`, recovered and stable to four decimals across 33,300 frames, and `p00=known` on the
**first** `F9`, so the double-toggle workaround is retired.

#### The disparity field is depth-dependent `[measured 2026-09-07]`

Block-matched over a 31×17 grid (trust filter peak > 0.55 and peak/second > 1.12; 416/527 tiles
trustworthy), at ipd 24.5 / conv 300: range **−5 … +63 px**, in three separated populations —
**Alice −1, world walls +34, NPCs +60**. A uniform slide would give one number everywhere.

#### ⚠️ Alice reading ≈ 0 is the convergence plane, NOT an unsheared character path

In the anaglyph Alice shows almost no fringing while the world doubles around her — which looks like
the classic "flat cardboard hero" failure. It is not. Sweeping convergence at fixed ipd 12.5 moves
her a long way: **conv 98 → +78, conv 300 → −1, conv 915 → +26** `[verified-live 2026-09-07, n=1 scene]`.
She *is* sheared; the third-person camera distance simply sits near the default convergence. The
rival hypothesis "skinned characters are skipped" is **`[disproved 2026-09-07]`**, and the NPCs
(skinned, +60) agree independently. Per-region ipd proportionality also holds: the same wall reads
+9 px at ipd 6.5 and +17 px at ipd 12.5, against 17.3 predicted `[verified-numerically 2026-09-07, n=2]`.

#### Screen-space: decals pass, HUD is still unjudged

**Decals move WITH the world `[verified-live 2026-09-07, n=1 scene]`** — wall posters +34 px,
identical to the bare brick beside (+34) and below (+34) them, peak 0.98–0.99. No tearing, so the
coupling invariant above holds for decals at least.

HUD/crosshair/SSAO remain unjudged: the save is at 0% completion and Alice has no HUD or combat
before Wonderland. `EXTRA CONTENT` is galleries only, **no playable level**, so there is no menu
shortcut `[verified-live 2026-09-07]`.

**The pause menu's visible world does not shear `[verified-live 2026-09-07, n=1]`** — and this is a
sound negative, not a dead test: frames kept advancing (24,300 → 25,200) and `wiggle flips` kept
climbing one per frame, so the eye really was alternating, yet capture spread was 0 px. Cause is
`[hypothesis]`.

⚠️ **`draws_fixed` is not evidence about the vertex path.** It counts *pixel*-shader fix-texture
bindings in `applyPixelStereo()`, not sheared draws. Its rate (≈5/frame in gameplay, ≈1/frame in
menus) is a separate curiosity.

#### ⚠️ Not established

Whether the disparity field matches an ideal off-axis frustum **quantitatively**. The convergence
sweep does not fit a simple "one uniform constant per convergence" model, but that is a limit of the
test: at conv 98 the disparity saturated the ±90 px search window, and the NPC region walks between
bursts. Whitechapel's far field is too dark to block-match at all (far probes peak 0.19–0.43 — *no
measurement*, which is not the same as *zero disparity*). Needs a static scene with a long, well-lit
sightline. `[hypothesis]`

Write-up: `modding-notes/2026-09-07-both-eyes-are-real-the-rock-scales-with-ipd-at-r2-0-9995.md`.
Evidence: `dev-archive/recon/2026-09-07-two-eye-wiggle-test/`. Harness:
`dev-archive/tools/alice_harness.py` (validated 7/7 on synthetic offsets before being trusted).

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

### ⛔️ CORRECTION 2026-09-09b — THERE IS NO "BIND ANY COMMAND TO ANY KEY" CHANNEL

**This supersedes the sub-section below it**, written earlier the same day. That section said
`AliceControlLayout.ini` "binds engine commands **directly to keys**, with no console in the path"
and treated it as a live channel. **Only one half of that is true.**

Three unused commands were bound to three free keys, in **both** copies of the layout file, with the
game closed: `BugItForGameController` on `G`, `StatUnitAndStatFPS` on `H`,
`ChangeCameraMode` on `J`. **All three did nothing**, and the rows were still in the file
afterwards — so the game had not rewritten it.

Two explanations fitted that equally (added rows ignored, or those three commands absent like the
console), so the discriminator was run: **`G` was rebound to `EnterFPSByRS`, the exact command that
works on `T`.**

```
before   : third-person
after G  : third-person      <- the command that works on T, on a new key
after T  : FIRST-PERSON      <- seconds later, same run
```

`[verified-live 2026-09-09, n=1 launch]`

**⇒ The game does not honour rows added to this file. The shipped bindings work; added ones do
not.** `T` → first person is real, and it is real because it *shipped* on `T` — not because the ini
is a channel we can write to.

⚠️ **The mechanism is NOT established** `[hypothesis]`: the layout may be cached in the profile or
save, compiled into the build, or read with a fixed row count. What is known is that the game *can*
rebind keys — its own CONFIGURATION → CONTROLS screen does, and the exe exports `ExecRebindKey` and
`ExecResetKeyBindings` (below). **Driving that UI is the untried next attempt**, and it is now the
only known route to the other commands named in the file.

⚠️ **And `BugItForGameController` was never actually executed** — the failure was in delivery, not
in the command. Whether it exists in this build is still open.

**What survives from the superseded section:** reading every input-related ini is still how `T` was
found, and that rule is right. What does not survive is the inference that anything *named* in such
a file can be reached by adding a row. The project's own standing rule already said as much — a
binding in a shipped ini is a lead, not evidence — and this is that rule biting one level up: the
*file* was evidence of what the game can do, not of what we can make it do.

### ⚠️ [SUPERSEDED 2026-09-09b — see the correction above] A SECOND COMMAND CHANNEL THAT IS NOT THE CONSOLE (2026-09-09, `/lm`)

2026-09-08 settled that the developer console is **not exposed in this retail build** — five
candidate causes excluded, `exec` never ran. That conclusion stands.

`AliceGame\Config\AliceControlLayout.ini` is a different file from `AliceInput.ini` (which holds
only axes and aliases) and the project had never opened it. Its `KeyBindArray1`/`KeyBindArray2` rows
name:

`EnterFPS`, `EnterFPSByRS`, `QuitFPS`, `ChangeCameraMode`, `ToggleCloseFollowCamera`, `TogglePOI`,
`ToggleGhost`, `togglephysicsmode`, `BugItForGameController`, `StatUnitAndStatFPS`,
`CheshireCatAppear`, `TriggerHysteria`, `ShowMenu`, `ShowJournalMenu`, `OpenSamepleMenu` (sic).

**`EnterFPSByRS` is proven live — it is on `T` and it works** (§6).
`[verified-live 2026-09-09, n=1 launch]` **Every other name in that list is a lead and nothing
more.** `[reported 2026-09-09]`


2026-09-08 settled that the developer console is **not exposed in this retail build** — five
candidate causes excluded, `exec` never ran. That conclusion stands. What it did **not** mean, and
was read as meaning for a day, is that the game's commands are unreachable.

`AliceGame\Config\AliceControlLayout.ini` binds engine commands **directly to keys**, with no
console in the path. It is a different file from `AliceInput.ini` (which holds only axes and
aliases) and the project had never opened it. Its `KeyBindArray1`/`KeyBindArray2` rows name:

`EnterFPS`, `EnterFPSByRS`, `QuitFPS`, `ChangeCameraMode`, `ToggleCloseFollowCamera`, `TogglePOI`,
`ToggleGhost`, `togglephysicsmode`, `BugItForGameController`, `StatUnitAndStatFPS`,
`CheshireCatAppear`, `TriggerHysteria`, `ShowMenu`, `ShowJournalMenu`, `OpenSamepleMenu` (sic).

**`EnterFPSByRS` is proven live — it is on `T` and it works** (§6).
`[verified-live 2026-09-09, n=1 launch]` **Every other name in that list is a lead and nothing
more** — a binding surviving in a shipped ini is not evidence the feature is live, which is this
project's own rule and cost it a session in 2026-09-08. `[reported 2026-09-09]`

Try `BugItForGameController` next: it reaches the same `BugIt` pose dump the dead console route was
after, and a working pose dump would make camera position, not just heading, measurable.

| command / cvar | effect | use |
|---|---|---|
| `FOV <10-150>` | native UE3 field-of-view command | confirmed via two independent Nexus FOV/ultrawide mods, both `BaseInput.ini`-bound |
| `DisableMouseSmoothing = 1` (config, `BaseInput.ini`-style) | removes mouse smoothing/negative acceleration and deadzones | per MadnessPatch — VR-critical, removes input-to-camera latency |
| F2 — **PATCH-ONLY, settled 2026-09-03** | opens the developer console | MadnessPatch 3.0.0+ adds `EnableConsole` bound to F2 as its own feature `[reported]`; **not stock** |
| Tilde `~` | UE3's stock default console key | per enslaved-vr's own shipping config — try if F2 turns out patch-only |
| `Show <group>`, `ToggleDebugCamera`, `Stat FPS`, `Stat D3D9RHI`, `ViewMode <mode>`, `SloMo` | standard UE3 exec commands | per enslaved-vr's own testing; `ToggleDebugCamera` especially worth trying for §6/§10 (free/debug camera) |

### The game's own settings surface (NEW 2026-09-03, `/pd`, static) `[inferred-static 2026-09-03]`

Read from the Steamless-unpacked exe's UTF-16 string table. This answers most of the queued
"what does the `Stereo3D` video-option actually do" without a launch.

- **`UAliceGameEngine` exposes 23 native script functions**, and they are the settings menu's whole
  vocabulary: `DoesSupportMSAA`, `GetNumOfSupportedResolutions`, `GetSupportedResolutions`,
  **`EnableStereo3D`**, `SetNvPhysXLevel`, `GetShowPostprocess`, `SetSoundVolume`, `ExecConfigData`,
  `ExecRebindKey`, `ExecResetKeyBindings`, `GetAliceKeys`/`SetAliceKeys`/`GetAliceKeyIndex`,
  `GetCompatCompositeIndex`, `GetCurrentDeviceID`/`SetCurrentDeviceID`,
  `SaveCheckpoint`/`LoadCheckpoint`/`FindCheckpointData`/`DeleteCheckpoints`,
  `HasStorageDeviceBeenRemoved`, `GetDestructionMaxChunkCount`, `LaunchAlice1`.
- **A complete family of 22 settings identifiers sits beside them, one per SETTING** (across the video, audio, gameplay and controls menus — not one per row of any single menu; a 23rd `Exec*` string, `ExecuteContextAction`, shares the prefix but is not a setting): `ExecAntiAlias`,
  `ExecAttackType`, `ExecControlLayout`, `ExecDifficulty`, `ExecDynamicShadows`, `ExecGamepadType`,
  `ExecGammaConfig`, `ExecGraphicsQuality`, `ExecInputAxis`, `ExecInputKey`, `ExecInvertY`,
  `ExecLowestDifficulty`, `ExecMotionBlur`, `ExecMouseSpeed`, `ExecMusicVolume`, `ExecPhysXLevel`,
  `ExecPostprocess`, `ExecScreenResolution`, `ExecSoundEffectVolume`, **`ExecStereo3D`**,
  `ExecSubtitles`, `ExecVoiceVolume`.
- The Scaleform menu inside `AliceGame.u` carries the same list in menu order (`Volume | Music |
  Voice | Subtitles | Gamma | GraphicsQuality | Resolution | AntiAlias | Stereo3D | Blur | Layout`)
  with matching accessors, so the three sources agree item for item.
- **⇒ The `Stereo3D` row is `ExecStereo3D`, routed through `ExecConfigData`, switching the native
  `EnableStereo3D`.** ⚠️ Held at two different strengths: `EnableStereo3D`'s **existence** is direct
  (the exe contains the UE3 native thunk name `intUAliceGameEngineexecEnableStereo3D`); the
  **routing through `ExecConfigData`** is an inference from the three lists agreeing, not a
  decompilation.
- **The engine gate is already open:** `AllowNvidiaStereo3d` is an `Engine.Engine` config property
  and is `True` in both `Engine/Config/BaseEngine.ini:193` (inside the vendor's own
  `; NVCHANGE_BEGIN: Jiayuan` markers) and the user config `AliceEngine.ini:168` `[measured 2026-09-03]`.
- **✅ CONFIRMED LIVE 2026-09-04 (`/lm`): the `3D STEREO` row IS present in Configuration → VIDEO and
  toggles OFF↔ON freely** `[verified-live 2026-09-04, n=1]` — not driver-hidden. So the native 3D
  Vision surface is exposed on this driver. Not CONFIRMed/engaged (that risks a renderer mode switch
  and is not the mod's route); whether pressing CONFIRM actually drives native 3D Vision on a modern
  driver is still untested. Interesting as corroboration, not a VR shortcut.
- ⚠️ **Not a shortcut to VR.** 3D Vision *Automatic* is a driver feature needing NVIDIA's stereo
  stack, deprecated on current drivers and normally gated on a 3D-capable display. What is useful to
  this project is the shader plumbing it left behind (`NvStereoEnabled`, `NvStereoFixTexture`, §6),
  which our proxy already reuses. **Unknown:** what `EnableStereo3D` does internally — the exe
  resolves NVAPI dynamically (`nvapi.dll`, `nvapi_QueryInterface`), but its call sites are not
  established.
- Evidence: `dev-archive/recon/2026-09-03-native-stereo3d-menu-path/`.

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used): title `Enter` → copyright `Enter` → PROFILE SELECT `Enter`
  (loads the highlighted profile) → main menu `Enter` on CONTINUE GAME → ~30 s load → gameplay
  (Whitechapel). `[verified-live 2026-09-04]` Full route/hazards: `ai-game-control-profiles/profiles/alice-madness-returns.json`.
- In-process input / camera drive method that worked: external `SendInput` scancodes via
  `flat-to-vr-RE-toolkit/tools/game-harness.py` for menus (`Enter`/arrows/`Esc`); the proxy's own
  **F-key hotkeys** (`GetAsyncKeyState`, polled each Present) are the stereo controls: **F9 stereo
  toggle, F10 eye swap, F11/F12 ipd, F7/F8 convergence** `[verified-live 2026-09-04 — F9 registered]`.
  Character/camera movement NOT exercised yet. **⚠️ Must be windowed** — `Fullscreen=True` in
  `Documents\My Games\Alice Madness Returns\AliceGame\Config\AliceEngine.ini` gives fullscreen-
  exclusive which BitBlt captures as black; set `Fullscreen=False` while the game is CLOSED (UE3
  rewrites config on exit). Res already 1280x720 there.
- Frame-capture method; where images land: `game-harness.py "Alice" shot out.png` (BitBlt, window
  focused first). Proxy evidence in `Binaries\Win32\alice_vr_proxy_log.txt`.
- **CAMERA CONTROL: FOUR ROUTES, AND THE IMPORT TABLE NOW SAYS WHICH ARE AVAILABLE** (folded from
  three `/gr` drops and one `/sr` drop of 2026-09-07; measured 2026-09-08). Camera control is the one
  automation capability still unproven on this game. `dev-archive/tools/alice_harness.py` implements
  routes 1 and 4; **none has been run.**

  | # | route | state |
  | --- | --- | --- |
  | 1 | **console `exec` file + `BugItGo`/`BugIt`** | implemented (`console`, `bugit`, `bugitgo`); `[reported]` that the commands exist |
  | 2 | keyboard `Axis aTurn` binding in `AliceInput.ini` | not implemented; `[reported]` / `[inferred-static]` |
  | 3 | virtual pad via an `xinput1_3.dll` proxy | **BUILT AND DEPLOYED 2026-09-08b, not run** |
  | 4 | `SendInput` `MOUSEEVENTF_MOVE` | implemented (`mouse`, `ballistics`) |

  **Route 1 is first because it is self-verifying.** UE3's `BugItGo <X> <Y> <Z> <Pitch> <Yaw> <Roll>`
  sets location *and rotation* absolutely and `BugIt` prints them back, so "did the camera move?"
  becomes a number rather than a screenshot judgement. Bind a key to `exec commands`, rewrite the
  extensionless `commands` file from Python between presses, and one keypress is a full
  Python-to-console channel. Needs `-freeconsole -allowcheats`. `[reported 2026-09-07]`
  WARNING: **where the exec file goes is NOT settled** - the drop said `Binaries\`, but the exe
  lives in `Binaries\Win32\` (its working directory), and UE3 builds are also documented reading exec
  files from `<Game>\Config`. The harness writes to **all four** candidates so one launch tests them
  together; all four exist on the dev PC `[verified-numerically 2026-09-08]`.

- **THE EXE'S IMPORT TABLE, READ FIRST-HAND, SETTLES TWO THINGS THE DROPS COULD ONLY INFER**
  `[verified-numerically 2026-09-08]` (`llvm-objdump -p AliceMadnessReturns.exe`):

  | imported | NOT imported |
  | --- | --- |
  | `DINPUT8.dll` -> `DirectInput8Create` | `RegisterRawInputDevices` |
  | `XINPUT1_3.dll` -> **ordinals 2 and 3, BY ORDINAL** | `GetRawInputData` |
  | `USER32`: `GetKeyState`, `GetMessageW`, `PeekMessageW` | `GetAsyncKeyState` |
  | `USER32`: `ClipCursor`, `GetClipCursor`, `GetCursorPos`, `SetCursorPos` | `GetKeyboardState` |

  - **Raw Input is excluded by construction.** The `/gr` drop *inferred* this from MadnessPatch
    hooking `ClipCursor`; the import table says it outright. So the mouse path is the Win32
    cursor/message path and an injected `MOUSEEVENTF_MOVE` has a plausible way in - **route 4 is
    worth trying**, where on a Raw-Input game it would not be.
  - **ROUTE 3 IS NOT BLOCKED, and the record saying otherwise is about a different mechanism.**
    Two drops warn the virtual-pad route "cannot be tested on the dev PC" because its **ViGEm bus**
    is broken. True of a ViGEm *virtual device* - and irrelevant here: Alice imports `XINPUT1_3.dll`
    **by ordinal, exactly as `prince-of-persia-2008-vr` does**, so an `xinput1_3.dll` **proxy**
    fabricates a pad *inside the process* and needs no ViGEm bus at all. That project's proxy exists,
    loads, and pins its ordinals in a `.def` for this same reason.
    WARNING: what is NOT established is whether Alice ever *polls* XInput - POP's proxy loaded fine
    and that game never called it. This is a route that is **available**, not one known to work.

- **ROUTE 3 IS BUILT AND DEPLOYED - AND IT IS AN INSTRUMENT FIRST** (2026-09-08b, `/pd`, no launch).
  `staging/alice-madness-returns-vr/proxy-xinput/`; deployed `xinput1_3.dll` md5 `26764e15...`,
  60,416 B, into `Binaries\Win32\`. Write-up:
  `modding-notes/2026-09-08b-the-xinput-proxy-is-an-instrument-first.md`.

  - **The open question is not "can we fabricate a pad" - it is whether Alice POLLS XInput.**
    Importing a DLL is not calling it, and there is a first-party precedent for the gap:
    `prince-of-persia-2008-vr` imports the same DLL the same way, its proxy loads cleanly, and that
    game was never once observed calling `XInputGetState`. So this counts ENTRIES into all three
    exports and prints a verdict on unload whether or not anything is injected:
    `NEVER CALLED` (route 3 is dead here) / `CALLED BUT NEVER FOR PAD 0` / `DECLINED` (our side) /
    `INJECTED`. `applied_pad` alone cannot tell the first from the third, and only the first is a
    fact about the game. `[compile-verified 2026-09-08]`
  - **Injection defaults OFF**, so deploying it changes no behaviour until a harness enables the
    shared block.
  - **Its shared block is deliberately NOT the sibling's.** POP uses `Local\pop2008_vr_input`;
    reusing that name would have made two running games share one block and each drive the other's
    pad - which would present as a game behaviour rather than a bug. Name, magic and every symbol
    are Alice's alone, and a test asserts they differ so a future copy-paste cannot undo it.
  - **The .def pins ordinals 2, 3 and 4.** Alice imports 2 and 3 BY ORDINAL, so a name-only export
    table would not resolve and the game would fail to start. The proxy imports no xinput itself
    (`KERNEL32` + UCRT only) so it cannot recurse; the real DLL is loaded by full system path with
    `xinput1_4.dll` as the ABI-compatible fallback `[verified-numerically 2026-09-08]`.
  - Host suite **43 checks, 0 failures** over the shipped `pad_inject.c`, covering the refusals
    rather than the happy path: disabled and bad-magic are bit-for-bit no-ops, a fabricated state
    starts CLEAN rather than ORing into whatever a failed call left, injection is additive over a
    real pad, and **the packet number advances on every apply** - a game comparing `dwPacketNumber`
    treats an unchanged one as stale and ignores the whole state, which would look exactly like
    "injection does not work here". `[verified-numerically 2026-09-08]`
  - **Reverting is deleting one file.** `xinput1_3.dll` is NEW in that folder - nothing was
    overwritten, so there is no backup to keep - and it shares no state with our `d3d9.dll`.

- Self-close (verified 2026-09-04): pause (`Esc`) → MAIN MENU (confirm YES) → main menu → EXIT GAME
  (confirm YES). Menus are a radial/vertical mix; verify each highlight before `Enter`
  (RESTART sits above MAIN MENU; the PROFILE screen has DELETE).

## 11. Dead ends & false leads (save future time)
- **Do not switch the vertex shear to the "one-element" per-eye edit**, however much cleaner it
  looks. It is already this code's constant term, and using it *alone* drops the convergence /
  off-axis term that 28,017 shipped pixel shaders implement themselves and cannot be changed. The
  two stages would then disagree by a constant: geometry moves, screen-space effects do not.
  `[verified-numerically 2026-09-04]`
- **A gated diagnostic can make a launch unreadable.** `vp_writes` and `p00` were counted only while
  stereo was enabled, and the summary was one-shot — so the 2026-09-04 launch reported zeros and
  needed an F9 double-toggle to say anything. Diagnostics that answer "is the premise true" must run
  when the feature is OFF, or the first launch cannot falsify anything.
- **✅ LIFTED 2026-09-03 — this dead end is CLEARED, and the method is recorded. Any static scan of `AliceMadnessReturns.exe`'s `.text`** — strings, immediates, xrefs. The section is encrypted at rest (entropy 8.00, entry point in `.bind`); a null result means nothing. **The wrapper is SteamStub v3.1, and unpacking a COPY with Steamless takes seconds and needs no launch — done 2026-09-03, `.text` entropy 8.00 → 6.71 and the NVAPI scan answered (§6).** Static scans of this exe ARE possible; just do them on an unpacked copy, and **always carry the `NvAPI_Initialize 0x0150E828` positive control**, because the packed file returns a clean zero for everything. The original text said: Needs a runtime dump first. `[measured 2026-09-02]`
- **Reading "no stereo strings in the exe" as "the integration lives in the engine layer"** (2026-09-01) — the premise is an artefact of that encryption. `[disproved 2026-09-02]`
- **Reading `SetActiveEye`'s absence from the NVAPI id table as "Automatic mode"** — the table is the linked SDK's fixed list, not the game's usage; `NvAPI_Initialize` is absent from it too. `[inferred-static 2026-09-02]`
- **Looking for `steam_api.dll` to confirm SteamStub** — it is absent from the import table, absent from the whole install, and there is **no "steam" string anywhere in the exe**, yet the binary *is* SteamStub-wrapped (§6). The game has no Steamworks *API* integration, only the DRM wrapper. **A negative here proves nothing; use the `0xC0DEC0DF` header magic instead.** `[measured 2026-09-03]`
- **Porting `alan-wake-vr`'s stereo edit into this project** — its matrices are `MATRIX_ROWS`, Alice's `ViewProjectionMatrix` is `MATRIX_COLUMNS`, so the two implementations are transposes. The Alan Wake form applied here mixes columns, corrupts `clip.w`, and still renders. `[verified-numerically 2026-09-03]` See §6.
- **Assuming `NvStereoFixTexture` is always sampler `s1`** — it is also `s3` (202), `s0` (46) and `s2` (10). `[verified-numerically 2026-09-02]`

## 12. Open risks toward the North Star
- **Framerate-dependent physics is a real, third-party-confirmed risk (external-research, 2026-08-25, from MadnessPatch's own fix list): hair/dress physics instability, projectile hitbox inconsistency, and general simulation behavior specifically at high framerates.** VR needs a high, stable frame rate (typically 90Hz+); this UE3-era game's physics were evidently tuned assuming a much lower framerate ceiling, and MadnessPatch had to fix exactly this class of bug. Running at VR framerates may re-expose the same issues — test explicitly once running at VR-target framerates, and treat MadnessPatch's own fix approach (understand, don't copy) as a reference point.
- **The strongest VR-feasibility signal of any project in this portfolio (external-research, 2026-08-25): vorpX delivers true Geometry 3D stereo AND working motion-controller emulation ("emulates a gamepad perfectly") for this exact game**, in both Immersive and Cinema modes. For comparison: Burnout Paradise's vorpX fails outright; Mad Max's vorpX works but third-person-only with no motion-controller mention; Prince of Persia has no vorpX profile at all. A third party has already solved, for this exact game, both the per-eye camera/projection override (§6's core problem) and mapping VR motion-controller input onto the game's own controls convincingly — neither reusable (closed-source), but both are strong existence proofs this engine doesn't resist full stereo + motion-input VR conversion. Treat vorpX's own default separation/convergence settings as a rough sanity-check reference once this project's own live camera work begins — not to copy, but to cross-check comfort. **Why vorpX does so well here specifically (this portfolio's own cross-engine library, external-research 2026-08-25): vorpX's Geometry 3D mode "works best on D3D9 games specifically"** — D3D9's older, simpler rendering model is exactly its best-case scenario (it works by rendering the scene twice, once per eye, at a real ~50% framerate cost). **A documented backup path exists if the from-scratch engine-level approach hits a wall**: `D3D9 game → dgVoodoo2 (wraps D3D9 onto D3D11) → geo-11 (free, D3D11-only stereo driver)`, optionally paired with a 3Dmigoto-class shader fix. Alice is unusually well-positioned for this specific backup, since it already has exactly the per-game shader-fix piece that route wants (the HelixMod fix, §6). **Scope reminder: both vorpX and geo-11 top out at seated/head-look experiences — no true 6DoF, no spatial motion-controller tracking** (vorpX's "motion controllers emulate a gamepad perfectly" is input-mapping, not hand presence) — this project's actual goal (full engine-level VR with real 6DoF) is a different category than either fallback, consistent with, not a substitute for, the primary plan.
