# Better-Together asset verification and doc sync

## Automated checks

- If `assets/source/` or `src/better_together_shared/asset_catalog.py` changed, run `python scripts/build_runtime_assets.py` before tests.
- Validate generated outputs with:
  - `python scripts/build_runtime_assets.py --check`
- Targeted tests:
  - `tests/test_asset_catalog.py`
  - `tests/test_asset_pipeline.py`
  - `tests/test_assets.py`

## What the tests cover

- `tests/test_asset_pipeline.py` checks build task selection, scaling strategies, transparency handling, server collision masks, stale output detection, and generated image expectations.
- `tests/test_assets.py` checks client/server loader symmetry, logical asset ID resolution, caching, absolute/relative path handling, and headless-safe conversion behavior.

## Useful command nuances

- `python scripts/build_runtime_assets.py --dry-run` prints the build plan without writing files.
- `python scripts/build_runtime_assets.py --check --strict-staleness` can catch outputs older than their preferred sources.

## Docs and credits to update

- Update `docs/assets-licenses.md` when attribution or asset inventory changes.
- Update the matching file in `credits/` when source attribution changes.
- Update `docs/architecture.md` if runtime bundle behavior or client/server asset-role differences change.
- Update `README.md` or `docs/quickstart.md` if the source-of-truth or asset-generation workflow changes.

## Reporting

- Call out whether regenerated runtime outputs were produced.
- Distinguish canonical source changes from generated bundle changes in your summary.
