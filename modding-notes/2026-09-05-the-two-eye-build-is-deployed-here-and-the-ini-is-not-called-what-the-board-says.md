# The two-eye build is deployed on the home PC — and the ini is not called what the board says

`/pd`, home PC, 2026-09-05. **The game was not launched; nothing here was run.**

## What was wrong

The starred `[FLAT]` row — *"The two-eye build is deployed (`Binaries\Win32\d3d9.dll` 702,976 B)
… Windowed (`AliceEngine.ini` `Fullscreen=False`)"* — described the **dev PC**. On the home PC,
three things did not hold:

1. **No proxy was deployed.** `Alice Madness Returns\Binaries\Win32\` contained no `d3d9.dll`.
   `[verified-numerically 2026-09-05]`
2. **`build.sh` could not run here.** It hard-coded the llvm-mingw path under the dev PC's user
   profile, and additionally defaulted `TOOLKIT` to
   `D:/claude video game stuff/github-backups-pd/flat-to-vr-RE-toolkit` — a dev-PC disk path — for
   the shared CTAB parser factored out on 2026-09-03.
3. **⚠️ There is no `AliceEngine.ini`.** UE3 names its config after the game's script package, and
   this game's is **`Monkey`**. The file is
   `Documents\My Games\UnrealEngine3\MonkeyGame\Config\MonkeyEngine.ini`, and there is no file
   named `AliceEngine.ini` anywhere in the install or in `My Games`.
   `[verified-numerically 2026-09-05]` Anyone following the row literally would have gone looking
   for a file that does not exist. (The whole `MonkeyGame\Config\` folder is `Monkey*`-named:
   `MonkeyEngine.ini`, `MonkeyGame.ini`, `MonkeyInput.ini`, and so on.)

## What was done

- `build.sh` now takes the toolchain from `PATH` with the dev-PC path as fallback, and derives
  `TOOLKIT` from the script's own location — `staging/` and `flat-to-vr-RE-toolkit/` are siblings
  under the lane clone root — falling back to the old absolute path. Verified that the derivation
  resolves to `C:/Users/TD3KX/github-backups-pd/flat-to-vr-RE-toolkit` and that
  `lib/d3d9ctab.c` is really there, so the build used the local toolkit rather than silently
  falling back. `[verified-numerically 2026-09-05]`
- Built and deployed: `Binaries\Win32\d3d9.dll`, hash-verified against the build output. Nothing
  overwritten (no file was present).
- **`MonkeyEngine.ini`: `Fullscreen=True` → `False`**, which the row's procedure requires. Backed
  up first as `MonkeyEngine.ini.bak-2026-09-05-pre-pd`, and the change was diffed: **exactly one
  line, +1 byte**, no other difference and no encoding damage. `[verified-numerically 2026-09-05]`
  To undo, restore the backup or set the line back — it is at line 812, in the same block as
  `ResX=3440` / `ResY=1440`.

## The corroboration worth noting

The home-PC build came out at **exactly 702,976 bytes** — the size the board records for the dev-PC
build of the same commit — despite a different toolchain path and a different toolkit path. Alan
Wake matched exactly too in the same session (62,464 B). `[verified-numerically 2026-09-05]` Sizes
were compared, not hashes, so this says "the same build", not "identical bytes".

## What the row now means here

Unchanged and now executable on this machine. In order: **(a)** the frame-120 log line should show
`vp_writes` climbing and `p00=` a real number, with no keypress at all; **(b)** F9 then F6 — the
picture should rock left/right and the rock should grow with F12; **(c)** in a HUD/combat scene,
check whether HUD, crosshair, SSAO and decals move with the world or tear away.

⚠️ One difference from the dev PC: there is **no `.bak` to revert to here**, because the game
shipped without a `d3d9.dll`. If the proxy misbehaves, delete
`Binaries\Win32\d3d9.dll` and the game is stock again.
