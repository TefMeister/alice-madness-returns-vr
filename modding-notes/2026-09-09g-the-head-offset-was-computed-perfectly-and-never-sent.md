# 2026-09-09g — the head offset was computed perfectly and never sent

`/lm` session, dev PC, one launch. Evidence:
`dev-archive/recon/2026-09-09g-the-head-offset-was-never-sent/`.

---

## The headline

**The eye offset never reached the device unless the stereo shear was also
non-zero.** It was written into a *local copy* of the four matrix registers, the
`applied` counter was incremented, and then — with stereo off — the function fell
through to the plain forward at the bottom of the hook and sent **the caller's
untouched matrix**. Every frame.

Fixed in `staging/…/proxy-d3d9/src/device.cpp`: the re-upload now fires when
**anything** was changed, and the shear is applied only when there is a shear.
`[compile-verified 2026-09-09]` — ⚠️ **the fixed build is deployed but has NOT
been run**; the session ended before a verifying launch.

## Why it took a launch to see

The failure signature points at the wrong thing. The log said

```
head=40.0,0.0,0.0 applied=21779 refused=0
```

which reads as *"the offset is being applied, every frame, and never refused"* —
so every hypothesis went to the arithmetic, or to whether the matrix was a real
projection at all. It was neither. **The counter counts the computation, not the
send**, and nothing in the log distinguished them.

⚠️ **General lesson: a counter that increments before the effect is delivered is
not evidence the effect happened.** Count the delivery, or say in the name that
you are not.

## The measurement that separated it

Same scene, same matrix, same session, minutes apart `[verified-live 2026-09-09, n=1 launch]`:

| | eye offset | picture moves |
|---|---|---|
| stereo **OFF** | 40 → 400 units | **0 px** at every value (corr 0.999+) |
| stereo **ON** | 365 → 255 units (110 units) | **131 px**, corr 0.44 |

A no-input control taken back to back read `dx=+0 px, corr=0.9997`, so the 0 px
is a real null and not a blind instrument.

## What this retires

- **⚠️ "The matrix we edit is a pure rotation, not a projection" is `[disproved
  2026-09-09]`.** Wonderland reads `p00cam=1.000000 p11=1.777778`, so
  `ratio=1.7778` against a backbuffer whose own aspect is `1.7778`. That is a
  genuine 90°-horizontal projection; `p00` of exactly 1.0 is what 90° looks like,
  not what a rotation looks like. The 2026-09-09f theory was good, measurable,
  and wrong — which is exactly what the ratio field was added to settle.
- **The 2026-09-09d "offset does not reach the screen" mystery is closed**, and
  the cause was not in the maths at any point.

## Two things learned on the way, both worth keeping

- **`c4` is translated too.** `CameraPosition` reads `-0.0,0.0,0.0` across
  **1,497,799** writes `[measured 2026-09-09]`. So it is in the same
  pre-translated space as the vertices, and **`PreViewTranslation` at `c5` is the
  next register to read** if the game's own world position is wanted.
- **⚠️ `pos=` is now reading back our OWN offset, not the camera.** With
  `head=255` the trace printed `pos=-28.2,253.4,0.7`. The position is recovered
  *after* the offset has been written into the matrix, so it reports what we
  injected. Harmless while the offset is 0; misleading the moment it is not.

## ⚠️ A tooling trap that cost a whole sweep

`alice_harness.py`'s numpad-minus is **`NPSUB`**; I sent `NPADSUB`. Enter is
**`ENTER`**; I sent `RETURN`. Both raise `KeyError` — but inside a chained shell
command the error scrolls past above the useful output, and the step simply does
not happen. Every "step the offset back down" in one sweep silently failed, so
the offset climbed monotonically to 390 while I believed it was returning to 40,
and five correlation readings measured nothing.

This is the **third** unchecked-failure bug on this project in one day
(`ctrlkey.py` ignoring `SendInput`'s return; `pressed()` consuming the edge; this).
**Read the value back from the game's own log after every state-changing key**,
which is what finally caught it.

## Automation — all five capabilities, this session

Launched the game, drove title → profile → CONTINUE GAME → gameplay, issued
console commands, moved the character and camera, and **closed it through its own
menus** (the `gameplay → process_exit` route re-verified step for step, clean
`proxy d3d9.dll unloading` in the log). `[verified-live 2026-09-09, n=1]`
