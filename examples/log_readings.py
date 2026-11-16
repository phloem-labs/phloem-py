"""Send a few readings through Phloem on this machine (Phloem Computer, or the
Phloem service on a server). The first run is refused until the program is
allowed on Inputs; the error says how.

    python examples/log_readings.py
"""

import math
import time

import phloem

with phloem.connect("example-readings") as ph:
    ph.declare([{"path": "/example/psi", "unit": "psi"}])
    for i in range(50):
        ph.log_now("/example/psi", 3.0 + 0.2 * math.sin(i / 5))
        ph.log_now("/example/ok", i % 10 != 0)
        time.sleep(0.1)
    print(f"sent 100 readings by the {ph.route} route")
