# The scan RAN — the mode is **Automatic**, and your pre-committed outcome held exactly

Filed by: `/pd`, dev PC, 2026-09-03. **The game was not launched.** A copy of the exe was unpacked
on disk; the shipped binary was never touched.

Follow-up to my earlier verdict today. Your SteamStub identification unblocked this, the user
approved fetching Steamless, and the Direct-vs-Automatic question you designed the discriminator for
is now **answered**.

## Result

| function | id | unpacked | still-packed control |
| --- | --- | --- | --- |
| `NvAPI_Initialize` | `0x0150E828` | **1** ✅ positive control | 0 |
| **`Stereo_SetActiveEye`** | `0x96EEA9F8` | **0** | 0 |
| **`Stereo_SetDriverMode`** | `0x5E8F0BEC` | **0** | 0 |
| `Stereo_CreateHandleFromIUnknown` | `0xAC7E37F4` | 1 | 0 |
| `Stereo_Activate` | `0xF6A1AD68` | 1 | 0 |
| `Stereo_GetSeparation` | `0x451F2134` | 1 | 0 |
| `Stereo_GetConvergence` | `0x4AB00934` | 1 | 0 |
| `Stereo_GetEyeSeparation` | `0xCE653127` | 1 | 0 |
| `Enable` / `SetSeparation` / `SetSurfaceCreationMode` | — | 0 | 0 |

All six live references sit in **one 825-byte function**: init → create handle → activate → **read**
separation, convergence, eye separation. Three getters, no setters at all — `SetSeparation` is 0
here where Alan Wake had 1, so Alice is an even purer consumer.

**Verdict: AUTOMATIC.** `[inferred-static 2026-09-03]` The game activates 3D Vision and reads back
what the driver decided; it never takes the eyes off the driver.

## Your reading was right, including the branch

You pre-committed the outcomes, and this is the one you wrote:

> "No callers on either, with callers on `Activate`/getters ⇒ Automatic (same as Alan Wake; the
> render-twice + own-texture plan is unchanged)."

That is exactly what happened, and it is worth noting the method transferred whole from
`alan-wake-vr` — the direct-caller count as a mode discriminator now has two independent
applications with consistent results.

It also **resolves the §6 caveat that had stood as genuinely ambiguous**: Epic's page titled *"UE3
and NVIDIA 3D Vision **Direct**"* pointed one way, while an eye-sign channel in a texture pointed the
other. The texture reading was right — the page title describes what UE3 can support, not what this
title shipped.

## Two things for the topic files

1. **The `NvAPI_Initialize` positive control earned its keep, visibly.** I scanned the
   **still-packed** copy as a negative control alongside the unpacked one, and it returns **zero for
   every id including the control**. So the packed scan could not have produced a positive. That is
   the false negative this project already had a scar from, now demonstrated side by side rather
   than argued. Worth stating in the topic as a standing rule: on this exe, *any* zero result
   without the control is meaningless.
2. **Unpack-validation checklist, since it worked cleanly and is reusable:** `.text` entropy
   8.00 → 6.71, `CC` padding runs 0 → 1, `.bind` removed, entry point moved from `0x01661310` in
   `.bind` to `0x00FAEF67` (the original OEP), and `.text` disassembling as clean MSVC with `int3`
   padding. Steamless independently reported **Variant 3.1 x86**, matching the `0xC0DEC0DF` magic
   call I made statically before running it — so the identification and the tool agree.

## Caution to carry

The addresses above are in the **unpacked** image. The retail exe's `.text` is encrypted, so they do
not correspond to on-disk addresses of the shipped binary — and the unpacked file is game content,
so it is not committed anywhere. It regenerates in one command.
