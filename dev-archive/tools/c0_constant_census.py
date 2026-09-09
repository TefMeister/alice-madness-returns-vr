#!/usr/bin/env python3
"""c0_constant_census.py - what does ANY shipped shader bind to register c0?

WHY THIS EXISTS
  The board's open question was "what IS the once-per-frame non-camera matrix at
  c0?". The live census (2026-09-09) established that exactly one non-camera
  matrix reaches c0 per frame and that it is the LAST write of the frame, but
  not what it is.

  Before instrumenting the game for that, there is a cheaper question that can
  be settled entirely on disk: is anything OTHER than ViewProjectionMatrix ever
  bound to vertex register c0? Compiled D3D9 shaders carry a CTAB block naming
  every constant and its register, so this is plain data in files that ship.

  The answer is no - see the dossier. That does NOT identify the mystery matrix,
  but it rules out a whole class of explanation: it is not some other named
  constant sharing the register, so it must be a different MATRIX written into
  the same ViewProjectionMatrix slot, i.e. a different VIEW.

⚠️ WHAT THIS CANNOT SEE
  A constant table says what a shader READS. SetVertexShaderConstantF writes the
  register whether or not any shader reads it, so a write with no corresponding
  CTAB entry is invisible here. This narrows the question; the live c0dump in
  the proxy is what settles it.

⚠️ READS BOTH CACHES. Earlier passes on this project only ever read
  RefShaderCache (material shaders). UE3 keeps its post-process, filter and
  fullscreen shaders in GlobalShaderCache - exactly where a once-per-frame final
  pass would live - so both are read here.

Reads game files, writes none, and extracts no game content: only constant names
and register indices, which are interface metadata.
"""
import argparse
import collections
import importlib.util
import os
import sys

DEFAULT_COOKED = (r"D:\Program Files (x86)\Steam\steamapps\common"
                  r"\Alice Madness Returns\AliceGame\CookedPC")
CACHES = ["RefShaderCache-PC-D3D-SM3.upk", "GlobalShaderCache-PC-D3D-SM3.bin"]


def load_ctab(toolkit):
    """Import the toolkit's d3d9-ctab.py (its filename is not importable)."""
    path = os.path.join(toolkit, "tools", "d3d9-ctab.py")
    if not os.path.exists(path):
        sys.exit("cannot find %s - pass --toolkit" % path)
    spec = importlib.util.spec_from_file_location("d3d9ctab", path)
    mod = importlib.util.module_from_spec(spec)
    saved, sys.argv = sys.argv, [path]      # it parses argv at import time
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.argv = saved
    return mod


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    guess = os.path.abspath(os.path.join(here, "..", "..", "..",
                                         "flat-to-vr-RE-toolkit"))
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cooked", default=DEFAULT_COOKED,
                    help="the game's CookedPC directory")
    ap.add_argument("--toolkit", default=guess, help="flat-to-vr-RE-toolkit checkout")
    ap.add_argument("--register", type=int, default=0,
                    help="float4 register to census (default 0)")
    ap.add_argument("--limit", type=int, default=25, help="rows per target")
    args = ap.parse_args()

    m = load_ctab(args.toolkit)
    reg = args.register

    for fn in CACHES:
        path = os.path.join(args.cooked, fn)
        if not os.path.exists(path):
            print("MISSING: %s" % path)
            continue
        seen, tables = m.collect(path)
        print("=" * 72)
        print("%s\n  %d CTAB blocks, %d distinct tables" % (fn, seen, len(tables)))

        per_target = collections.defaultdict(collections.Counter)
        totals = collections.Counter()
        for (rows, tgt), count in tables.items():
            totals[tgt] += count
            hit = None
            for name, regset, regidx, regcount in rows:
                # regset 2 = float4. A constant occupies the register if it
                # STARTS there; a 4x4 starting at c0 spans c0..c3.
                if regset == 2 and regidx == reg:
                    hit = (name, regcount)
                    break
            per_target[tgt][hit if hit else ("<nothing at c%d>" % reg, 0)] += count

        for tgt in sorted(per_target):
            print("\n  --- %s  (%d shaders) ---" % (tgt, totals[tgt]))
            for (name, rc), n in per_target[tgt].most_common(args.limit):
                print("     %7d  %-44s %s"
                      % (n, name, ("c%d x%d" % (reg, rc)) if rc else ""))
    print()
    print("A 4x4 matrix shows as `x4`. Anything marked `x1` is a single vector")
    print("and cannot be the once-per-frame MATRIX the board is asking about.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
