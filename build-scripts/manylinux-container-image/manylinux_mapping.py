#! /usr/bin/env python3.9
"""A helper script for producing dual aliased tags."""

import platform
import sys


ARCH = platform.machine()


TAG_ARCH_SEP = '_'


ML_LEGACY_TO_MODERN_MAP = {  # noqa: WPS407
    TAG_ARCH_SEP.join(('manylinux1', ARCH)): 'manylinux_2_5',
    TAG_ARCH_SEP.join(('manylinux2010', ARCH)): 'manylinux_2_12',
    TAG_ARCH_SEP.join(('manylinux2014', ARCH)): 'manylinux_2_17',
}


def to_modern_manylinux_tag(legacy_manylinux_tag):
    """Return a modern alias for the tag if it exists."""
    try:
        return '_'.join((
            ML_LEGACY_TO_MODERN_MAP[legacy_manylinux_tag],
            ARCH,
        ))
    except KeyError:
        return legacy_manylinux_tag


def make_aliased_manylinux_tag(manylinux_tag):
    """Produce a dual tag if it has a modern alias."""
    modern_tag = to_modern_manylinux_tag(manylinux_tag)

    if modern_tag != manylinux_tag:
        manylinux_tag = '.'.join((modern_tag, manylinux_tag))

    return manylinux_tag


if __name__ == '__main__':
    print(make_aliased_manylinux_tag(sys.argv[1]))  # noqa: WPS421
