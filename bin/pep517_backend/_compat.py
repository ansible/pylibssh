# -*- coding: utf-8 -*-

"""Interpython compatibility shims."""

from __future__ import (  # noqa: WPS422
    absolute_import, division, print_function,
)


try:
    from inspect import signature  # noqa: WPS433
except ImportError:
    # Python < 3.3
    from funcsigs import signature  # noqa: WPS433, WPS440


__metadata__ = type  # pylint: disable=invalid-name  # make classes new-style


__all__ = ('signature', )  # noqa: WPS410  # explicit re-export
