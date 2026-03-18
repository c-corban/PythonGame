---
description: "Use when editing asset paths, image loading, asset_catalog.py, build_runtime_assets.py, runtime Images bundles, pygame initialization, display setup, or the paired client/server asset helper modules in Better-Together."
name: "Asset and runtime caveats"
applyTo: "src/better_together_client/assets.py, src/better_together_server/assets.py, src/better_together_shared/asset_catalog.py, src/better_together_shared/asset_pipeline.py, src/better_together_shared/assets_runtime.py, scripts/build_runtime_assets.py, assets/source/**, src/better_together_client/Images/**, src/better_together_server/Images/**, docs/assets-licenses.md, credits/**"
---

# Asset and runtime caveats

- Keep `src/better_together_client/assets.py` and `src/better_together_server/assets.py` behaviorally aligned unless a task explicitly requires divergence.
- Treat `src/better_together_shared/asset_catalog.py`, `src/better_together_shared/asset_pipeline.py`, and `scripts/build_runtime_assets.py` as part of the same asset packaging surface when runtime bundle layout or source selection changes.
- Preserve `resolve_asset_path()` semantics so both runtime halves continue to load assets relative to their own package/module directory.
- `load_image()` and `load_scaled_image()` currently rely on `lru_cache`; preserve or intentionally replace that caching behavior.
- The loaders now convert images only when a display surface exists. Preserve that headless-safe behavior unless a task explicitly requires otherwise.
- When changing asset sources or attributions, update `docs/assets-licenses.md` and the relevant file in `credits/`.
