# Alice: Madness Returns (2011) — VR Engine Research

Engine research toward a VR conversion of **Alice: Madness Returns (2011)** —
built on **Unreal Engine 3** by Spicy Horse Games, published by Electronic
Arts — with stereo rendering, 6DOF head tracking, and (eventually)
motion-controlled combat as the goal.

This repository holds two things:

- **[`PLAYBOOK.md`](PLAYBOOK.md)** — a reusable, engine-agnostic, point-by-point
  method for taking *any* game whose engine nobody has converted to VR and
  getting it there. It is oriented around one North Star: **the game rendering
  in a headset with head tracking**, with everything else built on top. The same
  playbook is copied into each of our VR projects' research repos.
- **[`ENGINE-DOSSIER.md`](ENGINE-DOSSIER.md)** — the distilled, current-truth
  reference for *this* game's engine. Only the identity section is filled in
  so far — engine research has not started yet; this repo was seeded ahead of
  that work so the project structure is ready.

The blow-by-blow development history will live in the sibling repositories
(`-dev-archive` for the messy in-progress record, `-modding-notes` for readable
field notes). This repo is the consolidated engine knowledge, not the diary.

## A possible open lead (unverified)

Unreal Engine 3 has been the target of community VR tooling for other games
(the general UEVR-style ecosystem covers many UE3/UE4 titles) — whether any of
that tooling or technique applies here is an open question worth checking
during the external-research pass. Nothing about this has been verified yet;
treat it as a lead, not a finding.

## The six repositories for Alice: Madness Returns VR

Everything for this game lives in six repositories, each with one job — so you
always know where to look. You are in **alice-madness-returns-vr-engine-research**.

| Repository | What lives here |
| --- | --- |
| [alice-madness-returns-vr-mod](https://github.com/TefMeister/alice-madness-returns-vr-mod) | The mod itself — once code exists, it lands here. |
| [alice-madness-returns-vr-dev-archive](https://github.com/TefMeister/alice-madness-returns-vr-dev-archive) | Full development history — snapshots, probes, dead ends, raw recon. |
| [alice-madness-returns-vr-modding-notes](https://github.com/TefMeister/alice-madness-returns-vr-modding-notes) | Readable field notes / progress ledger. |
| [alice-madness-returns-vr-staging](https://github.com/TefMeister/alice-madness-returns-vr-staging) 🔒 | **Private** — unverified WIP builds, cross-machine handoff. |
| **alice-madness-returns-vr-engine-research** ← you are here | Distilled engine reference (dossier) + reusable VR RE playbook. |
| [alice-madness-returns-vr-external-research](https://github.com/TefMeister/alice-madness-returns-vr-external-research) | Ongoing public-research leads, gathered separately from hands-on modding work. |

## Status

Project started 2026-08-25. Groundwork phase: repos just created, no
reverse-engineering has begun yet. See the dossier for the current phase and
open risks as they're identified.

## Scope, ethics, and legality

- This is a **non-commercial fan project**. It requires owning a legitimate copy
  of the game and **redistributes no original game assets** — only files we
  create. See [`.gitignore`](.gitignore).
- We **credit everyone** whose work or research this builds on, and we honour
  correction/removal requests from actual rights holders. See
  [`CREDITS.md`](CREDITS.md).

## Templates

New engine? Start its dossier from
[`templates/per-engine-research-template.md`](templates/per-engine-research-template.md).

## Contributing & policy

See [CONTRIBUTING.md](CONTRIBUTING.md) — how we credit and link sources, our
**study-everything-public but write-our-own-code** rule (we copy no one else's
source code or files, any license or price), the terms for reusing our work
(free, with credit), and how to request a correction or removal.
