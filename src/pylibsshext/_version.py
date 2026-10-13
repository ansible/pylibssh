"""Version definition."""

from ._libssh_version import (  # noqa: N811, WPS300
    LIBSSH_VERSION as __libssh_version__,
)


try:
    from ._scm_version import version as __version__  # noqa: WPS300
except ImportError:
    from importlib.metadata import version as _get_dist_version

    __version__ = _get_dist_version('ansible-pylibssh')


__full_version__ = (
    f'<pylibsshext v{__version__!s} with libssh v{__libssh_version__!s}>'
)
__version_info__ = tuple(
    (int(chunk) if chunk.isdigit() else chunk)
    for chunk in __version__.split('.')
)


__all__ = (  # noqa: WPS410
    '__full_version__',
    '__libssh_version__',
    '__version__',
    '__version_info__',
)
