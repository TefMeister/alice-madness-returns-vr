# 3D Vision Automatic on a current driver: what it takes to light the game's own `Stereo3D` row — and why that is not a VR route

**Date:** 2026-09-03 · **Status:** 🆕 new · **Priority:** medium · **Answers:** the one research
target the modding side offered in `inbox/2026-09-03b-mod-the-stereo3d-toggle-is-answered-statically.md`
— *"whether NVIDIA 3D Vision Automatic is reachable at all on a current driver, and under what
conditions"*. This decides the remaining `[FLAT]` half of that board row: whether the game's native
stereo can even switch on here.

⚠️ **Framing first, as the modding side asked.** Whatever 3D Vision does, it drives a 3D *display*,
not a headset. Its value to this project is the shader plumbing it left behind (`NvStereoFixTexture`,
`NvStereoEnabled`, the driver-published separation/convergence), which our proxy already reuses.
Nothing below is a shortcut to VR. It is a platform fact about *observing the game's own stereo* on
this machine, useful as a reference picture and as a check that the shader plumbing is live.

## The short answer

**Reachable, but only with an old driver or a driver-side workaround, and only with something to
display it on.** NVIDIA discontinued 3D Vision in April 2019; on a stock current driver the game's
`Stereo3D` row can be ticked but nothing stereoscopic will happen. `[reported]`

## What the sources say, and how well

| Claim | Source | Tag |
| --- | --- | --- |
| NVIDIA announced on **2019-04-11** that driver support for 3D Vision would end; **425.31 is the last driver that includes it** | Wikipedia, citing NVIDIA's support-plan notice (the NVIDIA page itself returned 403 to an automated fetch) | `[reported]` |
| Drivers **up to 452.06** still ran DX11 3D Vision via a workaround; from the RTX 30-series release driver (456.38, Oct 2020) NVIDIA "partially removed" stereoscopic 3D, and **DX11** games lost it | 3D Fix Manager page (Pauldusler, updated 2024-03-23); HelixVision discussion (Bo3b, 2019-09-02) | `[reported]` |
| **DirectX 9 games "remain fully compatible to stereoscopic 3D and run on latest graphics cards"** — i.e. the DX9 3D Vision path was *not* what NVIDIA removed in 2020 | 3D Fix Manager page | `[reported]` — one source; **the single most relevant claim for Alice (a DX9 game) and unconfirmed here** |
| **geo-11** (davegl1234, June 2022) is a full replacement stereo driver for **DX11 only**; DX9 games reach it via **dgVoodoo2** translation, "about half" of them successfully | Helix Mod "Announcing: New geo-11 3D driver"; Helix Mod Tron 2.0 geo-11 post; 3D Fix Manager page | `[reported]` |
| Hardware: 3D Vision needs a **120 Hz 3D Vision-ready display + IR emitter/glasses**, or a 3DTV Play display, **or** anaglyph glasses in "3D Vision **Discover**" mode on any NVIDIA card | Wikipedia; 3D Fix Manager requirements; HelixVision (uses Discover mode to avoid the hardware) | `[reported]` |
| Getting 425.31 onto Windows 10 1903+ generally means removing the DCH driver with DDU and installing 425.31 offline, or a driver-modding tool (3D Fix Manager's Drivers tab, the community "3D Vision Driver Changer") | HelixVision discussion; MTBS3D thread titles (MTBS3D itself returned 403) | `[reported]` |

## What this means for the board row

- **The `[FLAT]` half — "does the Stereo3D row light up on this machine?" — has a predictable
  answer on a current driver: no.** Ticking it will, at most, run the game's `EnableStereo3D` path
  against a driver that no longer has the feature. That is still a *useful* run: with the proxy's
  logging on, it shows whether the game calls `NvAPI_Stereo_Activate` and whether the driver returns
  an error — but expect a flat picture.
- **Seeing the game's own stereo would need either** (a) driver 425.31 installed — a machine-wide
  change and not something to do casually on the VR test machine, since it predates every current VR
  runtime's tested driver range; or (b) a driver-modding tool; or (c) the dgVoodoo2 → DX11 → geo-11
  route, which this project's own 2026-08-25 cross-engine topic already lists as the backup
  *3D-fix* path. None of these is on the project's critical path, because the plan does not depend
  on the driver's stereo — it reuses the shader plumbing with our own texture.
- **If the DX9 claim holds** (3D Vision still active for DX9 on current drivers), the row *could*
  light on this machine with only Discover-mode anaglyph glasses — the cheapest possible reference
  picture of the developers' own stereo. Worth one attempt precisely because it is cheap; not worth
  a driver downgrade.

## Cross-project

Alan Wake (DX9, Automatic, same `nvstereo.h` consumer pattern, live Ctrl+F3/F4 separation hotkeys)
sits in exactly the same position; a pointer row is in that project's INDEX. Enslaved (UE3/D3D9) and
any other 3D-Vision-era title on the account inherit the same facts, so the platform half went to the
cross-engine library's inbox for `/sr`.

## Sources

- https://en.wikipedia.org/wiki/Nvidia_3D_Vision — discontinuation announcement (2019-04-11), 425.31 as last supporting driver, hardware requirements
- https://helixmod.blogspot.com/2017/05/3d-fix-manager.html — Pauldusler's 3D Fix Manager: 425.31 / 452.06 driver facts, the October 2020 DX11 removal, DX9 "fully compatible" statement, geo-11, Discover-mode alternative
- https://helixmod.blogspot.com/2022/06/announcing-new-geo-11-3d-driver.html — geo-11 announcement (davegl1234)
- https://helixmod.blogspot.com/2022/08/tron-20-geo-11-3d-fix-dx9-dx11-dgvoodoo2.html — the dgVoodoo2 DX9→DX11→geo-11 pattern in practice
- https://steamcommunity.com/app/1127310/discussions/0/1635291505036080879/ — Bo3b's HelixVision driver notes (425.31 recommended, 452.06 ceiling, on-the-fly driver modding, Discover mode, DDU route)
- https://nvidia.custhelp.com/app/answers/detail/a_id/4781/ — NVIDIA's own support-plan notice; **403 to automated fetch, cited via Wikipedia only**
- https://www.mtbs3d.com/forum/viewtopic.php?t=23703 — "Install 3D-Vision for Driver 442.50 (and later)"; **403 to automated fetch, title only**
