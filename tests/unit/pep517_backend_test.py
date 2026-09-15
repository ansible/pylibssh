"""Tests for the in-tree PEP 517 build backend."""

import os
import shlex
import sys
import sysconfig

import pytest

from pep517_backend._cython_configuration import patched_env


TRACE_MACRO = '-DCYTHON_TRACE_NOGIL=1'


@pytest.mark.parametrize('tracing', (True, False))
def test_tracing_macro_goes_through_cppflags(monkeypatch, tracing):
    """Append the macro to CPPFLAGS and leave CFLAGS alone.

    A CFLAGS environment variable replaces the interpreter's own compiler
    flags in setuptools' distutils, which silently drops -O3 from the
    build, while CPPFLAGS is appended to them.
    """
    monkeypatch.setenv('CFLAGS', '-fuser-cflag')
    monkeypatch.setenv('CPPFLAGS', '-DUSER=1')

    with patched_env({}, cython_line_tracing_requested=tracing):
        cppflags = shlex.split(os.environ['CPPFLAGS'])
        assert os.environ['CFLAGS'] == '-fuser-cflag'

    assert cppflags[0] == '-DUSER=1'
    assert (TRACE_MACRO in cppflags) is tracing
    assert os.environ['CPPFLAGS'] == '-DUSER=1'


@pytest.mark.skipif(
    sys.platform == 'win32',
    reason='MSVC does not read CFLAGS or CPPFLAGS',
)
def test_interpreter_flags_survive_the_build_env():
    """Keep the interpreter's flags and add the macro on top.

    This drives setuptools' real compiler customization, so it fails if the
    backend ever goes back to setting CFLAGS.
    """
    # The RPM builds run the suite without setuptools available.
    ccompiler = pytest.importorskip('setuptools._distutils.ccompiler')
    distutils_sysconfig = pytest.importorskip(
        'setuptools._distutils.sysconfig',
    )
    interpreter_flags = shlex.split(sysconfig.get_config_var('CFLAGS') or '')

    with patched_env({}, cython_line_tracing_requested=True):
        compiler = ccompiler.new_compiler()
        distutils_sysconfig.customize_compiler(compiler)
        command = compiler.compiler_so

    for flag in interpreter_flags:
        assert flag in command
    assert TRACE_MACRO in command
