# -*- coding: utf-8 -*-

"""PEP 517 build backend pre-building Cython exts before setuptools."""

from __future__ import (  # noqa: WPS422
    absolute_import, division, print_function,
)

from ._backend import (  # noqa: WPS436  # Re-exporting PEP 517 hooks
    build_sdist, build_wheel, get_requires_for_build_sdist,
    get_requires_for_build_wheel, prepare_metadata_for_build_wheel,
)


__all__ = (  # noqa: WPS317, WPS410
    'build_sdist', 'build_wheel', 'get_requires_for_build_sdist',
    'get_requires_for_build_wheel', 'prepare_metadata_for_build_wheel',
)


__metadata__ = type  # pylint: disable=invalid-name  # make classes new-style
