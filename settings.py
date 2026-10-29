"""Settings used by the code: config.example.py, overridden by your config.py.

config.py is optional and ignored by git, so a fresh clone works without it.
"""

import runpy
from pathlib import Path

ROOT = Path(__file__).parent


def load(example: Path, user: Path) -> dict:
    """UPPER_CASE values from `example`, replaced by those in `user` if it exists."""
    values = runpy.run_path(str(example))
    if user.exists():
        values.update(runpy.run_path(str(user)))
    return {k: v for k, v in values.items() if k.isupper()}


def describe(user: Path) -> str:
    """Which file the settings come from, for the --test summary."""
    if user.exists():
        return f"{user.name} (missing values from config.example.py)"
    return "config.example.py only (no config.py; copy it to config.py to change settings)"


globals().update(load(ROOT / "config.example.py", ROOT / "config.py"))
SOURCE = describe(ROOT / "config.py")
