# 2026-09-29: the shadow matrix arrives before its pass

*Dev PC, a session with Tefa at the keys for the menu recording, then driven by Claude.*

## The menus drive themselves

Tefa played launch → Alice in the level once while Menu-o-matiC recorded (Page Up = a key is needed,
Page Down = just wait, End = stop). Five of the eleven marks became checkpoints: the autosave warning,
the copyright screen once "Press ENTER" shows, profile select, the main menu, and the level. The moving
logos are simply waited out. The route replays from a closed game in 50 s, three times out of three.

Two lessons went into the tool: the recorder's marker keys moved off the number pad (this mod's hotkeys
live there, and presses that reached the game moved the view), and a replay now keeps waiting when the
game opens its window empty for a moment.

## Why the shadow fix could never fire

The `otherview` line in an ordinary lit room: `ScreenToShadow binds=15,535 writes=0`. The pass is on
screen all the time, yet its matrix register is never written while it is bound. A watcher build
(`edf5c7829111`) stamped every pixel-constant write with the shader bound at the time: at every one of
2,136 binds, c8 had been written that same frame with another pixel shader bound.

So the game uploads the matrix and only then binds the pass. The rewrite built on 2026-09-13 only looks
at writes made with the pass bound, so it would have stayed at `fixed=0` forever, and switching its
marker on would have "shown" that the fix does nothing. The next build moves the rewrite to the draw.

## Also done

- `device.cpp` was over the 1,500-line limit; split move-only into two include files, proven by an
  identical build hash (`8dea5b9ce191`) before anything new went in. Tag `pre-split-2026-09-29-alice`.
- Offset 0 vs 200 pictures were taken, but at 200 Alice's feet are on the bottom edge of the screen, so
  her shadow is out of shot. The next picture pair needs a spot with the floor under her in view.

## Later the same day: the fix moved to the draw, and it fires

Build `99f74b4b13e8` remembers the game's last upload of the four shadow-matrix registers and, just
before a draw with the shadow pass bound, sends the corrected matrix. Live in the start room, fix on:

- head offset 0: nothing sent, picture unchanged apart from the animated characters;
- head offset 200: 7,401 corrections sent, 0 refused, and the floor-shadow areas change;
- back to 0: the count stops rising.

It also fixed a latent fault: the head pair the correction uses was never cleared when the head came
back to rest, so the last non-zero edit would have kept being applied.

Not yet known: whether the shadows now sit in the right place. The start room's shadows are soft, and
at offset 200 Alice's feet are on the screen edge. The next pictures need a spot with a crisp shadow on
open floor, which Tefa walks Alice to.
