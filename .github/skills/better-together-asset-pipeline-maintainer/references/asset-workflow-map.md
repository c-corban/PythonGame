# Better-Together asset workflow map

## Source of truth

- `assets/source/` is the canonical editable asset tree.
- `src/better_together_client/Images/` and `src/better_together_server/Images/` are generated runtime bundles.
- `src/better_together_shared/asset_catalog.py` defines logical asset IDs, preferred inputs, and runtime output locations.
- `src/better_together_shared/asset_pipeline.py` and `scripts/build_runtime_assets.py` build or validate runtime outputs.

## Change types

### Source art change

- Update files under `assets/source/`.
- Rebuild bundles with `python scripts/build_runtime_assets.py`.
- Re-run validation with `python scripts/build_runtime_assets.py --check`.

### Asset catalog change

- Update `src/better_together_shared/asset_catalog.py`.
- Expect runtime bundle layout, source mapping, or build strategy to change.
- Rebuild generated outputs before tests.

### Asset pipeline change

- Update `src/better_together_shared/asset_pipeline.py` or `scripts/build_runtime_assets.py`.
- Review build strategies such as copy, scale by cells, scale to size, top-left transparency promotion, and server collision-mask generation.
- Check whether `--check`, `--strict-staleness`, or `--dry-run` behavior needs docs coverage.

### Loader behavior change

- Update `src/better_together_client/assets.py` and `src/better_together_server/assets.py` together unless divergence is intentional.
- Preserve path resolution relative to each package and headless-safe conversion behavior unless the task explicitly changes it.

## Important behaviors to preserve unless intentionally changed

- Client bundle keeps visual runtime art.
- Server bundle may store collision-oriented monochrome mask outputs for crew and obstacle assets.
- Logical asset IDs resolve through the shared catalog rather than raw hard-coded paths.
- Loaders use caching and only convert surfaces when a display surface exists.
