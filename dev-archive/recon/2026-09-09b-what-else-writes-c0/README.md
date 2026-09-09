# 2026-09-09b — what else writes c0?

`/pd` session, dev PC. **The game was not launched and nothing here was run
against it.** Everything came from reading two files the game ships and from a
host test that runs against matrices built in the test itself.

| file | what it is |
| --- | --- |
| `c0-constant-census.txt` | output of `dev-archive/tools/c0_constant_census.py` — what every shipped shader binds to register c0, in **both** shader caches |
| `stereo-test-output.txt` | the full `stereo_ue3.c` suite including the 9 new classifier checks, all passing |

## The two findings

1. **No shipped shader binds anything but `ViewProjectionMatrix` to vertex c0**
   in the material cache (2,431 of 2,807; the other 376 bind nothing there).
   `[measured 2026-09-09]`
2. ⭐ **The global cache has exactly one vertex shader binding a non-view
   constant at c0: `SampleOffsets`, an 8-register array, with no other constants
   at all** — a UE3 filter/blur pass. The proxy intercepts on `count >= 4`, so
   such a write is indistinguishable from a 4×4 there. `[measured 2026-09-09]`

## What is NOT established

That the once-per-frame non-camera write **is** that blur upload. It is a
`[hypothesis]` that fits every measured property, produced from what the game
ships rather than from what it does. The live `c0dump` — which now prints
`Vector4fCount` — settles it in one launch: `count == 8` confirms it,
`count == 4` kills it.

⚠️ Earlier passes on this project read only `RefShaderCache`. `GlobalShaderCache`
holds the post-process and fullscreen shaders — the passes that run last in a
frame — and had never been examined.

## Reproducing

```
python dev-archive/tools/c0_constant_census.py
```

Reads game files, writes none, and extracts no game content — only constant
names and register indices, which are interface metadata.
