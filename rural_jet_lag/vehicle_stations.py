"""Console-script entry point for `uv run vehicle-stations`.

The actual implementation lives at `tools/generate_vehicle_stations.py`.
This is a thin shim so the script is reachable from the repo root via the
uv-registered console command.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "tools"
    / "generate_vehicle_stations.py"
)


def main() -> None:
    if not SCRIPT_PATH.is_file():
        raise FileNotFoundError(f"expected script at {SCRIPT_PATH}")
    sys.argv[0] = "vehicle-stations"
    module_name = "_generate_vehicle_stations"
    spec = importlib.util.spec_from_file_location(module_name, SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load {SCRIPT_PATH}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod  # required for dataclasses to resolve types
    spec.loader.exec_module(mod)
    sys.exit(mod.main())
