# Phloem SDK for Python

Send readings from Python to [Phloem](https://phloem.ai). Each reading becomes
a named channel you can watch live, replay, chart and check, the same as one
from a connector.

```python
import phloem

with phloem.connect("hil-runner") as ph:
    ph.log_now("/rig/psi", 3.2)
```

## Install

```sh
pip install phloem        # or: uv add phloem
```

Python 3.9 or later. Wheels for Linux (x64, Arm64; including Alpine), macOS
(Apple silicon, Intel) and Windows (x64). Nothing else to install. Fully typed:
editors and type checkers see every call.

## Two ways to send

`connect` picks the way by whether it is given an API key.

| | Through Phloem on this machine | Straight to the cloud |
|---|---|---|
| **When** | no API key | an API key is set |
| **Needs** | Phloem Computer, or the Phloem service on a server; the program allowed once on **Inputs** | a workspace API key and your workspace's URL, both on the account page |
| **If the network drops** | nothing is lost: Phloem keeps the data on disk and uploads it later | data waits in memory (64 MiB by default) |
| **For** | test stands, anything with hardware | CI jobs, simulations, notebooks |

To send straight to the cloud, set the two values the account page shows
beside a new key, then run the same program:

```sh
export PHLOEM_URL=https://api.<your-environment>.phloem.ai
export PHLOEM_API_KEY=phla_…
```

or pass them: `phloem.connect("ci", url=..., api_key=...)`. `ph.route` says
which way the data is going.

## Sending

```python
import time
import phloem

with phloem.connect("bench-pc") as ph:
    # one reading, stamped now
    ph.log_now("/rig/psi", 3.2)

    # readings at their own time
    t0 = time.time_ns()
    ph.log("/rig/mode", t0, "source", "fire")
    ph.log_many("/rig/psi", "source", [t0, t0 + 1_000_000], [3.1, 3.2])

    # a fixed-rate signal: each block starts where the last one ended
    s = ph.stream(["/daq/ch0", "/daq/ch1"], "host", step_hz=1000)
    s.push({"/daq/ch0": ch0_block, "/daq/ch1": ch1_block})

    # say that data is missing from a point
    ph.gap(["/daq/ch0"], t0, "overrun")
```

| Call | What it does |
|---|---|
| `log_now(path, value)` | one reading, stamped with this machine's clock |
| `log(path, t_ns, basis, value)` | one reading at its own time |
| `log_many(path, basis, times_ns, values)` | many readings of one channel |
| `stream(paths, basis, step_hz=…)` then `push({path: block, …})` | a fixed-rate sender |
| `gap(paths, frontier_ns, detail)` | state that data is missing |
| `flush()` | send what is held now |
| `close()` | end the stream; raises if anything was not delivered |

**Values:** `float`, `int`, `bool` or `str`. **Paths** name channels:
`/rig/psi`.

**Timestamps** always say which clock they are on: `"host"` (this machine's),
`"source"` (your device's or recording's own) or `"backdated:<anchor_us>"` (a
recording replayed now). There is no default.

## Knowing nothing was lost

Leaving the `with` block (or `ph.close()`) waits for everything to be
delivered. If anything was not, it raises `phloem.UnsentError` with the exact
count of readings, so a CI job fails instead of passing silently.

| Exception | When |
|---|---|
| `phloem.UnsentError` | at close: something was not delivered |
| `PermissionError` | the key was refused or revoked, or the program is not allowed on this machine yet (the message says how to allow it) |
| `ConnectionError` | Phloem or the cloud could not be reached |
| `ValueError` | a call was wrong, for example an API key with no URL |

## Good to know

- **One program per name.** The name you pass is the program. A second
  program started under the same name takes over and the first one stops.
  Give parallel jobs their own names.
- **After a crash,** readings still in memory are lost. Do not send again what
  was already sent: it would be stored twice. Send through Phloem on the
  machine where that matters.
- **Version:** `phloem.__version__`. Every language's SDK is released at the
  same version.

## Documentation

https://phloem.ai/docs/sdk/ · runnable examples: [`examples/`](https://github.com/phloem-labs/phloem-py/tree/main/examples) · what changed in each version: [`CHANGELOG.md`](https://github.com/phloem-labs/phloem-py/blob/main/CHANGELOG.md).

## Support

Found a bug or need something? [Open an issue](https://github.com/phloem-labs/phloem-py/issues).

## Licence

Apache License 2.0.
