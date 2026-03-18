# Better-Together runtime smoke checklist

## Pre-flight

- Run the automated baseline first unless the user explicitly wants a narrower validation pass.
- The server is headless-capable, but it still depends on Pygame asset loading.
- The client requires a graphical desktop session.

## Manual smoke flow

1. Start `python -m better_together_server` and wait for `Waiting for connections`.
2. Start `python -m better_together_client` and confirm the client connects without an immediate error.
3. Move with `WASD` or the arrow keys.
4. Confirm the HUD still renders inventory counters.
5. Confirm repair and cannon prompts appear in the expected deck zones.
6. Close the client and confirm the server logs the disconnect.

## Extra checks for networking or room changes

1. Connect multiple clients.
2. Verify later joins reuse AI-controlled slots before creating a new room.
3. Verify a disconnected player slot returns to AI.
4. Verify an empty room is deleted.

## Reporting

- Say whether the smoke test was run locally, partially verified, or still requires human confirmation.
- Call out any skipped steps caused by environment limits such as no graphical desktop session.
