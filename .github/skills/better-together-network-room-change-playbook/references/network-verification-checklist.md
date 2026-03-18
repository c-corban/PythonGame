# Better-Together network verification checklist

## Automated checks

- `tests/test_protocol.py` for snapshot/message helpers and normalized payload behavior.
- `tests/test_transport.py` for framing and message-size behavior.
- `tests/test_client_network.py` for connect/send/update handling on the client.
- `tests/test_server_network.py` for server networking helpers.
- `tests/test_room_manager.py` for room assignment, slot reuse, and cleanup behavior.
- `tests/test_server_game.py` and `tests/test_server_ai.py` when room simulation or entity ownership changes.
- `tests/test_server_protocol.py` for the live handshake, malformed update rejection, disconnect logging, and room cleanup flow.

## Live integration notes

- `tests/test_server_protocol.py` starts a real server process and waits for log lines such as `Waiting for connections`, `Lost connection with`, and `Closed room with ID: 0`.
- The live integration test may skip if the default port is already in use.
- `tests/test_support.py` is the model for dummy SDL setup and workspace `PYTHONPATH` handling in tests.

## Manual multiplayer follow-up

- Connect multiple clients and confirm later joins reuse AI slots before creating a new room.
- Disconnect a client and confirm its slot returns to AI.
- Confirm a room with only AI slots left is deleted.

## Docs to update

- Update `docs/architecture.md` whenever protocol flow, room lifecycle, or state ownership changes.
- Update `README.md` or `docs/quickstart.md` when launch/setup expectations change with the networking change.
