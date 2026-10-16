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


globals().update(load(ROOT / "config.example.py", ROOT / "config.py"))
