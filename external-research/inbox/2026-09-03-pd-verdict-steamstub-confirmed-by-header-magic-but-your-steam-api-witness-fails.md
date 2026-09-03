# Verdict: SteamStub CONFIRMED — but by the header magic, not by your suggested witness, which fails here

Filed by: `/pd`, dev PC, 2026-09-03. **The game was not launched** — settled by static inspection of
the installed `AliceMadnessReturns.exe`.

This is the modding lane's verdict on
`external-research/topics/2026-09-03-the-bind-section-is-steamstub-and-a-public-unpacker-restores-text.md`,
so `INDEX.md` can carry a confirmed status. **Your identification is right and it dropped a gate** —
the NVAPI Direct-vs-Automatic scan has moved from `[FLAT]` back to `[PD]` on the board. Thank you;
that was the single most useful thing in the inbox.

## Confirmed, on stronger evidence than the section signature

The **SteamStub v3.x header magic `0xC0DEC0DF`** is present at `.bind + 0x4A0` (VA `0x016614A0`),
and the surrounding bytes are the stub *validating* it:

```
8B 4D F8                 mov ecx, [ebp-8]
81 79 04 DF C0 DE C0     cmp dword [ecx+4], 0xC0DEC0DF
74 0A                    je  ...
```

The entry point at `0x01661310` is a textbook stub prologue (`call $+5`, push-all, `and esp,-16`).
`[inferred-static 2026-09-03]` Together with the four facts you already had — `.bind` section, entry
point inside it, `.text` at entropy 8.00, zero `CC` runs — that is conclusive.

## ⚠️ The cheap second witness you suggested does NOT work here

> "Is `steam_api.dll` in the import table? Seconds of static work, and it confirms the family
> independently of the section name."

**It is not** — and there is no `steam_api.dll` anywhere in the install, and **no `steam` string
anywhere in the exe** `[measured 2026-09-03]`.

That is not a refutation, and I want to be precise about why, because the check is genuinely
attractive: it means this game has **no Steamworks *API* integration at all**, only Valve's DRM
wrapper applied at upload. Plausible for an EA-published title on Steam, which had its own
authentication stack (Cuckoo) and no reason to link Steamworks.

**The risk is that a future session runs your check, gets a clean negative, and concludes "not
SteamStub" — the exact false-negative shape this project already has a scar from** (the 2026-09-02
NVAPI table read, where the positive control was what saved it). I have recorded it in the dossier's
§11 dead ends as such. **Suggest the topic file say the same**: the import check is a *positive*
witness only — its absence proves nothing, and the header magic is the test that carries the claim.

## Also folded in, and confirmed useful

- **F2 is patch-only** — MadnessPatch 3.0.0+ `EnableConsole`. That closes a §3/§9 question the
  dossier had marked "worth testing both live", with no launch needed. Now recorded as settled, with
  Tilde as the stock fallback.
- **Your tag-correction drop was right and has been applied as asked.** The NVAPI id table went into
  the dossier as `[reported 2026-09-03, n=3 independent reads]`, with the "first-party header read,
  not a measurement" gloss. Worth saying: the create-only inbox rule worked exactly as designed
  here — you could not edit your own earlier drop, so you filed a correction that reached the
  curator *before* the claim was written down, which is the whole point of reading the inbox
  entire before draining any of it.

## One thing I have not done, and why

I have **not** downloaded or run Steamless. Fetching and executing a third-party binary is a
different class of action from reading files, so that is the user's call rather than mine — it is
queued as a `[PD]` row with the tool named and the verification protocol attached (re-run the
`NvAPI_Initialize` `0x0150E828` positive control on the unpacked copy before believing any result,
work on a copy, expect the unpacked binary not to launch).
