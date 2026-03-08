# Quickstart

This guide is the fastest safe path to running the current prototype locally.

## Prerequisites

- Python 3
- `pygame`
- A graphical desktop session capable of opening Pygame windows for the **client**

Examples below use `python`. If your machine exposes Python as `python3`, use that command instead.

## Install dependencies

For a full local development checkout, install the repository from the repository root:

```bash
python -m pip install -e .
```

For a split deployment on separate computers, check out the repository on each machine, install it from the repository root, and run only the role that machine needs.

## Run automated checks

Before launching the prototype for code changes, run the lightweight automated baseline from the repository root:

```bash
python scripts/build_runtime_assets.py --check
python -m unittest discover -s tests -v
```

These tests currently cover server room invariants, mirrored asset-helper behavior, shared protocol helpers, package entrypoint import safety, and a basic live server handshake / cleanup flow. They do **not** replace runtime smoke testing for rendering or full gameplay input.

If you change `src/better_together_shared/asset_catalog.py` or any runtime image source files, regenerate the package-local runtime bundles before running the tests:

```bash
python scripts/build_runtime_assets.py
```

Canonical checked-in asset masters now live under `assets/source/`; the generator refreshes the package-local `src/better_together_client/Images/` and `src/better_together_server/Images/` runtime bundles from that source tree.

## Launch order

If the client and server will run on different computers, set the host values in `src/better_together_server/.env` and `src/better_together_client/.env` first. The runtime reads these settings:

- `BETTER_TOGETHER_SERVER_BIND_HOST` — where the server socket binds.
- `BETTER_TOGETHER_SERVER_BIND_PORT` — which port the server listens on.
- `BETTER_TOGETHER_CLIENT_SERVER_HOST` — where the client tries to connect.
- `BETTER_TOGETHER_CLIENT_SERVER_PORT` — which port the client tries to connect to.

For normal development, edit the role-specific file for the runtime you are launching. The package-local files are the preferred configuration surface.

Start the server first:

```bash
python -m better_together_server
```

On macOS, you can now double-click `Launch Better Together Server.command` from the repository root to do the same thing without opening a terminal yourself.

Then start the client:

```bash
python -m better_together_client
```

On macOS, you can instead double-click `Launch Better Together Client.command` from the repository root after the server is already running.

If the client cannot connect, it exits with a clear message telling you to start the server entrypoint first.

The package entrypoints above are the preferred launch path.

The macOS `.command` launchers prefer the repository `.venv` when it exists, fall back to `python3` / `python` when it does not, prepend `src/` to `PYTHONPATH` for raw-checkout launches, and set `BETTER_TOGETHER_ENV_FILE` to `src/better_together_server/.env` or `src/better_together_client/.env` automatically when those role-specific files exist.

Internally, the canonical runtime now lives in `src/better_together_client/`, `src/better_together_server/`, and `src/better_together_shared/`.

## What to expect

- By default the server listens on `localhost:2911`, but the bind host/port and client target host/port can now be configured separately through `src/better_together_server/.env` and `src/better_together_client/.env`.
- The server now runs headlessly; it does not open a gameplay or helper window.
- The client opens the main game window titled **Better Together**.
- A successful connection immediately assigns the client one crew slot and begins frame-by-frame snapshot exchange with the server.

## Manual smoke test

Use this checklist after the automated tests pass whenever setup changes, doc updates that affect run instructions, or gameplay changes need a quick sanity pass.

1. Start `python -m better_together_server` and confirm it prints `Waiting for connections`.
2. Start `python -m better_together_client` and confirm the game window opens without an immediate connection error.
3. Move with `WASD` or the arrow keys.
4. Confirm the HUD shows wood and cannonball inventory counters.
5. Walk near a cannon position and confirm the “Hold SPACE” prompts appear.
6. Close the client and confirm the server logs a lost connection.

Optional multiplayer check:

1. Start the server.
2. Launch more than one client instance.
3. Confirm later clients join existing rooms while AI-controlled slots are still available.

## Current limitations

- Networking now supports separate bind and connect settings, but it still assumes a trusted LAN-style setup and manual host configuration.
- Networking now uses simple length-prefixed framing around `pickle` payloads plus basic message/snapshot validation, but it still assumes a trusted LAN-style setup and is not hardened for hostile clients.
- Automated tests cover server room invariants, mirrored asset helpers, and a basic live protocol flow, but manual smoke tests still matter for rendering and full gameplay behavior.
- The server is now headless-capable, but its collision logic still relies on runtime image loading from the server asset tree.
- Runtime asset bundles are now described by `src/better_together_shared/asset_catalog.py` and can be rebuilt or validated with `scripts/build_runtime_assets.py`.

For the deeper architecture behind these limitations, see [`architecture.md`](architecture.md).
