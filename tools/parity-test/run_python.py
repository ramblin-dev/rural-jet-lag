"""Capture / re-run the Python baseline for the JS-vs-Python parity test.

Shells out to the ``vehicle-stations`` CLI with a fixed polygon, fixed args,
and the snapshotted Overpass fixture in ``./fixtures``. Writes deterministic
output filenames (no timestamp) to ``./baseline``.

First run (with empty ``fixtures/``): hits Overpass twice (POIs + water) and
saves both responses into ``fixtures/`` so subsequent runs are reproducible.
Subsequent runs read from the fixtures and never touch the network.

The JS-side parity test mirrors this script's args exactly, with a
``js-sioux`` name prefix instead of ``python-sioux``; the two baselines are
then diff'd to catch algorithmic drift between implementations.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent


def main() -> int:
    cmd = [
        "uv", "run", "vehicle-stations",
        "--polygon-file", str(HERE / "polygon.geojson"),
        "--name", "python-sioux",
        "--overpass-fixture-dir", str(HERE / "fixtures"),
        "--output-dir", str(HERE / "baseline"),
        "--no-timestamp",
        # Pin every tunable so the baseline is independent of code-default drift.
        "--min-station-spacing-m", "300",
        "--density-radius-m", "1609",
        "--playing-hours", "7am-7pm",
        "--playing-days-of-week", "sat,sun",
        # Let game-size auto-infer from polygon area (exercises the area code path
        # incl. water subtraction). Let the cap auto-tune for the same reason.
    ]
    print("Running:", " ".join(cmd), file=sys.stderr)
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


if __name__ == "__main__":
    sys.exit(main())
