# -*- coding: utf-8 -*-

"""Data conversion helpers for the in-tree PEP 517 build backend."""

from __future__ import (  # noqa: WPS422
    absolute_import, division, print_function,
)

from functools import partial
from itertools import chain

from ._compat import signature, wraps  # noqa: WPS436


__metadata__ = type  # pylint: disable=invalid-name  # make classes new-style


def _emit_opt_pairs(opt_pair):
    flag, flag_value = opt_pair
    flag_opt = '--{name!s}'.format(name=flag)
    if isinstance(flag_value, dict):
        sub_pairs = flag_value.items()
    else:
        sub_pairs = ((flag_value,),)

    for pair in sub_pairs:  # noqa: WPS526
        yield '='.join(map(str, (flag_opt,) + pair))


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


def _map_args_to_kwargs(func_sig, args, kwargs):
    """Return all positional args converted into keyword-args."""
    return dict(kwargs, **func_sig.bind(*args, **kwargs).arguments)


def convert_to_kwargs_only(orig_func):
    """Ensure a given function is called with kwargs only."""
    orig_func_signature = signature(orig_func)
    map_args_to_kwargs = partial(_map_args_to_kwargs, orig_func_signature)

    @wraps(orig_func)  # noqa: WPS210, WPS430
    def func_wrapper(*args, **kwargs):  # noqa: WPS210, WPS430
        # NOTE: `pep517` lib calls PEP 517 hooks with positional arguments
        # NOTE: making it harder to extract certain args by their names.
        # NOTE: This is why we map all args to kwargs and pass them like
        # NOTE: that further.
        # Ref: https://github.com/pypa/pep517/issues/115
        kwargs = map_args_to_kwargs(args, kwargs)
        del args  # Prevent accidental `args` var usage  # noqa: WPS420

        return orig_func(**kwargs)

    return func_wrapper
