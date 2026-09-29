# 2026-09-29: shadow fix at the draw, first look in a sharp-shadow spot

Tefa walked Alice to a spot with a crisp shadow; Claude took the pictures (half size, our build's output).

- `s-on-0.png`: head offset 0 (the fix sends nothing here, so this is the game's own picture). Alice's
  shadow is crisp, down-left of her feet, on brightly lit ground.
- `s-off-200.png`: offset 200, fix OFF (switched off live with `poke.py`, same spot, same moment).
  Bright ground beside Alice with a hard straight edge of light; no clear Alice silhouette.
- `s-on-200b.png`: offset 200, fix ON. The ground around her goes mostly dark, again with a straight edge.

Neither 200 picture shows her shadow the way offset 0 does, and the fix changes the lighting a lot.
Not judged right or wrong yet. `poke.py` flips the fix switch inside the running game (the variable's
address comes from `llvm-nm` on the deployed DLL: `g_shadowOn` at RVA 0x4cb980 in `99f74b4b13e8`).
