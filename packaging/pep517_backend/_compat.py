"""Cross-python stdlib shims."""

from __future__ import annotations

import os
import sys
import typing as _t
from contextlib import contextmanager
from pathlib import Path


if _t.TYPE_CHECKING:
    from collections import abc as _c


if sys.version_info >= (3, 11):
    from contextlib import chdir as chdir_cm

    from tomllib import loads as load_toml_from_string
else:
    from tomli import loads as load_toml_from_string

    @contextmanager
    def chdir_cm(path: str | os.PathLike[str]) -> _c.Iterator[None]:
        """Temporarily change the current directory, recovering on exit."""
        original_wd = Path.cwd()
        os.chdir(path)
        try:  # noqa: WPS505
            yield
        finally:
            os.chdir(original_wd)


__all__ = (  # noqa: WPS410
    'chdir_cm',
    'load_toml_from_string',
)
