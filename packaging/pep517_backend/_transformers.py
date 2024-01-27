# -*- coding: utf-8 -*-

"""Data conversion helpers for the in-tree PEP 517 build backend."""

from itertools import chain


def _emit_opt_pairs(opt_pair):
    flag, flag_value = opt_pair
    flag_opt = '--{name!s}'.format(name=flag)
    if isinstance(flag_value, dict):
        sub_pairs = flag_value.items()
    else:
        sub_pairs = ((flag_value,),)

    yield from (
        '='.join(map(str, (flag_opt,) + pair))
        for pair in sub_pairs
    )


def get_cli_kwargs_from_config(kwargs_map):
    """Make a list of options with values from config."""
    return list(chain.from_iterable(map(_emit_opt_pairs, kwargs_map.items())))


def get_enabled_cli_flags_from_config(flags_map):
    """Make a list of enabled boolean flags from config."""
    return [
        '--{flag}'.format(flag=flag)
        for flag, is_enabled in flags_map.items()
        if is_enabled
    ]
