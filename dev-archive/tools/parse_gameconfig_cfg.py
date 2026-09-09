#!/usr/bin/env python3
"""parse_gameconfig_cfg.py - decode Alice's key-binding profile and map it to
`[Engine.KeyCommands]`.

WHAT THIS ANSWERS
  The board asked how the game actually loads its key layout, after rows added
  to `AliceControlLayout.ini` were verified live to do nothing while shipped
  ones worked. The answer is that `AliceControlLayout.ini` is not the binding
  mechanism at all. Two different files hold the two halves:

    COMMANDS  `[Engine.KeyCommands]` in `AliceInput.ini` - 33 `Key_<Action>`
              entries, each naming the command string that action runs. No
              command text appears in the profile, so these must be read here.

    KEYS      `CheckPoint\\<profile>\\GameConfig_PC.CFG` - a FIXED array of
              33 x 2 = 66 length-prefixed key-name strings: the primary key for
              actions 1..33, then the secondary key for actions 1..33.

  So the bindable action set is fixed at 33. Adding a row to any ini cannot
  create a 34th, which is exactly why the added rows were inert.

  This script proves the pairing rather than asserting it: it parses the binary
  profile, reads the ini section, and prints them side by side. The check that
  makes it convincing is slot 5 - it reads `T` / `Key_AimingMode` /
  `EnterFPSByRS`, and `T` entering first person is the one binding this project
  has verified live.

Reads two files, writes neither. Extracts only key names and command strings,
which are interface metadata.
"""
import argparse
import os
import struct
import sys

DEFAULT_CFG = os.path.expanduser(
    r"~\Documents\My Games\Alice Madness Returns\AliceGame"
    r"\CheckPoint\tefa\GameConfig_PC.CFG")
DEFAULT_INI = os.path.expanduser(
    r"~\Documents\My Games\Alice Madness Returns\AliceGame"
    r"\Config\AliceInput.ini")


def parse_cfg(path):
    """Every <u32 len><len bytes, NUL-terminated ASCII> record, in order.

    The length includes the terminator, so "T\\0" is len 2. Records outside
    2..40 bytes or containing non-printables are skipped rather than guessed at
    - the head of the file is settings, not strings."""
    d = open(path, "rb").read()
    out, i = [], 0
    while i + 4 <= len(d):
        n = struct.unpack_from("<I", d, i)[0]
        if 2 <= n <= 40 and i + 4 + n <= len(d):
            b = d[i + 4:i + 4 + n]
            if len(b) > 1 and b[-1:] == b"\0" and all(32 <= c < 127 for c in b[:-1]):
                out.append(b[:-1].decode("ascii"))
                i += 4 + n
                continue
        i += 1
    return d, out


def parse_keycommands(path):
    txt = open(path, encoding="latin-1").read().replace("\r", "")
    if "[Engine.KeyCommands]" not in txt:
        sys.exit("no [Engine.KeyCommands] section in %s" % path)
    sec = txt.split("[Engine.KeyCommands]", 1)[1].split("\n[", 1)[0]
    rows = []
    for line in sec.split("\n"):
        if "=" in line and line.strip().startswith("Key_"):
            k, v = line.split("=", 1)
            rows.append((k.strip(), v.strip()))
    return rows


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cfg", default=DEFAULT_CFG)
    ap.add_argument("--ini", default=DEFAULT_INI)
    args = ap.parse_args()
    for p in (args.cfg, args.ini):
        if not os.path.exists(p):
            sys.exit("no such file: %s" % p)

    raw, keys = parse_cfg(args.cfg)
    actions = parse_keycommands(args.ini)
    n = len(actions)

    print("%s" % os.path.basename(args.cfg))
    print("  %d bytes, %d key-name slots" % (len(raw), len(keys)))
    print("%s" % os.path.basename(args.ini))
    print("  [Engine.KeyCommands] holds %d actions -> 2 x %d = %d slots expected"
          % (n, n, 2 * n))
    ok = (len(keys) == 2 * n)
    print("  %s" % ("MATCH - the profile is primary[1..n] then secondary[1..n]"
                    if ok else "MISMATCH - the layout below is not trustworthy"))
    print()
    print("  %-3s %-17s %-17s %-27s %s"
          % ("idx", "primary", "secondary", "action", "command"))
    for k in range(n):
        p = keys[k] if k < len(keys) else "?"
        s = keys[k + n] if k + n < len(keys) else "?"
        name, cmd = actions[k]
        print("  %-3d %-17s %-17s %-27s %s" % (k + 1, p, s, name, cmd[:52]))

    free = [(k + 1, actions[k][0]) for k in range(n)
            if k < len(keys) and keys[k] == "None"
            and k + n < len(keys) and keys[k + n] == "None"]
    print()
    print("  Actions with NO key at all (%d): %s"
          % (len(free), ", ".join("%d:%s" % f for f in free)))
    print()
    print("  A command can only be changed in the ini; a KEY lives in the")
    print("  profile above and the slot count is fixed, so a NEW action cannot")
    print("  be added by editing any ini. Repoint an existing one instead.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
