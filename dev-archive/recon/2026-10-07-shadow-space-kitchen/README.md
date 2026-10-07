# 2026-10-07: the re-derived shadow fix, first live run (kitchen at the save point)

Build `91faf14b965c` (staging `alice-madness-returns-vr/proxy-d3d9`, `7a06834`): the ScreenToShadow correction now
works on the shader's real input u = (x·W, y·W, W, 1); `g_shadowSpace` 1 = new (default), 0 = the old clip-space K.

Live `[verified-live 2026-10-07, n=1]`: loads and plays; the log says `shadowfix ON space=1`; at head offset 200 the
fix is sent at the draw (`sent=2931`). `poke.py` (from `2026-09-29-shadow-fix-at-the-draw/`) flipped both switches in
the running game: `g_shadowSpace` RVA `0x4b008`, `g_shadowOn` RVA `0x4cb988` in this build.

Pictures (half size, our build's output): `s0` offset 0; `s200new` offset 200, new fix; `s200old` old fix; `s200off`
fix off. **Not a deciding spot**: Alice casts no clear shadow in the kitchen, and the three offset-200 pictures differ
by only 2-4 grey levels on average (partly the Duchess moving between grabs). The verdict needs the crisp-shadow
forest spot of 2026-09-29.
