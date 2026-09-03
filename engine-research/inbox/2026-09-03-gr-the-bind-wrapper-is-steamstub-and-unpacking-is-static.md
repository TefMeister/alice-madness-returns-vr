# The `.bind` wrapper is identified: it is SteamStub, and unpacking is a STATIC step

**From:** `/gr` (2026-09-03, estate sweep)
Supersedes: ENGINE-DOSSIER.md §4 ("No DRM found"), and the "needs a runtime dump" remedy in §6's
`⛔️ THE EXE'S .text IS ENCRYPTED AT REST` block and in §11's first dead-end row
**Topic:** [`external-research/topics/2026-09-03-the-bind-section-is-steamstub-and-a-public-unpacker-restores-text.md`](../../external-research/topics/2026-09-03-the-bind-section-is-steamstub-and-a-public-unpacker-restores-text.md)

## The dead end this answers

§11, first row:

> **Any static scan of `AliceMadnessReturns.exe`'s `.text`** — strings, immediates, xrefs. The
> section is encrypted at rest (entropy 8.00, entry point in `.bind`); a null result means nothing.
> **Needs a runtime dump first.** `[measured 2026-09-02]`

The measurement is right. **The remedy is more expensive than it needs to be.**

## What the research found

The four measured facts — a section named **`.bind`**, the **entry point inside it** rather than in
`.text`, `.text` at **entropy 8.00**, and **zero `CC` padding runs** — are the published detection
signature of **SteamStub, Valve's own DRM wrapper** applied at upload time. The stub decrypts and
decompresses the real code section into memory at startup and then jumps to the original entry
point. `[reported 2026-09-03]`

Two open-source unpackers cover it, both on GitHub and both explicitly for software you own:
**[Steamless](https://github.com/atom0s/Steamless)** (variants 1, 2 and 3, 32- and 64-bit — this exe
is PE32, so in range) and **[Steamstub-v3-Unpacker](https://github.com/GHFear/Steamstub-v3-Unpacker)**.
Steamless's stated purpose is to "remove the Steam DRM and decrypt the `.text` section", producing a
PE for static analysis.

## Suggested dossier changes

1. **§11, first row and §6's remedy line:** change "Needs a runtime dump first" to *"Unpack a **copy**
   with Steamless first (static, `[PD]`); a runtime dump is the fallback if the variant is
   unrecognised."* The whole NVAPI Direct-vs-Automatic scan moves back from `[FLAT]` to `[PD]`.
2. **§4:** "No DRM found" now needs a second sentence, not just §6's cross-reference. EA Cuckoo
   really is gone and that history is intact — but the shipping binary **is** wrapped in Steam's own
   DRM stub, and that is what §6 measured. Suggested: *"EA Cuckoo removed Jan 2022 (documented,
   dated). The build is nonetheless wrapped in **SteamStub**, Valve's own DRM — see §6; that is a
   packaging wrapper, not an anti-tamper system like Denuvo, and a public unpacker handles it."*
3. **§3's section list** already records `.bind`; worth one parenthesis marking it as the SteamStub
   stub section rather than a UE3-toolchain artefact (unlike `.textidx`, which the same line
   correctly calls benign).

## Two cautions to carry into the dossier with it

- **The unpacked exe is for reading, not running.** Public write-ups of this workflow note an
  unpacked binary generally will not launch standalone because the game still expects the Steam API
  environment the stub established. Expected outcome, not a failed unpack. Work on a copy; never
  overwrite the shipped exe. `[reported 2026-09-03]`
- **Re-run the positive control before believing any result** on the unpacked file:
  `NvAPI_Initialize` `0x0150E828` must be found. That control is what stopped the 2026-09-02 scan
  being misread as a clean "Automatic", and it is what will stop a partial unpack being misread the
  same way.

## One cheap second witness

Is `steam_api.dll` in the import table? Seconds of static work, and it confirms the family
independently of the section name.
