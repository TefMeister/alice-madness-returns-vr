# Gold Digger: the first OpenXR run's camera rate (simulator)

From three Camera Jitter BeG0nE reports of 2026-10-26 (shelf `jitter`, items
`...begone-camera-jitter_2026-10-26_11-53-23_openxr`, `..._11-54-38_openxr`, `..._12-00-39_openxr`).
All three are the OpenXR Simulator, not the headset (the dev PC's 2026-10-26b run).

- The game drew **60 pictures a second** and the head pose was read 60 times a second, but the camera was
  written only **about 15 times a second** (15.3, 15.0, 11.4): **0.24 camera writes per picture**
  `[measured 2026-10-26, n=3]`.
- The board's expectation is that the head pose is renewed every second frame (one left+right pair per
  two frames, so ~30 a second). 15 a second is **half of that**: one renewal per **four** frames, if this
  counter counts the same thing `[hypothesis]`.
- The one run with turning (12-00-39) says JITTER in 2 of 2 turning seconds, and "98% of pose reads returned
  the same pose as the read before". On the simulator that second line is expected: the head is moved in
  steps by `set_head_pose`, so it holds still between steps. Only the 15-a-second camera rate is worth carrying.
- The frames at the jittery seconds were not cut: the rider on the home PC said "ffmpeg is not installed",
  although ffmpeg is installed there (winget). Tool problem, handed to the tool.

**Proposed board row** (folds into the existing `[VR USER]` first-headset row, not a new one):
before or during the first real-headset run, check where the jitter recorder counts camera writes in
Alice's bridge (per pair, per eye, or per `vr_pose.c` reader call), so a "0.24 per picture" in the headset
report can be read as a real rate fault or a counting difference. If it is real, the pair should take a
fresh pose every two frames, not four. `MODEL: OPUS`.
