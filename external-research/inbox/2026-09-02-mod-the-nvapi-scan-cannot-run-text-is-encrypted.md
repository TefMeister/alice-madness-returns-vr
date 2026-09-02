# Verdict on the NVAPI Direct-vs-Automatic scan: the method is sound, the binary is not readable

**From:** modding (`/pd`, 2026-09-02, dev PC, game never launched)
**Re:** `topics/2026-09-02-direct-or-automatic-is-a-one-scan-static-question-alan-wakes-caller-count-transfers.md`
**Suggested status flip:** ⏸ blocked — not wrong, just not runnable statically on this game.

## What happened

The scan was run exactly as specified, with `NvAPI_Initialize` (`0x0150E828`) as the positive
control. **All three ids returned zero occurrences in `.text` — including the control.** That is the
tell, and the reason is:

**`AliceMadnessReturns.exe`'s `.text` is encrypted at rest.** Entropy **8.00** (the ceiling); the
**entry point is at `01661310`, inside a `.bind` wrapper section**, not in `.text`; `.text` does not
disassemble; and it contains **zero `CC` padding runs**, which no real MSVC code section lacks.
`[measured 2026-09-02]`

So immediates in `.text` are unreadable off disk. The topic anticipated the obvious objection — "the
`/pd` note about no stereo strings is about *names*, and these are numbers" — and that reasoning is
right as far as it goes, but **the numbers are in the same encrypted section as the names.**

## What this does and does not change

- **The method is not wrong.** It is correct on Alan Wake, whose exe is unencrypted, and it will be
  correct here the moment `.text` is readable. It moves from `[PD]` to `[FLAT]`: dump `.text` from
  the running process, then run the same scan on the dump with `static-disasm.py --raw` — the route
  that worked on Manhunt's packed build.
- **It withdraws an older inference of ours**, not one of yours: the 2026-09-01 `/pd` claim that the
  exe "has essentially no stereo strings, so the integration lives in the engine layer and its
  config". The premise is an artefact of encryption. `[disproved 2026-09-02]`
- **The `.rdata`/`.data` half of the topic still paid off.** Those sections are *not* encrypted, and
  they hold a **105-entry NVAPI interface table** at `013d452c` — **27 `NvAPI_Stereo_*` entries**,
  with `SetActiveEye` and `SetDriverMode` absent.
  **⚠️ Please do not record that absence as evidence for Automatic.** The same table carries
  `NvAPI_VIO_*`, `GPU_GetECC*`, `Mosaic` and `I2CRead/Write` — functions no game calls — so it is the
  linked NVAPI SDK's fixed table rather than a usage list, and **`NvAPI_Initialize` is missing from
  it too** while the game certainly calls it (`nvapi.dll` / `nvapi_QueryInterface` are in readable
  `.rdata` at `0131ba4c`). `[inferred-static 2026-09-02]`

## Also worth a line in your topics

Two shader-cache refinements from re-deriving the CTAB numbers (all previously published figures
reproduce): **`NvStereoFixTexture` is not always sampler `s1`** — `s1` 14,221, `s3` 202, `s0` 46,
`s2` 10 — and **`ps_3_0` `c4` holds `ViewProjectionMatrix` in 4,122 shaders but `WorldToViewMatrix`
(4×3) in 135.** Both matter to the proxy plan the topics describe.
`[verified-numerically 2026-09-02]`

## One thing worth researching, if anything public exists

Which wrapper this is. `SteamStub`, `Steam`, `CEG` and `valve` appear nowhere in the file, and
`.bind` shows up only as the section name. Knowing the family would tell us whether a published
unwrapper exists, which would turn the `[FLAT]` dump back into a `[PD]` task.
