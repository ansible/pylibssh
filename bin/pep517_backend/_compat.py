# -*- coding: utf-8 -*-

"""Interpython compatibility shims."""

from __future__ import (  # noqa: WPS422
    absolute_import, division, print_function,
)

import sys
from functools import wraps as _stdlib_wraps


IS_PY2 = sys.version_info[0] == 2
IS_PY3 = not IS_PY2
IS_AT_LEAST_PY34 = sys.version_info >= (3, 4)


try:
    from inspect import signature  # noqa: WPS433
except ImportError:
    # Python < 3.3
    from funcsigs import signature  # noqa: WPS433, WPS440


if IS_AT_LEAST_PY34:  # `__wrapped__` added in 3.4
    wraps = _stdlib_wraps
else:
    @_stdlib_wraps(_stdlib_wraps)
    def wraps(wrapped, *args, **kwargs):  # noqa: WPS440
        """Copy some of the original function attributes into a wrapper."""
        def wrapper_func(func):  # noqa: WPS430
            func = _stdlib_wraps(wrapped, *args, **kwargs)(func)
            func.__wrapped__ = wrapped  # noqa: WPS609

            return func

        return wrapper_func

    wraps.__doc__ = _stdlib_wraps.__doc__


__metadata__ = type  # pylint: disable=invalid-name  # make classes new-style


# NOTE: Keep the parentheses until `flake8-rst-docstrings` is fixed.
# Ref: https://github.com/peterjc/flake8-rst-docstrings/issues/24
__all__ = ('signature', 'wraps')  # noqa: WPS410  # explicit re-export
