# 2026-09-11 — Alice is 160 units tall: the scale is ~95 units per metre, not 50

Dev PC `DESKTOP-V8GTSIR`, `/lm` (auto-picked), two launches, one reader helper. Evidence:
`dev-archive/recon/2026-09-11-alice-is-160-units-tall/`. Dossier: the unit-scale section.

---

## The headline

**The head-tracking scale was off by about a factor of two.** Two independent routes — one live,
one read out of the game's own packages — both put Alice at about **160 game units** tall, which
means **~95 units per metre (1 unit ≈ 1 cm)**, not the 50 the tracker ships with. With 50, a real
head movement moves the in-game eye about half as far as it should.

## 1. The live measurement

The board's recipe (first person, lower the eye to the floor) could not run: **`T` did not enter
first person on this launch** — three presses including a 1.5 s hold, the binding present in
`AliceControlLayout.ini`, and `W` walking fine `[verified-live 2026-09-11, n=1 launch]`. It worked
on 2026-09-09 (London). Why it did not here is open (the reader is looking; the Wonderland
archetype's first-person camera setup differs from London's).

So it was measured in third person, which turns out to be cleaner:

- Lowering the camera with the proxy's head offset moves Alice's image **linearly at 2.465 px per
  game unit** (−20/−40/−60/−80 units → 47/95/150/198 px, template-matched).
- She stands **392 px** tall on screen (hair crown 312.5 → soles 704.5).
- Height = 392 / 2.465 = **159.0 units**. The ratio does not depend on the camera distance or the
  field of view, so no assumption about the projection enters.
- **Repeated 100 units closer:** she grows ×1.57 and moves 3.825 px/unit → **160.9 units**. The
  1.55× change in shift per unit matches the 1.57× change in size, as it must.

`[verified-live 2026-09-11, n=2 camera distances]`

## 2. The static check (the reader)

The game's script packages are LZO-compressed, so nothing is greppable; the reader decompressed
them in memory and read the default properties, with two positive controls (stock UE3 pawn values,
and the 65°/70° fields of view we had measured live). The player spawns from per-area
**archetypes**, not the class defaults: **collision cylinder 158 tall**, and Alice's skeleton puts
her **eyes at 152.6** units and eyebrows at 155 `[measured 2026-09-11]`. Head top ~160–165: the same
number as the live measurement, by a completely different route.

Every other size anchor fits ~95 and none fits 50 (step-up 37 cm vs 70 cm; auto-climb up to 2.06 m
vs 3.9 m; gravity 7.9 m/s² vs 15).

## 3. The stereo keys, re-proven

All six numpad stereo keys fire, each with its `HOTKEY` log line, NumLock ON in the banner:
stereo on/off (`NumPad0`), eye mode (`NumPad1`), ipd (`NumPad*` / `NumPad/`), convergence
(`NumPad3` / `NumPad.`) `[verified-live 2026-09-11, n=1 each]`. On screen: stereo ON shifts the
view −4 px, swapping eyes +8 px — symmetric ±4 about centre.

## 4. Also

- **Launch 1 exited on its own** at 18:17, a minute into gameplay, with no crash dialog and **no
  Windows crash report** (the newest is 2026-09-10's `0x00be0f63`). Cause unknown. Launch 2 was
  fine for the rest of the session.
- **The reader built the board's `[PD]` pixel-shader fix** (the pixel-shader copy of the view is now
  moved with the head, and `CameraPosition` gets the offset), opt-in by a marker file, 59 checks
  passing `[compile-verified 2026-09-11]`. Not yet run.

## Automation, scored

| Capability | Status |
| --- | --- |
| Self-launch | ✅ ×2 (Steam appid 19680) |
| Menu → gameplay | ✅ Enter ×4 (logos, title, profile, Continue) |
| Commands | ⛔ no console in this build (settled 2026-09-08) |
| Character + camera | ✅ walking; camera by the proxy's head offset; ⚠️ first person (`T`) did not engage this launch |
| Self-close | — (see the board entry) |

## Not established

- Alice's intended real-world height (the 91–103 band).
- Why `T` did not enter first person here.
- How 95 feels in the headset with stereo ON — the remaining `[VR]` step.
