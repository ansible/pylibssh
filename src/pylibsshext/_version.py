# -*- coding: utf-8 -*-

"""Version definition."""

from ._libssh_version import (  # noqa: N811, WPS300, WPS436
    LIBSSH_VERSION as __libssh_version__,
)


try:
    from ._scm_version import (  # noqa: WPS300, WPS433, WPS436
        version as __version__,
    )
except ImportError:
    from pkg_resources import get_distribution as _get_dist  # noqa: WPS433
    __version__ = _get_dist('ansible-pylibssh').version  # noqa: WPS440


__full_version__ = (
    '<pylibsshext v{wrapper_ver!s} with libssh v{backend_ver!s}>'.
    format(wrapper_ver=__version__, backend_ver=__libssh_version__)
)
__version_info__ = tuple(
    (int(chunk) if chunk.isdigit() else chunk)
    for chunk in __version__.split('.')
)
