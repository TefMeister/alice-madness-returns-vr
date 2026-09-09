# 2026-09-09f — hold duration is erratic because the durations tested are shorter than a frame

`/pd` session, dev PC. **The game was not launched. Nothing here has been run
against it.** The last `[PD]` row on this project is closed, entirely by
re-reading a log that was already on disk.

Evidence: `dev-archive/recon/2026-09-09f-hold-duration-is-sub-frame/`.
Tool: `dev-archive/tools/analyse_hold_duration.py`.

---

## The row

> *"why hold DURATION behaves erratically (20/40/160 ms → −5.3/−168.7/+75.4°,
> while 80 ms repeats to 1%). Measured, unexplained `[hypothesis]`."*

## 1. What the binding actually is

`AliceInput.ini` → `[Engine.PlayerInput]` `[measured 2026-09-09]`:

```
Bindings=(Name="NumPadFour",Command="Axis aTurn Speed=-200.0 AbsoluteAxis=100")
Bindings=(Name="NumPadSix", Command="Axis aTurn Speed=+200.0 AbsoluteAxis=100")
```

It is an **axis**, not a button. UE3 applies an axis **once per tick while the
key is held** — so the turn is produced by a *sampled* process, and the sampling
rate is the frame rate. That is the whole shape of the answer.

## 2. The numbers, from a log we already had

386 `camtrace` samples in
`recon/2026-09-09-c0-census-camera-yaw-and-the-built-in-first-person-camera/log-run4-cumulative-yaw-and-fps.txt`
`[measured 2026-09-09]`:

| | |
|---|---|
| frame period | **median 32.3 ms** (31 fps), min 31.3, max 41.8 |
| `dmax` across the whole run | **never above 83°** |
| `dmax` on samples where the camera moved | median 53.7°, **max 56.8°** |

### ⇒ The tested durations sit at or below one frame

| hold | frames at 32.3 ms |
|---|---|
| **20 ms** | **0.6 — shorter than a single frame** |
| 40 ms | 1.24 |
| 80 ms | 2.5 |
| 160 ms | 5.0 |

**A 20 ms press can be pressed and released entirely between two polls.**
Whether the game sees it at all — and whether one poll or two land inside it —
depends on the *phase* of the press within the frame, which nothing controls. So
short holds are quantised and phase-dependent, which is exactly what "erratic and
non-monotonic" looks like.

**And it explains the one value that was reliable:** 80 ms spans ~2.5 frames, so
it is always caught by at least two polls, and the count varies by at most one
out of two-to-three. That is why 80 ms alone repeats to 1%.

⇒ **Hold duration is the wrong control variable.** The dossier's existing method
— *count PRESSES at the fixed 80 ms hold* — is therefore not a workaround around
a mystery; it is the correct way to drive a per-tick axis. The row is closed as
**explained**.

## 3. ⚠️ A tidier explanation that the data KILLED

Before measuring, the obvious candidate was **angle wrapping**. `alice_yaw_delta`
wraps each per-frame step into (−180, 180], and the code's own comment says the
cumulative total "is only valid while the camera turns LESS than 180 degrees in a
single frame" — with `dmax` printed precisely so a reader can check. A sign flip
(−168.7 at 40 ms, **+75.4** at 160 ms) is exactly what exceeding that looks like,
and this machine is deliberately low-powered, so long frames are plausible.

**`dmax` never exceeded 83° in the entire run** `[measured 2026-09-09]` — less
than half the limit, and 56.8° on the samples that actually moved. The unwrapper
was never near its ambiguous regime. **Wrapping is `[disproved 2026-09-09]` as
the cause**, and the instrument that disproved it was already in the log because
someone had the sense to print `dmax` in the first place.

Recorded because it was a good hypothesis and it was wrong, and the next person
to look at a sign flip will reach for it too.

---

## What is NOT established

- **The per-poll turn amount.** The observed single-window moves cluster at
  94.0 / 94.2 (the calibrated press, twice) and 75.1 / 77.9, with larger ones at
  168.7, 183.8 and 302.2. Those are consistent with a small integer number of
  polls, but the log does not record key-down timing, so the poll count per press
  cannot be recovered and the quantum is not pinned.
- **The +75.4° at 160 ms specifically.** Five frames should be sampled reliably,
  so phase alone does not obviously explain that one, and it is `n=1`. It may
  simply be a mis-timed press. Not explained; not important, because the method
  it would inform has been superseded.
- **That the frame period during the original hold experiment was 32.3 ms.** The
  log analysed is from the same session and machine, but the individual presses
  are not timestamped in it, so this is the session's *typical* period rather
  than the period during each press.

## What would change the answer

A hold of **≥ 500 ms** (15+ frames) should turn ~15× the per-poll amount with a
few-percent spread. If a long hold is *also* erratic, the sampling explanation is
wrong and something in `AbsoluteAxis=100`'s own behaviour is responsible. That is
one flat launch, and it is not worth one on its own — ride it along.
