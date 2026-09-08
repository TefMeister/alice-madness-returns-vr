# The XInput proxy is an instrument first, an injector second

`/pd`, dev PC, 2026-09-08b. **The game was not launched. Nothing in this note has been run.**

Source: `staging/alice-madness-returns-vr/proxy-xinput/`. Deployed `xinput1_3.dll` md5 `26764e15…`,
60,416 B, into `Binaries\Win32\`.

## The row, and why it existed

Yesterday's session established from the import table that camera route 3 — a virtual gamepad — was
**not** blocked after all. Two research drops had recorded it as untestable on this machine because
the dev PC's **ViGEm bus** is in an Error state. That is true of a ViGEm *virtual device*, and
irrelevant here: `AliceMadnessReturns.exe` imports `XINPUT1_3.dll` **by ordinal 2 and 3**, so a
**proxy** fabricates a pad *inside the process* — no bus, no driver, no virtual device, nothing for a
broken ViGEm instance to break. `[verified-numerically 2026-09-08]`

I queued it rather than starting it at the end of that session. This is it.

## What it is, in priority order

**An instrument first.** The open question is not "can we fabricate a pad" — it is **whether Alice
polls XInput at all**. Importing a DLL is not calling it, and there is a first-party precedent for
exactly that gap: `prince-of-persia-2008-vr` imports the same DLL the same way, its proxy loads
cleanly, and that game was **never once observed calling `XInputGetState`**.

So the proxy counts **entries** into all three exports and prints a verdict on unload, whether or not
anything is ever injected:

| verdict | meaning here |
| --- | --- |
| `NEVER CALLED` | Alice does not poll XInput on this path — **route 3 is dead for this game** |
| `CALLED BUT NEVER FOR PAD 0` | it polls other indices only |
| `CALLED FOR PAD 0 BUT OUR APPLY DECLINED` | our side; the log names which precondition failed |
| `INJECTED` | the pad path works and route 3 is live |

`applied_pad` alone could not tell the first from the third, and only the first is a fact about the
game. The sibling project shipped a counter that could not make that distinction and spent a launch
on an uninterpretable zero; that lesson is carried over rather than re-learned.

**An injector second, defaulting OFF.** Nothing is fabricated until a harness sets `enabled` in the
shared block, so deploying this changes no behaviour on its own.

## Deliberately its own namespace

The sibling proxy uses `Local\pop2008_vr_input`. If this one reused that name and both games ran, the
two would share one block and **each would drive the other's pad** — which would present as a game
behaviour, not as a bug. So the shared-memory name (`Local\alice_vr_pad`), the magic (`ALIP`) and
every symbol are Alice's alone.

The cost is real and worth stating: the pad logic now exists twice on the estate. The alternative was
a silent cross-game coupling, and a test asserts the two differ so a future copy-paste cannot
reintroduce it.

## Verification

- Builds clean under `-Wall -Wextra`, PE32/i386. `[compile-verified 2026-09-08]`
- **Export table pins ordinals 2, 3, 4** — Alice imports 2 and 3 *by ordinal*, so a name-only table
  would not resolve and the game would fail to start. 4 is exported although unimported, for a caller
  that reaches it via `GetProcAddress`.
- **The proxy does not import xinput at all** (`KERNEL32` + UCRT only), so it cannot recurse into
  itself; the real DLL is loaded by full system path, with `xinput1_4.dll` as the documented
  ABI-compatible fallback. `[verified-numerically 2026-09-08]`
- Host suite **43 checks, 0 failures**, linking the shipped `pad_inject.c`. It covers the refusals
  rather than just the happy path: disabled and bad-magic are **bit-for-bit** no-ops, a fabricated
  state starts clean rather than ORing into whatever a failed call left behind, injection is additive
  over a real pad, NULLs are handled, the packet number advances on every apply, and every verdict
  row including the impossible ones. `[verified-numerically 2026-09-08]`

**Nothing here has been run in the game.**

### Two details that would have been silent failures

- **The packet number must advance.** A game that compares `dwPacketNumber` treats an unchanged one
  as stale and ignores the entire state — which would look exactly like "injection does not work on
  this game". Asserted by its own test.
- **A fabricated state starts clean.** When the real call failed, whatever it left in the buffer is
  undefined; ORing into it would fabricate buttons nobody asked for. Also asserted.

## Deployment and reverting

`xinput1_3.dll` is a **new file** in `Binaries\Win32\` — nothing was overwritten, so there is no
backup to keep and **reverting is deleting that one file**. It is a second, independent proxy slot
alongside our existing `d3d9.dll`; the two share no state, and removing one leaves the other
untouched. `deployed.sh` now records both.

## The next launch

No setup. Launch, reach gameplay, quit, then read `alice_xinput_log.txt` beside the exe.

| the log says | what it means |
| --- | --- |
| no `ENTERED` line, `VERDICT: NEVER CALLED` | **Route 3 is dead on this game.** Camera control falls to routes 1, 2 and 4 — and route 1 (`bugit`) is already the top `[FLAT]` row, so this costs nothing extra to learn. |
| `XInputGetCapabilities ENTERED` but no `GetState` | the game probes for a pad, is told there is none, and gives up. `pad_force=1` should then be enough, and that is a one-flag retest rather than new code. |
| `GetState ENTERED`, `VERDICT: DECLINED` | expected on the first launch, because injection defaults off — but the entry count is the answer we came for: **Alice polls XInput**, and route 3 is live. |
| `VERDICT: INJECTED` | only possible once a harness enables the block. |

⚠️ One launch answers this **and** the `bugit` row at the same time; they touch different mechanisms
and neither disturbs the other.

## What is NOT established

- Whether Alice polls XInput. **That is the question**, and it is untested.
- Whether a fabricated pad drives the camera even if it is polled. Being seen and being *acted on*
  are different, and the `/sr` drop's test-design warning applies directly: a sibling's first
  injection test ran at a title screen that polls no input at all, and every negative from it was
  worthless because it could not have gone positive. **Test in gameplay, not at a menu.**
- Whether the UCRT imports matter on this machine. They resolve on Windows 10 and the sibling proxy
  uses the same toolchain in the same game folder shape, but that is an inference from a sibling,
  not a measurement here. `[inferred-static]`
