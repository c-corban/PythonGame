---
name: better-together-asset-pipeline-maintainer
description: 'Use when reviewing or planning Better-Together asset sources, asset_catalog.py, runtime Images bundles, build_runtime_assets.py, asset attributions, or mirrored client/server asset loader behavior.'
argument-hint: 'Describe the asset change, bundle issue, or asset-pipeline files involved.'
---

# Better-Together Asset Pipeline Maintainer

## When to Use

- Adding, replacing, or resizing runtime art.
- Editing `assets/source/`, `src/better_together_shared/asset_catalog.py`, `src/better_together_shared/asset_pipeline.py`, or the generated `src/better_together_*/Images/` bundles.
- Fixing asset-loading or attribution drift between client and server runtimes.

## Procedure

1. Start with the [asset workflow map](./references/asset-workflow-map.md). Treat `assets/source/` as canonical and the package-local `Images/` trees as generated outputs.
2. Decide whether the change is a source-art change, asset-catalog change, pipeline change, or loader-behavior change. Keep `src/better_together_client/assets.py` and `src/better_together_server/assets.py` behaviorally aligned unless the task explicitly needs divergence.
3. When source art or the asset catalog changes, rebuild or validate bundles from the repository root with the documented asset commands described in the references.
4. If the change affects runtime bundle contents or loader expectations, use the [asset verification and doc sync guide](./references/asset-verification-and-doc-sync.md) to run the right tests and update attribution/docs in the same branch.
5. Summarize what changed in the source tree, what changed in generated outputs, and whether docs or credits were updated.

## References

- [Asset workflow map](./references/asset-workflow-map.md)
- [Asset verification and doc sync](./references/asset-verification-and-doc-sync.md)
