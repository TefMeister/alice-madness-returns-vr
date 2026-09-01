# 2026-09-01 (b) — The real toggle is a `Stereo3D` video option; the INI key I leaned on looks inert

**Supersedes:** `2026-09-01-nvidia-stereo-3d-is-integrated-and-on-by-default.md` — which treated
`AllowNvidiaStereo3d=True` as *the mechanism*. It probably is not. The finding below is better
evidence and points somewhere more useful.

**Date:** 2026-09-01, dev machine, `/pd` pass. **The game was never launched.** Static analysis of
shipped files; nothing modified, nothing run.

---

## 1. There is a `Stereo3D` entry in the game's own video options

`AliceGame/CookedPC/AliceGame.u` — the game's own UnrealScript package — contains the string
`Stereo3D`, and it appears **four times, each in the middle of a run of video-settings names**:

```
… setAntiAlias · Stereo3D · Mo… · Blur · PostProcess · DynamicShadow · PhysXLevel …
… Gamma · GraphicsQuality · Resolution · AntiAlias · Stereo3D · … · Blur · Layout …
```

with `buttons` nearby in one of them. **This is a graphics-options screen, and `Stereo3D` is one of
its entries.** `[inferred-static 2026-09-01, n=4 occurrences]` — the identification rests on the
company it keeps, which is about as strong as string-adjacency evidence gets: every neighbour is an
unambiguous video setting.

That answers the queued question — *"check for a native in-game 'Stereo 3D' toggle before any
from-scratch shader-reflection work"* — with a **yes**, and locates it in the options UI rather than
in a config file.

## 2. ⚠️ Correcting myself: `AllowNvidiaStereo3d` appears to be inert

This morning I found `AllowNvidiaStereo3d=True` in `Engine/Config/BaseEngine.ini`, wrapped in
NVIDIA's `NVCHANGE_BEGIN/END` markers, and described it as the mechanism behind the community
findings. **That reading is probably wrong.**

Searched for the name `AllowNvidiaStereo3d`:

* **`AliceMadnessReturns.exe`** — absent.
* **Every `.u` / `.upk` in `AliceGame/CookedPC/`** — absent.
* A separate recursive scan of the whole `AliceGame/` tree — absent.

In UE3 a config key of that form is a `UProperty` name, which lives in a package's name table; read
natively instead, the literal would sit in the executable. **It is in neither.** So nothing in the
shipped game appears to read that key: the NVIDIA branch's INI default survived into the build while
its consumer did not.

**And the search is trustworthy here**, which is the part I checked rather than assumed: these
packages are **not compressed** — magic `0x9E2A83C1` with payload entropy **5.25–6.91 bits/byte**
(compressed data sits above ~7.5). A raw byte search can therefore see inside them. Had they been
compressed, "absent" would have meant nothing at all.

That check exists because of a mistake made earlier the same day on Alan Wake, where a truncated
search was published as a complete result. **An "absent" result is only evidence of absence once you
have shown the search could have found the thing.**

## 3. Alice loads NVAPI dynamically, exactly like Alan Wake

`AliceMadnessReturns.exe` contains `nvapi.dll` and `nvapi_QueryInterface` as strings, sitting
directly beside `d3d10.dll` and `dxgi.dll` — UE3's standard "load these at runtime if present"
block. There is **no static import** of NVAPI.

Same consequence as Alan Wake: the stereo path's dependency is **interceptable from a proxy**, so
"3D Vision was discontinued" does not by itself make it unreachable.

## 4. What this means for the project

The picture is now coherent and considerably better than this morning's:

* A **`Stereo3D` option in the game's own menu** (not a config flag we have to guess at).
* An **NVAPI dependency loaded dynamically**, so its absence is survivable and its answers are
  forgeable.
* A community fix that only had to correct **UI** depth — consistent with the world already
  rendering correctly in stereo when the option is on.

### Still not established

* That the option still functions on modern hardware, or what it does when NVAPI is unavailable.
* Whether the eye offset happens in the game's shaders (usable) or in the driver (not usable). This
  is the crux, and it is the same open question as Alan Wake's — worth answering once for both.
* Where `Stereo3D` sits in the menu, or whether it is hidden when no stereo driver is detected.

### Next

**No launch needed:** find the shader constant or render path the `Stereo3D` setting drives.
`Engine.u`'s name table is the place to look.

**Checked and ruled out already:** Alice does **not** ship its shader sources. Its `Engine/` folder
holds only `Config/`, `Localization/` and `Splash/` — no `Shaders/`. So the trick that settled
Enslaved's camera question outright (that project ships `Engine/Shaders/*.usf`) is **not available
here**, and Alice's register conventions cannot be read off the same way. Since both are UE3 D3D9,
Enslaved's mapping (`c0`-`c3` view-projection, `c4` camera position, `c5` PreViewTranslation) is a
reasonable starting *hypothesis* for Alice — but it is engine-version dependent and must be
confirmed against this build, not assumed from a sibling.

**On a live session:** open the video options and look for `Stereo3D`. That is now a specific thing
to look for in a specific screen, rather than "check for a toggle".

🤖 Static analysis of shipped files only. The game was not launched, nothing was modified, and no
game content was copied here.
