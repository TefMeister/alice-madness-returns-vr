# When you fold in my 2026-09-02 drop, fix its tag as it goes

**From:** `/gr` (2026-09-03, estate sweep)
Supersedes: the confidence tag on
`engine-research/inbox/2026-09-02-gr-direct-vs-automatic-one-static-scan-and-f2-is-patch-only.md`,
line 8 — not its content

## The one-line ask

That drop's NVAPI id table is tagged:

> `[verified-static 2026-09-02, NVIDIA's public nvapi_interface.h]`

**`verified-static` is not one of the eight vocabulary names**, so it reads as a strong claim to a
human and counts as *untagged* to every tool. Inbox files are create-only — I cannot edit my own
earlier drop, and neither should you — so the correction has to happen **as you fold it into the
dossier**. Please write it in as:

> `[reported 2026-09-03, n=3 independent reads]` — first-party, from NVIDIA's own published
> `nvapi_interface.h`, but a document read rather than a measurement

That follows `/gs`'s 2026-09-02 precedent for vendor-documentation reads, which deliberately avoided
`inferred-static` because that name means *read out of a binary* and would understate a first-party
header read.

## Why `n=3` rather than `n=1`

The ids in that table have now been read out of NVIDIA's header three times by two session types —
`/gr` 2026-09-01, `/sr` 2026-09-02, `/gr` again 2026-09-03. Today's read was independent and carried
**two positive controls inside the same query** (`NvAPI_Initialize` `0x0150E828`,
`NvAPI_Stereo_Enable` `0x239C4545`, both correct) plus an end-of-file check, so a truncated fetch
answering from the first few hundred entries would have been caught. The two ids that matter to this
project both confirmed:

- `0x96EEA9F8` → `NvAPI_Stereo_SetActiveEye` (the Direct-only discriminator)
- `0x5E8F0BEC` → `NvAPI_Stereo_SetDriverMode`

So when the scan finally runs on an unpacked `.text` (see today's other drop — the wrapper is
SteamStub and unpacking is static), **its discriminators are already settled and do not need
re-checking.**

## Nothing else in that drop changes

The method, the ids, the positive control and the `F2 is MadnessPatch's own EnableConsole, not
stock` finding are all unaffected. This is a tag correction only.
