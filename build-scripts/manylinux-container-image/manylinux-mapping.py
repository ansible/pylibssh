#! /usr/bin/env python3.9

import platform
import sys


ARCH = platform.machine()


ML_LEGACY_TO_MODERN_MAP = {
    '_'.join(('manylinux1', ARCH)): 'manylinux_2_5',
    '_'.join(('manylinux2010', ARCH)): 'manylinux_2_12',
    '_'.join(('manylinux2014', ARCH)): 'manylinux_2_17',
}


def to_modern_manylinux_tag(legacy_manylinux_tag):
    try:
        return '_'.join((
            ML_LEGACY_TO_MODERN_MAP[legacy_manylinux_tag],
            ARCH,
        ))
    except KeyError:
        return legacy_manylinux_tag


def make_aliased_manylinux_tag(manylinux_tag):
    modern_tag = to_modern_manylinux_tag(manylinux_tag)

    if modern_tag != manylinux_tag:
        manylinux_tag = '.'.join((modern_tag, manylinux_tag))

    return manylinux_tag


if __name__ == '__main__':
    print(make_aliased_manylinux_tag(sys.argv[1]))
