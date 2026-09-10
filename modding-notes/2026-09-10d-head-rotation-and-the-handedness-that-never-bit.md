# 2026-09-10d — head rotation, and the handedness error that never came

`/pd` session, dev PC. **The game was not launched and nothing here has been run against it.**
Everything below is compile-verified or checked numerically on the host.

---

## The headline

**The camera now turns with the player's head as well as moving with it.** Build
`648a44e15b47`, 727,040 B, deployed, backup `d3d9.dll.bak-2026-09-10d-pre-headrot`.
`[compile-verified 2026-09-10]` The test suite went from 33 checks to **63, none failing**
`[verified-numerically 2026-09-10, n=63]`.

## ⭐ The board's own warning was wrong, and that is the useful part

The `OPEN` row said, in my words yesterday evening:

> ⚠️ Expect this to be where a handedness error finally does bite: unlike the offset, a
> rotation cannot be reduced to dot products.

**It can, and it is.** Build both orthonormal triples with `forward = −back` — the one stored
at re-centre and the one the head has now — and take the nine pairwise dot products,
`L[i][j] = A_i · A′_j`. Column *j* of the result is simply *where axis j went*, written in the
origin's own axes, which is what a rotation in that frame **is**.

No component is permuted or negated beyond the single documented `forward = −back`, and no
coordinate handedness is named anywhere in the conversion. `det(L) = +1` falls out rather than
being imposed: each triple has determinant −1 against OpenVR's right-handed axes, and the two
signs cancel. The test asserts it `[verified-numerically 2026-09-10]`.

**The lesson generalises past this project:** when a conversion between two coordinate
conventions looks like it needs sign decisions, check whether it can be written as projections
onto a basis you already hold. Dot products of vectors living in one consistent space are plain
numbers, and plain numbers have no handedness to get wrong.

## ⚠️ The real trap was somewhere else entirely — the depth column

The obvious way to turn the camera is to decompose the matrix, rotate the basis, and write the
columns back. **That would have been wrong here**, and it would have failed in a way that does
not look like a rotation bug.

The view-projection's columns are understood as `p00·right`, `p11·up`, *(column 2)*, `forward`.
Column 2 is the **depth** column, and **nothing in this project has ever inspected it** — the VP
diagnostic prints only rows 0 and 3 `[measured 2026-09-10]`. Rebuilding three columns and
leaving the fourth alone would compute `clip.x` and `clip.y` from the new facing while `clip.z`
kept the old one. The picture would turn and the depth would not, which reads as z-fighting and
wrong occlusion, not as a broken rotation.

**So it pre-multiplies instead.** Rotating the *world* about the eye point needs to know nothing
about any column: the matrix product carries all four through consistently, column 2 included,
whatever it holds. It is the same trick the eye offset already used — translating the eye by *d*
is translating the world by −*d* — generalised from a translation to a rotation.

Two of the 63 checks exist purely to pin this down: after a 25° turn the depth column is still
exactly parallel to forward, and its length ratio is unchanged. Both would fail under
decompose-and-rebuild.

## What else the tests pin

`[verified-numerically 2026-09-10, n=63]`, linking the shipped `stereo_ue3.c` and `vr_pose.c`
rather than transcriptions:

- **Identity changes nothing, bit for bit.** A launch with a headset sitting still is
  indistinguishable from a launch without one.
- **`p00` and `p11` are unchanged** — the projection is not disturbed, only the facing.
- **The eye does not move**, to the precision of the original matrix. Turning your head must not
  translate you.
- **The matrix still passes `is_camera_vp`**, so the stereo shear that runs afterwards still sees
  what it expects.
- **A 25° head turn to the left turns the camera 25° to the left**, and forward moves toward
  −right rather than +right.

## ⚠️ Order matters, and it is documented in the code

The offset is applied **first**, in the unrotated basis; the rotation turns the view about the
eye the offset just placed. The tracker reports head *position* in the frame the player was
facing when they re-centred, not the one they are facing now, so applying the rotation first
would steer the positional offset with the player's head — which is not how a head works. Both
still land before the stereo shear, for the reason already on record: the shear destroys the
orthonormal basis both of them need.

## What is NOT established

- **That any of it works.** Nothing has been launched and no headset has ever been connected to
  any of today's three builds. Every claim here is compile-verified or host-numeric.
- **That the two halves can be tested separately.** They cannot, as built: position and rotation
  engage together the moment a tracker is live. If the first headset session sees something
  wrong, the log distinguishes them — the camtrace line now carries `headrot=on|identity` with
  its own applied/refused counters beside the offset's — but there is no key to turn one off. The
  keypad is full, and inventing a chord for this was judged worse than the log.
- **Comfort.** Rotational head tracking composed onto a game whose own camera is still driven by
  the mouse and keyboard can fight the player. Whether it does is a headset question.
- **The diagnostic that would show the derivation is wrong rather than a knob untuned:** if
  turning your head left turns the view *right*, the fault is in the basis correspondence, and
  the 63 checks say it would have to be in Alice's own camera axes rather than in this
  conversion — which would make it the same root cause as a mirrored positional offset, not a
  separate bug.
