# Where the next pixel-VP run should go — dynamic lights are rare in this game

From: `/lm` reader helper (dev PC), 2026-09-11. Static only: map export tables, the localisation
text, and the save's own strings, all read-only. No launch, no builds, no staging edits.

Context: on `84eca4ff` in the Vale of Tears the pixel diagnostic read `VP-shader-bound=0
camera-shaped=0` over 63,602 full c4 windows `[verified-live 2026-09-11, n=1]`, so that spot draws
nothing that uses the pixel VP copy. Most of the 4,090 pixel shaders carrying it are dynamic-light
passes (3,580 bind `LightAttenuationTexture`).

## Where the save is `[measured 2026-09-11]`

`CheckPoint\tefa\Alice2Checkpoint.sav` and `PersistentData_PC.PSD` name `Chapter1_W1_P` and the
streamed pieces `Chapter1_W1_VoT_01_S`, `VoT_03_S`, `VoT_04_S`, `VoT_05`, `VoT_05_S`, plus
"Start of VOT" and `A2_VOT_02`. **Chapter 1, Vale of Tears, early.**

## Dynamic lights across the whole game `[measured 2026-09-11]`

Of **858** shipped `.umap` pieces, only **17** contain any Movable, Toggleable or Dominant light
actor, and **none contains a Dominant light** (the sun-type ones that would light a whole outdoor
area per pixel). No light components sit on non-light actors either. The full list:

| map piece | lights |
|---|---|
| **`Chapter1_W1_TMaker_02_S`** — same world as the save | 1 PointLightMovable |
| `Chapter1_W1_Cin_Car` (a cutscene) | 2 PointLightMovable |
| `Chapter1_W2_Cin_1102` (a cutscene) | 2 PointLightMovable |
| `Chapter2_L1_Cin_214` (a cutscene) | 1 Movable, 1 Toggleable |
| `Chapter2_W1_Tundra_01_S` | 1 PointLightMovable |
| `Chapter2_W3_Crypt_01_S` / `_02_S` / `_03_S` | 1 PointLightMovable each |
| `Chapter3_W1_SP_01` | 1 PointLightToggleable |
| `Chapter4_W2_West_06Dyn_02` | 1 PointLightMovable |
| **`Chapter5_L1_Hyde_02_S`** — the densest in the game | 1 Movable, **6 Toggleable** |
| `Chapter5_W1_BoysL_04`, `Chapter5_W1_Boys_01_04` / `_05`, `Chapter5_W2_Boys2_01` | 1–2 Toggleable |
| `Chapter6_Asylum_01_S`, `CC_Rolling` (challenge cave) | 1 SpotLightMovable |

## Recommendation

1. **Nearest: play forward from the save into the TMaker part of Chapter 1's first Wonderland world**
   (`Chapter1_W1_TMaker_02_S`, streamed into the same `Chapter1_W1_P` as the save). That TMaker comes
   after the VoT pieces is `[inferred-static]` from the level list, not confirmed. Its single movable
   point light also means the effect will be local: stand near it.
2. **Densest: Chapter 5's London Hyde area** (`Chapter5_L1_Hyde_02_S`, 7 dynamic lights) — far
   from the save.
3. **Chapter Select exists** (`FlashUI_ChapterSelect`, "Chapter Points"), but the game warns
   *"Load this Chapter Point? This will delete previously saved data."* So jumping there costs
   Tefa's current save — his call, not ours. Back up `CheckPoint\tefa\` first if it is ever used.

## Two caveats for reading that run

- **Characters are lit through a `DynamicLightEnvironment`** (Alice has `MyLightEnvironment`). Its
  light did not produce a VP-bound pixel write in the Vale of Tears with Alice on screen, so do not
  count on Alice herself as the test surface `[inferred-static]`.
- **`VP-shader-bound` counts only full 4-register windows.** The same run saw 203,587 one-register
  and 303,258 two-register writes touching c4. A copy uploaded in pieces would not be counted there.
  If a scene with visible dynamic lights still reads `camera-shaped=0`, a split upload is the next
  suspect: the matcher skips writes under 4 registers, and the diagnostic would need a "VP-declaring
  pixel shader bound at draw time" counter to see it `[hypothesis]`.
