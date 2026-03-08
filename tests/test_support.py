import os
import sys
from pathlib import Path


os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"


def add_workspace_package_paths():
    for path in reversed((SRC_DIR,)):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))


def build_workspace_pythonpath(*paths):
    package_paths = []
    for path in (*paths, SRC_DIR):
        path_string = str(path)
        if path_string not in package_paths:
            package_paths.append(path_string)

    existing_path = os.environ.get("PYTHONPATH")
    if existing_path:
        package_paths.append(existing_path)

    return os.pathsep.join(package_paths)
