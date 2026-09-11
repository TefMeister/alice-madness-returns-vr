# Unit scale, read statically from the game's own script package — about 95 units per metre, not 50

From: `/lm` reader helper (dev PC), 2026-09-11. Static only: no launch, nothing attached, no game
file copied anywhere. Answers the board's `[FLAT]` "MEASURE THE GAME'S UNIT SCALE" row with an
independent number to check the live one against.

## How it was read

`AliceGame\CookedPC\AliceGame.u` and `Engine.u` are LZO-compressed UE3 packages (version 690,
engine 6760, compression flag 2), so a plain `grep` finds nothing — `BaseEyeHeight` does not occur
in `Engine.u`'s bytes at all. The numbers below come from decompressing the chunks in memory
(a ~150-line pure-Python LZO1X decoder plus a UE3 name/import/export and tagged-property reader,
scratch only) and walking each object's default properties. **Positive controls:** Engine's
`Default__Pawn` reads back the stock UE3 values (`CollisionHeight 78`, `CollisionRadius 34`,
`BaseEyeHeight 64`, `JumpZ 420`, `MaxStepHeight 35`), and London's `FPSCamera.FOV = 65` and third
person `FOV = 70` are **exactly the hfov values measured live on 2026-09-09** (65.1° / 70.0°).
`[measured 2026-09-11]`

⚠️ **The player is spawned from an ARCHETYPE, not the class default.** `DefaultGame.ini` names
`ArcheType_AliceLondon` / `ArcheType_AliceWonderland` (both exports of `AliceGame.u`), and they
override the size values. `Default__AlicePawn` itself overrides no eye height or cylinder, so
reading only the class defaults would have given the stock 78 / 64 numbers.

## The numbers `[measured 2026-09-11]`

| | London (first person works here) | Wonderland |
|---|---|---|
| collision cylinder half-height | **79** (radius inherited, 34) | **79** |
| ⇒ cylinder full height | 158 | 158 |
| mesh `Translation.Z` below pawn centre | −82 | −79.5 |
| `BaseEyeHeight` / `EyeHeight` (above pawn centre) | **40** / 50 | 50 / 40 |
| `FPSCamera` Distance / FOV / Offset | 0 / **65** / **(−35, 10, 30)** | Distance 100 (a different setup) |
| `AliceCameraOffset` | (0, 2, 0) | (0, 0, 15) |
| third-person Distance (Default/Idle) | 285 / 300 | — |
| `JumpZ` | 70 | 235 (+ `DoubleJumpZ` 150) |
| `MaxStepHeight` | 35 (inherited) | 35 |
| `Min/MaxAutoClimbHeight` | 64 / 196 | same |
| `ShrinkBaseEyeHeight` | 15 | 10 |

**The mesh's own skeleton** (`SK_AliceL` and `SK_AliceW` have identical bind poses): toes at
Z 0.1, feet 9.4, pelvis 88.2, neck 138.9, head bone 143.5, **both eye bones 152.6**, eyebrows
155.0, eyes symmetric at ±3.4. No scale on the mesh component or the actor. `[measured 2026-09-11]`
(The bone-chain composition was chosen because it is the one that puts the toes on the floor and
the eyes symmetric; the other convention puts the toes 118 units up.) `[inferred-static]`

## What it implies

**Alice's eyes are ~150 units above the floor and her head top ~160–165.** For a young woman of
1.60–1.75 m (eye height 1.48–1.64 m) that is **≈ 91–103 units per metre, central ≈ 95** — about
**1 unit = 1 cm**, and roughly **double** the `50.0` the tracker ships with `[inferred-static]`.
The error band is mostly "how tall is Alice", which no file says.

Every other size anchor agrees and none supports 50 `[inferred-static]`:

| anchor | at ~95 u/m | at 50 u/m |
|---|---|---|
| cylinder 158 tall, 68 wide | 1.66 m tall, 0.72 m wide (the dress) | 3.2 m tall, 1.4 m wide |
| step-up 35 | 37 cm | 70 cm |
| auto-climb 64 … 196 | 0.67 … 2.06 m ledges | 1.3 … 3.9 m |
| Wonderland jump `JumpZ 235`, g −750 | apex 37 u = 0.39 m | 0.74 m |
| gravity −750 | 7.9 m/s² (floaty — fits Alice) | 15 m/s² |

The jump and gravity rows are weak (custom jump code: `LowJumpAccel`, double jump, float); the
skeleton and the cylinder are the strong ones.

⚠️ The 2026-09-10e headset feel ("left it on 50") is not contradicted so much as explained: it was
stereo OFF, and translation scale in a mono view is very hard to judge by feel `[hypothesis]`.

## Prediction for the live measurement

The first-person camera's height above the floor depends on a formula in script bytecode that was
not decoded. Floor = pawn centre − 79 (cylinder bottom). Candidates `[hypothesis]`:

| camera = pawn centre + … | N (units above floor) | N ÷ 1.6 |
|---|---|---|
| `BaseEyeHeight` + `FPSCamera.Offset.Z` (40 + 30) | **149** — lands on the eye bones | 93 |
| `EyeHeight` + Offset.Z (50 + 30) | 159 | 99 |
| `BaseEyeHeight` only | 119 | 74 |
| Offset.Z only | 109 | 68 |

A live N near 149 would confirm both the scale and the camera formula at once. A live N near
109–119 would mean the designers put the first-person camera at chest height, and the floor-drop
number would then UNDERSTATE the scale — trust the skeleton's ~95 in that case, not N ÷ 1.6.

## Answers to the measurement's mechanics (from source, `[inferred-static 2026-09-11]`)

- **The head offset's UP axis is CAMERA-LOCAL and follows pitch.** `alice_stereo_apply_eye_offset`
  builds `d = dx·right + dy·up + dz·forward` from the VP's own columns (`up = column_1 / p11`), so a
  pitched camera tilts "up". **Level the view first**: read `pitch=` from the `camtrace` line; at
  |pitch| ≤ 5° the vertical error is under 0.4%. At any pitch θ, vertical = N·cos θ.
- **Keys, with no tracker live:** `NumPad5` cycles RIGHT → UP → FORWARD, starting at RIGHT, so
  ONE press selects UP and logs `HOTKEY NumPad5: head axis -> UP (step 5.0, offset now …)`.
  `NumPad−` / `NumPad+` step the current axis by ∓5 units and log
  `HOTKEY NumPad-: head offset now right=… up=… forward=… (camera pos …)`.
- **They switch to scale/re-centre ONLY if a tracker is live.** The dev PC should log `vr: no HMD
  present` (or `no openvr_api.dll`) at the first `Present`; if the log instead says `HEAD TRACKING
  IS LIVE`, NumPad± changes the scale and the floor-drop cannot be done.
- **Reaching −149 is ~30 presses of NumPad−**; the four candidates sit at 22, 24, 30 and 32 presses.
