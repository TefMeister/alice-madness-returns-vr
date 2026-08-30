# This portfolio's own `enslaved-vr` project already has LIVE, first-hand UE3-on-D3D9 camera/injection findings — directly applicable here

**Status:** 🆕 new · **Priority:** very high — not a third-party source, but this user's own prior
work on a sibling project (`enslaved-vr`, Enslaved: Odyssey to the West) running the **exact same
engine generation and renderer** (Unreal Engine 3, Direct3D 9) as Alice: Madness Returns. This is
more valuable than any public documentation found so far, because it's live-verified against a real
UE3-on-D3D9 binary, not generic engine theory. Directly refines the companion "UE3 public camera
architecture" topic (previous sweep) and gives `ENGINE-DOSSIER.md` §4/§6/§7/§9 concrete, tested
starting points.

## Why this is worth cross-referencing

`enslaved-vr`'s `ENGINE-DOSSIER.md` and `modding-notes/00-status.md` (both public repos, read for
context per this research role's normal cross-project latitude) document three real working
sessions (2026-08-21) of static recon, a built-and-deployed D3D9 proxy, and an actual in-game
constant-register capture — the exact next steps Alice's own dossier is queued up for. Both games
share: 32-bit, D3D9-only (D3D10/11 code compiled in but config-gated off in Enslaved's case — worth
checking whether Alice's build has the same dead code path), PhysX-era middleware, Bink video, and a
UE3-standard `SetVertexShaderConstantF`-based constant mechanism (no D3D11 cbuffers).

## The single most important correction: the view-projection matrix is probably NOT a simple shared `c0` register

The companion public-docs topic (previous sweep) reported UE3's generic documentation places the
view-projection matrix in constant register `c0`. **Enslaved's actual live capture contradicts the
simple version of that**: analyzing a real gameplay frame's VS-constant histogram found **every 4×4
matrix upload was per-object/per-draw** (at `c0`, `c6`, `c10`, and `c231`+`c235` for a distinct
skinned-character vertex factory) — **no register held a constant value shared across all draws in
the frame**. The working conclusion: the camera is very likely **folded into a per-draw World ×
ViewProjection matrix**, not delivered as one separately-uploaded, once-per-frame shared VP register.
Enslaved's team built their proxy to auto-detect this directly — flag any register whose 4×4 value is
*identical across every draw in a frame* as a genuine shared-VP candidate; if nothing gets flagged,
the camera is baked per-object and needs to be decomposed/intercepted from the combined matrix
instead.

**This matters a great deal for Alice's own §6/§7 expectations**: don't assume `c0` will contain a
clean, isolated view-projection matrix just because public UE3 docs describe it that way — build (or
adapt) the same "flag shared-across-all-draws registers" detection technique before assuming which
register (or lack thereof) is the injection point, and be prepared for the harder "decompose a
per-object WVP" case if nothing comes back shared.

## Directly reusable technical blueprint

- **Proxy architecture, validated and deployed on a real UE3-D3D9 title**: a fail-safe `d3d9.dll`
  proxy forwarding all real exports, intercepting `Direct3DCreate9`, then patching
  `IDirect3D9::CreateDevice` (**vtable slot 16**), and on the returned device patching `Present`
  (**17**), `Reset` (**16**), and `SetVertexShaderConstantF` (**94**) — logging CreateDevice params, a
  per-frame register-upload histogram, and an optional watched-register 4×4 dump. This is
  essentially the exact next build Alice's own dossier's §4/§7 already calls for; Enslaved's is a
  proven reference implementation of the same idea (own logic, not to be copied verbatim, but the
  vtable slots and hook points are simply facts about D3D9's interface layout that apply identically
  here).
- **UE3's default console key is Tilde (`~`), not F2** — confirmed via `ConsoleKey=Tilde` /
  `TypeKey=Tab` still bound in Enslaved's shipping `BaseInput.ini`/`MonkeyInput.ini`. This is useful
  context for Alice's own open §3/§9 question ("F2 — unconfirmed if stock or patch-only"): UE3's
  *stock* default is Tilde, so if F2 turns out to be MadnessPatch-specific, trying Tilde on the
  unpatched game first is a reasonable, well-precedented first move.
- **A concrete, testable list of standard UE3 exec commands** beyond `FOV`: `Show <group>`,
  `ToggleDebugCamera`, `Stat FPS`, `Stat D3D9RHI`, `ViewMode <mode>`, `SloMo` — worth adding to
  Alice's §9 cheat sheet as candidates to try once console access is confirmed either way.
  `ToggleDebugCamera` in particular could be directly relevant to §6/§10 (a free/debug camera is
  exactly the kind of tool that helped unblock other fronts in this portfolio).
- **Two-altitude framing for owning the camera** (Enslaved's own dossier language, directly
  applicable strategy, not a specific finding): (1) **RHI level** — intercept
  `SetVertexShaderConstantF`/`SetTransform` in the D3D9 proxy and re-derive/replace the view-
  projection per eye; (2) **Engine level** — patch the UnrealScript/native camera path
  (`APlayerCamera::UpdateCamera` or a game-specific override) before the renderer ever consumes it.
  Worth deciding between these for Alice explicitly, the same way Enslaved's dossier frames it as an
  open decision.
- **UE3's authoritative runtime config often lives under `Documents\My Games\UnrealEngine3\<ProjectName>\Config\`**,
  not the in-install-directory INI files (which are just defaults) — a genuinely non-obvious
  methodological point confirmed by Enslaved's own testing. Worth checking for an
  `AliceGame`-equivalent per-user config path before assuming edits to the game-directory `.ini`
  files will actually take effect.
- **Custom viewport client class names are worth checking for**: Enslaved's own engine overrides
  camera/viewport behavior via `GameViewportClientClassName=NTEngine.NTReplayGameViewportClient` in
  its engine INI. Checking Alice's equivalent config key (likely under an `AliceGame\Config\` INI) for
  a custom (non-default) `GameViewportClientClassName` is a cheap, config-file-only way to discover
  whether Spicy Horse layered custom camera/viewport logic on top of stock UE3 — directly relevant
  given the companion "native stereo3D" topic already suggests real custom camera work was done here.
- **EasyHook32.dll ships inside Enslaved's own install** — the game's own runtime bundles a hooking
  framework, suggesting this UE3 era/toolchain doesn't inherently resist injection. Worth a quick
  check of whether Alice's install ships anything comparable (not expected, but cheap to confirm).

## Concrete next step

Before building Alice's own D3D9 proxy's constant-capture logic from scratch, adapt Enslaved's
"flag any register that's identical across every draw in the frame" shared-VP detection technique
directly — it's the fastest way to get a real go/no-go answer for whether Alice's camera delivery
matches the simple shared-`c0` public-docs model or the more complex per-object-WVP pattern Enslaved
actually found. Also worth checking Alice's per-user config path and any custom
`GameViewportClientClassName` before assuming stock UE3 camera behavior.

## Sources

- `enslaved-vr-engine-research/ENGINE-DOSSIER.md` (this user's own portfolio, `TefMeister/enslaved-vr-engine-research`)
- `enslaved-vr-modding-notes/00-status.md` (this user's own portfolio, `TefMeister/enslaved-vr-modding-notes`)
