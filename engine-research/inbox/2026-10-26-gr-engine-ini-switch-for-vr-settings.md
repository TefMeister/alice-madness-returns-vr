# /gr pointer: an engine-ini switch could give the VR launch its own settings file

From: `/gr` estate sweep, 2026-10-26, CHECK-IN. Topic:
`external-research/topics/2026-10-26-an-engine-ini-switch-could-give-vr-its-own-settings.md`.

**Board row it serves:** `[PD]` "VR screen effects off when OpenXR is on" (2026-10-26), which asks for the cheapest
switch that only applies with OpenXR on, given that UE3 reads `AliceEngine.ini` before our hooks run.

**Finding** `[reported 2026-10-26]`: Unreal's command-line list has an override-INI group, `ENGINEINI=<file>` (no
leading `-`), with the UE3 file family (Compat, Lightmass, UI, EditorUserSettings). One forum report says it worked on
UE3. Whether Alice's shipping build honours it is untested `[hypothesis]`.

**Suggested dossier change:** list `ENGINEINI=` as candidate route 1 for the VR-only screen-effect settings, with the
one-launch test (a test copy with `MotionBlur=False`; check the log for the config file loaded) and the fallback
(launcher writes the setting before start and restores it after).
