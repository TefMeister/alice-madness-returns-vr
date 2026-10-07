# 2026-10-07 — the shadow fix re-derived, and three more fixes waiting for one test

Dev PC, `/lm`, unattended, one reader.

- First OBS recording of Alice: menus → save → a look around the kitchen, 60 fps, game window only.
- The reader found why the 2026-09-29 shadow fix looked wrong: it corrected the right thing in the wrong maths space.
  Rebuilt against what the game's shaders really do; in simulation the error goes from over 100 to almost zero.
- The same mistake affects light falloff and depth of field (fix built, off), and in the headset 40 of the shadow
  shaders would show shadows floating ~3 m away (fix built, off). Same for all 33 light/blur shaders (fix built, off).
- The big code file was split into smaller files, proved byte-identical.
- Installed and running: `5d3ce56be320` (the corrected shadow fix on). The newest build `080ed4a06f9f` (all switches)
  is in staging, not installed.

**Not established:** whether any of it looks right in the game. The kitchen has no clear Alice shadow. The deciding
test is the mushroom spot from 2026-09-29 with Tefa walking there: offset 0 vs offset 200 with each switch.
