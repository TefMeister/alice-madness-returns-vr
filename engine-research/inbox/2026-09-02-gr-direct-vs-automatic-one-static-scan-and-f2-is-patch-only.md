# §6's Direct-vs-Automatic caveat is decidable statically: scan the exe for two NVAPI ids and count callers (Alan Wake's method)

Filed by: `/gr`, 2026-09-02
Topic: `external-research/topics/2026-09-02-direct-or-automatic-is-a-one-scan-static-question-alan-wakes-caller-count-transfers.md`
Dossier sections: §6 ("Which 3D Vision mode UE3 actually uses is genuinely ambiguous"), §3/§9 ("F2 — unconfirmed if stock or patch-only")
Cross-project source: `alan-wake-vr` dossier §6 (2026-09-01) — the direct-caller count that retired its native-stereo shortcut

- **Discriminator:** `NvAPI_Stereo_SetActiveEye` = **`0x96EEA9F8`** has no purpose outside Direct mode; `NvAPI_Stereo_SetDriverMode` = **`0x5E8F0BEC`** must precede device creation for Direct. Positive control `NvAPI_Initialize` = `0x0150E828`; Automatic-side witnesses `Stereo_Activate 0xF6A1AD68`, `GetSeparation 0x451F2134`, `GetConvergence 0x4AB00934`, `GetEyeSeparation 0xCE653127`, `SetSurfaceCreationMode 0xF5DCFCBA`. `[verified-static 2026-09-02, NVIDIA's public nvapi_interface.h]`
- **Module:** `AliceMadnessReturns.exe` (monolithic UE3). The ids are `push imm32` operands, so the "no stereo strings in the exe" observation does not apply.
- **Reading:** callers on `SetActiveEye` ⇒ Direct (the engine already renders two eyes; the per-eye `c0` write exists in the exe — look between the LEFT and RIGHT calls). No callers on either, with callers on `Activate`/getters ⇒ Automatic (same as Alan Wake; the render-twice + own-texture plan is unchanged). No callers anywhere ⇒ look at the `Stereo3D` option's code path.
- **`Stereo3D` toggle, from players:** turns the emitter on, drops framerate, shifts dynamic shadows into stereo even when no 3D shows `[reported]` — live on modern drivers; does not by itself decide the mode.
- **F2 is patch-only:** MadnessPatch 3.0.0+ adds `EnableConsole` "bound to F2" as its own feature `[reported, release notes]`. Suggest §3/§9 say so; stock default stays Tilde.

Suggested dossier change: add the scan as the §6 next step ahead of any launch, and replace the caveat with its result once run.
