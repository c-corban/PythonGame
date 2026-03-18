---
description: "Use when editing Better-Together player snapshots, player.py state fields, snapshot serialization, char asset IDs, or compatibility between client/server player state and the shared protocol."
name: "Player snapshot compatibility guardrails"
applyTo: "src/better_together_client/player.py, src/better_together_server/player.py, src/better_together_shared/protocol.py"
---
# Player snapshot compatibility guardrails

- Treat `src/better_together_client/player.py`, `src/better_together_server/player.py`, and `src/better_together_shared/protocol.py` as one compatibility seam.
- When adding, removing, renaming, or retyping snapshot-backed fields, update both runtime player classes and the shared snapshot helpers together.
- Preserve the logical `char` asset-ID contract unless the task explicitly changes how runtime asset resolution works everywhere.
- Do not change only the local player class and assume networking will adapt automatically; `create_player_snapshot()`, `create_player_from_snapshot()`, `apply_player_snapshot()`, and the `extract_*` helpers must stay compatible.
- Validate snapshot-shape changes with `tests/test_protocol.py`, then add client/server network coverage when the new field crosses the live socket boundary.
- If the wire-visible player state changes, update `docs/architecture.md` in the same branch.
