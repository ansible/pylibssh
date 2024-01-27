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
    from contextlib import nullcontext as nullcontext_cm  # noqa: F401, WPS433
except ImportError:

    @contextmanager  # type: ignore[no-redef]
    def nullcontext_cm(  # noqa: WPS440
            enter_result: t.Any = None,  # noqa: WPS318
    ) -> t.Iterator[t.Any]:
        """Emit the incoming value.

        A no-op context manager.
        """
        yield enter_result


try:
    # Python 3.11+
    from tomllib import loads as load_toml_from_string  # noqa: WPS433
except ImportError:
    # before Python 3.11
    from tomli import loads as load_toml_from_string  # noqa: WPS433, WPS440


__all__ = (  # noqa: WPS410
    'chdir_cm',
    'load_toml_from_string',
    'nullcontext_cm',
)
