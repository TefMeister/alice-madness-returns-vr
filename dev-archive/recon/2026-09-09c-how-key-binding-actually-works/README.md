# 2026-09-09c — how key binding actually works

`/pd` session, dev PC. **The game was not launched and nothing here was run
against it.** Everything came from reading two files the game already wrote and
searching the shipped executable's unencrypted `.rdata`.

| file | what it is |
| --- | --- |
| `keybinding-map.txt` | output of `dev-archive/tools/parse_gameconfig_cfg.py` — the profile's 66 key slots mapped row-by-row onto the 33 `[Engine.KeyCommands]` actions |

## The finding

Key binding is split across two files, and `AliceControlLayout.ini` — the one
every session had been editing — is neither:

- **commands**: `[Engine.KeyCommands]` in `AliceInput.ini`, 33 `Key_<Action>` rows;
- **keys**: `CheckPoint\<profile>\GameConfig_PC.CFG`, a fixed 33 × 2 = 66 array
  of key names (primary 1..33, then secondary 1..33), with **no command text
  anywhere in it**.

`[measured 2026-09-09]`. The action set is fixed at 33, so no ini edit can create
a 34th — which is why added rows were inert.

**The anchor that makes the mapping more than arithmetic:** slot 5 reads
`T` / `Key_AimingMode` / `EnterFPSByRS`, and `T` entering first person is the one
binding verified live on this project.

## What is NOT established

That `Engine.KeyCommands` feeds those 66 slots is an **adjacency plus count**
argument — the strings sit together in `.rdata`, the counts match 2:1, and the
rows read coherently. It is not a decoded loader. `.text` is encrypted at rest
and no unpacked copy of the exe survives on this machine.

Nothing here has been run, so the recipe in the note is `[inferred-static]`.

## Reproducing

```
python dev-archive/tools/parse_gameconfig_cfg.py
```

Reads two files, writes neither, and extracts only key names and command
strings — interface metadata, not game content.
