# -*- coding: utf-8 -*-

"""PEP 517 build backend pre-building Cython exts before setuptools."""

from contextlib import suppress as _suppress

# Re-exporting PEP 517 hooks
# pylint: disable-next=unused-wildcard-import,wildcard-import
from setuptools.build_meta import *  # noqa: E501, F403, WPS347

# Re-exporting PEP 517 hooks
from ._backend import (  # type: ignore[assignment]  # noqa: WPS436
    build_sdist, build_wheel, get_requires_for_build_wheel,
    prepare_metadata_for_build_wheel,
)


with _suppress(ImportError):  # Only succeeds w/ setuptools implementing PEP 660
    # Re-exporting PEP 660 hooks
    from ._backend import (  # type: ignore[assignment]  # noqa: WPS433, WPS436
        build_editable, get_requires_for_build_editable,
        prepare_metadata_for_build_editable,
    )
