"""Server CLI bootstrap for Better Together."""

import os


RUNTIME_ROLE_ENV_VAR = "BETTER_TOGETHER_RUNTIME_ROLE"
SERVER_RUNTIME_ROLE = "server"


def main():
    os.environ.setdefault(RUNTIME_ROLE_ENV_VAR, SERVER_RUNTIME_ROLE)

    from .app import main as app_main

    app_main()


__all__ = ["main"]


if __name__ == "__main__":
    main()
