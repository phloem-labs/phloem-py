"""A fixed-rate signal, the way a data-acquisition loop sends one: blocks of
samples at 1 kHz, each placed where the last one ended.

    python examples/fixed_rate.py
"""

import math

import phloem

RATE_HZ = 1000
BLOCK = 100  # samples per block: 0.1 s

with phloem.connect("example-daq") as ph:
    stream = ph.stream(["/daq/ch0", "/daq/ch1"], "host", step_hz=RATE_HZ)
    n = 0
    for _ in range(20):  # two seconds of data
        ch0 = [math.sin(2 * math.pi * 5 * (n + i) / RATE_HZ) for i in range(BLOCK)]
        ch1 = [math.cos(2 * math.pi * 5 * (n + i) / RATE_HZ) for i in range(BLOCK)]
        stream.push({"/daq/ch0": ch0, "/daq/ch1": ch1})
        n += BLOCK
    print(f"sent {n} samples per channel")
