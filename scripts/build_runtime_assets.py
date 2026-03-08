#!/usr/bin/env python3
"""Build or validate Better Together runtime asset bundles from the shared catalog."""

from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from better_together_shared.asset_pipeline import main


if __name__ == "__main__":
    raise SystemExit(main())
