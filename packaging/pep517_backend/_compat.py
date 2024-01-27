"""Cross-interpreter compatibility shims."""

import os
import typing as t  # noqa: WPS111
from contextlib import contextmanager
from pathlib import Path


try:
    from contextlib import chdir as chdir_cm  # noqa: WPS433
except ImportError:

    @contextmanager  # type: ignore[no-redef]
    def chdir_cm(path: os.PathLike) -> t.Iterator[None]:  # noqa: WPS440
        """Temporarily change the current directory, recovering on exit."""
        original_wd = Path.cwd()
        os.chdir(path)
        try:  # noqa: WPS505
            yield
        finally:
            os.chdir(original_wd)


try:
    # Python 3.11+
    from tomllib import loads as load_toml_from_string  # noqa: WPS433
except ImportError:
    # before Python 3.11
    from tomli import loads as load_toml_from_string  # noqa: WPS433, WPS440


__all__ = ('chdir_cm', 'load_toml_from_string')  # noqa: WPS410
