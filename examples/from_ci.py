"""Send a CI job's results straight to the cloud: no Phloem on the machine,
just the two values the account page shows beside a new API key.

    export PHLOEM_URL=https://api.<your-environment>.phloem.ai
    export PHLOEM_API_KEY=phla_...
    python examples/from_ci.py

Closing waits for the cloud to confirm every reading and raises
phloem.UnsentError if any was not, so the job fails instead of passing
silently.
"""

import time

import phloem

results = {"/ci/build_s": 182.4, "/ci/tests_failed": 0, "/ci/passed": True}

with phloem.connect("ci-nightly") as ph:
    assert ph.route == "direct", "set PHLOEM_URL and PHLOEM_API_KEY"
    now = time.time_ns()
    for path, value in results.items():
        ph.log(path, now, "host", value)
print("delivered")
