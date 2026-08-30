# DRM history: EA "Cuckoo" authentication DRM was present, but removed in a January 2022 patch on the relisted Steam release

**Status:** 🆕 new · **Priority:** medium-high — directly seeds `ENGINE-DOSSIER.md` §4, with an
unusually well-documented backstory worth recording for context.

## What was found

Alice: Madness Returns has a genuinely unusual DRM history, worth understanding precisely rather
than assuming:

- The original 2011 release used **"EA Cuckoo" DRM** — an online-authentication scheme tied to EA's
  own account/activation servers.
- **EA delisted the game from sale in September 2016** after accidentally distributing a batch of
  already-used Steam keys — rather than replace the affected keys, EA pulled the entire game from
  sale and refunded affected buyers. This left existing owners with a game still carrying
  server-dependent authentication DRM for a title no longer being sold or (implicitly) not
  guaranteed ongoing server support — a real fragility risk for anyone trying to run it during that
  window.
- The game was **later relisted on Steam**, and per community reporting (ResetEra thread, corroborated
  by PCGamingWiki discussion), **a January 14, 2022 patch removed the EA Cuckoo authentication DRM
  entirely** from the relisted Steam version.

## Why this matters

This is now a genuinely clean DRM situation for this project — consistent with the pattern already
seen on the Prince of Persia (2008) front (DRM present historically, but the currently-installed
build turns out clean) rather than the Denuvo-protected fronts (Burnout Paradise, Mad Max). Static
recon should specifically confirm the absence of any EA Cuckoo / authentication-related strings or
network calls, but there's a real, dated, well-documented reason to expect a clean result rather than
going in blind.

## Concrete next step

When static recon begins, check specifically for EA Cuckoo/authentication-DRM signatures (network
init code, activation-related strings) as a first pass, informed by this history — expect them to be
absent (per the Jan 2022 patch), but confirm rather than assume, same discipline as every other front
in this portfolio.

## Sources

- https://www.resetera.com/threads/the-relisted-steam-version-of-alice-madness-returns-recently-got-updated-to-work-without-ea-authentication-drm.548510/
- https://www.pcgamingwiki.com/wiki/Alice:_Madness_Returns
