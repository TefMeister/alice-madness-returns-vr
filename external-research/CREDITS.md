# Credits & Attribution

This project is a reverse-engineering and modding effort built on the public
research, tools, and documentation of many people who came before us. None of
this would be possible without their work. We list every source we've drawn
on below — including work that helped only as inspiration — by name or
handle, as accurately as we could verify it.

## The game itself

This mod modifies, at runtime, the original **Alice: Madness Returns** (2011)
by **Spicy Horse Games**, published by **Electronic Arts**, built on **Unreal
Engine 3** by **Epic Games**. The game, its engine, and all of its assets
belong to their respective owners, and the game is the entire reason this
project exists. **No game files, code, or assets are distributed in any of
this project's repositories** — only code, notes, and tools we wrote
ourselves.

## Prior art, tools, and research this repo draws on

| Source / Work | Creator(s) | Link |
|---|---|---|
| vorpX Alice: Madness Returns compatibility reports & Geometry VR list | vorpX (Ralf Herrmann) & forum community | https://www.vorpx.com/forums/topic/a-masterpiece-is-back-alice-madness-returns/ |
| MadnessPatch | Wemino | https://github.com/Wemino/MadnessPatch |
| PC Gamer coverage of MadnessPatch | PC Gamer | https://www.pcgamer.com/games/action/the-sequel-to-one-of-my-favorite-3d-platformers-always-had-a-janky-pc-port-but-a-huge-fanmade-patch-just-dropped-in-hopes-to-fix-it/ |
| "alice32-9-ultrawide" / "UltraWide And 60FPS Fix" mods | Nexus Mods creators | https://www.nexusmods.com/alicemadnessreturns/mods/53 |
| DRM history reporting (EA Cuckoo removal) | ResetEra community | https://www.resetera.com/threads/the-relisted-steam-version-of-alice-madness-returns-recently-got-updated-to-work-without-ea-authentication-drm.548510/ |
| PCGamingWiki (Alice: Madness Returns technical notes) | PCGamingWiki community | https://www.pcgamingwiki.com/wiki/Alice:_Madness_Returns |
| Helix Mod: Alice: Madness Returns | Chiz, Helix Mod community | https://helixmod.blogspot.com/2012/02/alice-madness-returns-written-by-chiz.html |
| UDK Camera Technical Guide | Epic Games | https://docs.unrealengine.com/udk/Three/CameraTechnicalGuide.html |
| UE3:Camera (UDK) wiki page | BeyondUnreal wiki community | https://wiki.beyondunreal.com/UE3:Camera_(UDK) |
| Epic Developer Community forums (view/projection matrix discussion) | Epic Games forum community | https://forums.unrealengine.com/t/bound-shader-view-matrix/451510 |
| enslaved-vr project (this portfolio's own Enslaved: Odyssey to the West VR effort) | Project owner + Claude, this portfolio | https://github.com/TefMeister/enslaved-vr/tree/main/engine-research |
| flat-to-vr-cross-engine-research (this portfolio's own cross-engine library) | Project owner + Claude, this portfolio | https://github.com/TefMeister/flat-to-vr-cross-engine-research |
| NVIDIA 3D Vision developer documentation — "Using nvstereo.h" (the `StereoParmsTexture` channel layout and update cadence) and the Automatic background/issues pages | NVIDIA Corporation | https://archive.docs.nvidia.com/gameworks/content/technologies/desktop/nv3dva_using_nvstereoh.htm |
| Unreal Developer Network — "Unreal Engine 3 and NVIDIA 3D Vision Direct" (`AllowNvidiaStereo3d`, fullscreen-only restriction) | Epic Games | https://docs.unrealengine.com/udk/Three/ThreeDVision.html |
| 3Dmigoto (its published `nvstereo.h` copy is what shows the header is freely available; nothing taken from it) | bo3b and 3Dmigoto contributors | https://github.com/bo3b/3Dmigoto |
| NVAPI public repository — `nvapi_interface.h` id table and `nvapi_lite_stereo.h` (Direct-mode contract) | NVIDIA Corporation | https://github.com/NVIDIA/nvapi |
| 3D-Vision-Direct sample README (what a Direct-mode app does; nothing taken) | bo3b | https://github.com/bo3b/3D-Vision-Direct |
| "Stereo 3d refuses to work" — what the in-game toggle does | Steam Community discussion participants | https://steamcommunity.com/app/19680/discussions/0/828925216495800901/ |
| MadnessPatch release notes (`EnableConsole` on F2, 3.x changes) | Wemino | https://github.com/Wemino/MadnessPatch/releases |
| "Epic Brings NVIDIA 3D Vision Support to Unreal Engine 3" (GDC 2010 press release) | NVIDIA Corporation | https://nvidianews.nvidia.com/_gallery/download_pdf/54481935f6091d2735000245/ |
| Steamless — SteamStub DRM unpacker (supported variants, purpose, licence; nothing taken from it) | atom0s | https://github.com/atom0s/Steamless |
| Steamstub-v3-Unpacker (v3 unpack/rebuild behaviour and options; nothing taken from it) | GHFear | https://github.com/GHFear/Steamstub-v3-Unpacker |
| "Cube World Reversing — Unpack the game" (the `.bind` section, entry-point redirection and runtime `.text` decryption, explained on a different game) | Adam Hlt | https://adamhlt.com/cube-world-reversing-unpack-the-game/ |

Development on this project is AI-assisted: much of the research, code, and
documentation was produced with **Claude (Anthropic)** (https://claude.com)
working alongside the project owner.

## Missing from this list?

If you — or someone whose work you know — contributed to, influenced, or
even just inspired anything used in this project and you aren't credited
here, please **open a GitHub issue on this repo** and we'll correct it as
soon as possible. We would much rather over-credit than leave anyone out.

## Respecting creators

This project exists because other people generously shared their
reverse-engineering research, tools, and modding know-how in public — we've
tried to credit every one of them by name or handle above, as accurately as
we could verify. If you are the creator or rightful owner of anything
credited or used here and you'd rather your work not be referenced in this
repo, or you want specific content removed or no longer used by the mod,
please tell us: **open a GitHub issue on this repo**. We'll act on that
request promptly — no argument, no delay — and we'll find another way to get
the job done that doesn't rely on your material. This is your work; we're
just grateful to have learned from it.
