# The `.bind` section names the wrapper: it is Steam's own DRM stub, and public unpackers restore `.text`

**Date:** 2026-09-03 · **Status:** 🆕 new · **Answers:** the closing question of
`external-research/inbox/2026-09-02-mod-the-nvapi-scan-cannot-run-text-is-encrypted.md`

## The question this answers

The modding side ran the NVAPI Direct-vs-Automatic scan exactly as
[the 2026-09-02 topic](2026-09-02-direct-or-automatic-is-a-one-scan-static-question-alan-wakes-caller-count-transfers.md)
specified, with `NvAPI_Initialize` (`0x0150E828`) as the positive control, and **all three ids
returned zero occurrences in `.text` — including the control.** The reason was measured on the file
itself: `AliceMadnessReturns.exe`'s `.text` has entropy **8.00**, does not disassemble, contains
**zero `CC` padding runs**, and the **entry point sits at `01661310`, inside a section named
`.bind`** rather than in `.text`. `[measured 2026-09-02]`

The drop closed by asking the one thing that would unblock it:

> Which wrapper this is. `SteamStub`, `Steam`, `CEG` and `valve` appear nowhere in the file, and
> `.bind` shows up only as the section name. Knowing the family would tell us whether a published
> unwrapper exists, which would turn the `[FLAT]` dump back into a `[PD]` task.

**It is SteamStub — Valve's own DRM wrapper, applied at upload time.** The four facts above are not
merely consistent with it; taken together they are its published detection signature.

## Why `.bind` is the identification, and why the absent strings are not a counter-argument

The `.bind` section is **the** documented SteamStub tell. It is a section appended to the end of the
executable holding the stub code, and the PE entry point is rewritten to start inside it instead of
at the program's real entry — which is exactly the layout measured here (entry at `01661310`, in
`.bind`, not in `.text`). Public unpackers use the section's presence as the detection test, and
then fingerprint byte patterns *within* the `.bind` code to decide which SteamStub version it is.
`[reported 2026-09-03]`

The original code section is **encrypted at rest and decrypted (and decompressed) into memory by
the stub at startup**, before control is handed to the real entry point. That is precisely the
signature the modding side measured — 8.00 entropy, no disassembly, no `CC` padding — and it is why
the positive control failed: `NvAPI_Initialize`'s id is in the file, but not in plaintext.
`[reported 2026-09-03]`

**The missing strings prove nothing either way.** `SteamStub` is a name the RE community gave the
wrapper, not a string Valve ships; `CEG` is a *different* Valve product (Custom Executable
Generation, per-user compiled binaries) and its absence is expected on a normally-wrapped build.
The one string that would be diagnostic — `steam_api.dll` in the import table — was not part of the
check that was run, and is worth confirming as a second witness.

## What this unlocks — the scan goes back to `[PD]`

Two public, open-source unpackers exist for this exact wrapper. Both are legitimate
reverse-engineering tools distributed on GitHub, and both are explicit that they are for software
you own:

| Tool | Author | Coverage | Licence |
| --- | --- | --- | --- |
| [Steamless](https://github.com/atom0s/Steamless) | atom0s | SteamStub variants 1, 2 (v2.0.0 / v2.0.1, 32-bit), 3 (v3.0.0 / v3.0.1 / v3.1.0 / v3.1.2, 32- and 64-bit) | CC BY-NC-ND 4.0 |
| [Steamstub-v3-Unpacker](https://github.com/GHFear/Steamstub-v3-Unpacker) | GHFear | SteamStub v3; "unpacks and rebuilds original windows executable", optional keep-`.bind`, checksum fix, certificate-table removal | CC BY-NC 4.0 |

Steamless's stated purpose is to "remove the Steam DRM and decrypt the `.text` section", producing a
PE suitable for static analysis. `AliceMadnessReturns.exe` is 32-bit (the addresses in every note on
this project are 32-bit), which is inside variant 1–3 coverage. `[reported 2026-09-03]`

So the route is: run the unpacker over a **copy** of the exe, confirm `.text` now disassembles and
carries `CC` padding runs, **re-run the positive control first** (`NvAPI_Initialize` `0x0150E828`
must now be found), and only then read the Direct-vs-Automatic discriminators
(`NvAPI_Stereo_SetActiveEye` `0x96EEA9F8`, `NvAPI_Stereo_SetDriverMode` `0x5E8F0BEC`). That is all
static work on a file already on disk — **`[FLAT]` → `[PD]`**.

## ⚠️ Two cautions worth having before anyone tries it

1. **The unpacked exe is for reading, not for running.** Public write-ups of this exact workflow
   note that an unpacked binary generally will not launch standalone, because the game still expects
   the Steam API environment the stub set up. That is fine for our purpose — we want a readable
   `.text`, not a second way to start the game — but it means "it doesn't run" is an expected
   outcome, not a failed unpack. Never overwrite the shipped exe; work on a copy.
   `[reported 2026-09-03]`
2. **The runtime-dump route stays valid as the fallback**, and is the same one that worked on
   Manhunt's packed build: the stub decrypts `.text` in memory, so a dump of the running process
   yields plaintext code without touching any file on disk. If the unpacker refuses this build
   (an unrecognised variant), nothing is lost — the task simply stays `[FLAT]` as the drop said.

## What this does NOT change

The drop's own warning stands and is repeated here so it is not lost: **do not read the 105-entry
NVAPI interface table at `013d452c` as evidence for Automatic.** It carries `NvAPI_VIO_*`,
`GPU_GetECC*`, `Mosaic` and `I2CRead/Write` — functions no game calls — and omits `NvAPI_Initialize`
itself while the game demonstrably calls it. It is the linked SDK's fixed table, not a usage list.
`[inferred-static 2026-09-02]` The Direct-vs-Automatic question is still open and still decided by
the `.text` scan, which is why unwrapping `.text` matters.

Also withdrawn by the drop, and recorded here so the correction travels: the 2026-09-01 `/pd` claim
that the exe "has essentially no stereo strings, so the integration lives in the engine layer and
its config" was an artefact of the encryption, not a finding. `[disproved 2026-09-02]`

## Also folded in from the same drop — two shader-cache refinements

Both re-derived from the CTAB numbers, with every previously published figure reproducing:

- **`NvStereoFixTexture` is not always sampler `s1`.** Distribution across the cache: `s1` 14,221,
  `s3` 202, `s0` 46, `s2` 10. A proxy that hardcodes `s1` misses ~1.7% of shaders.
  `[verified-numerically 2026-09-02]`
- **`ps_3_0` `c4` is not one thing.** It holds `ViewProjectionMatrix` in 4,122 shaders but
  `WorldToViewMatrix` (4×3) in 135. `[verified-numerically 2026-09-02]`

Both matter to the proxy plan described in
[the `NvStereoFixTexture` topics](2026-09-02-nvstereofixtexture-exact-format-and-who-writes-it.md).

## The concrete next step

1. Confirm the second witness: is `steam_api.dll` in the exe's import table? (Static, seconds.)
2. Unpack a **copy** with Steamless.
3. Re-run the positive control on the output before believing any result.
4. Then the Direct-vs-Automatic scan, as originally specified.

## Sources

- [atom0s/Steamless](https://github.com/atom0s/Steamless) — supported SteamStub variants, stated
  purpose ("remove the Steam DRM and decrypt the `.text` section"), licence and own-your-games
  stipulation.
- [GHFear/Steamstub-v3-Unpacker](https://github.com/GHFear/Steamstub-v3-Unpacker) — v3 unpacker,
  rebuild-original-executable behaviour, keep-`.bind` option, licence.
- [Adam Hlt, "Cube World Reversing — Unpack the game"](https://adamhlt.com/cube-world-reversing-unpack-the-game/)
  — the `.bind` section, entry-point redirection into it, `.text` encrypted at rest and decrypted at
  runtime, and the two practical routes (Steamless vs. analysing the runtime-decrypted process).

## Cross-project note

The identification test in this topic — *a `.bind` section, plus an entry point outside `.text`* —
is engine-agnostic and costs seconds on any Windows game in the estate. A pointer has been filed to
`flat-to-vr-cross-engine-research/inbox/` for `/sr`, because "is this exe Steam-wrapped, and does
that explain my empty static scan?" is a question every project can hit, and Alice is the second
build in the estate (after Manhunt) where a packed `.text` silently turned a scan into a false
negative.
