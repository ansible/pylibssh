# This file is part of the pylibssh library
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, see file LICENSE.rst in this
# repository.
"""Compatibility shim for cross-platform hybrid Python 2/3 support."""

from __future__ import absolute_import, division, print_function

from subprocess import CalledProcessError  # noqa: S404


__metadata__ = type


try:
    from subprocess import CompletedProcess  # noqa: S404, WPS433
except ImportError:
    class CompletedProcess:  # noqa: WPS440
        """A process that has finished running.

        This is returned by run().
        """

        def __init__(self, args, returncode, stdout=None, stderr=None):
            """Initialize a CompletedProcess instance.

            :param args: The list or str args passed to run().
            :type args: list or str

            :param returncode: The exit code of the process, negative for signals.
            :type returncode: int

            :param stdout: The standard output (None if not captured).
            :type stdout: str or bytes or NoneType

            :param stderr: The standard error (None if not captured).
            :type stderr: str or bytes or NoneType
            """
            self.args = args
            self.returncode = returncode
            self.stdout = stdout
            self.stderr = stderr

        def __repr__(self):
            """Make a representation of CompletedProcess instance.

            :returns: A representation of CompletedProcess instance.
            :rtype: str
            """
            args = [
                'args={args!r}'.format(args=self.args),
                'returncode={rc!r}'.format(rc=self.returncode),
            ]
            if self.stdout is not None:
                args.append('stdout={out!r}'.format(out=self.stdout))
            if self.stderr is not None:
                args.append('stderr={err!r}'.format(err=self.stderr))
            return '{mod!s}.{cls!s}({args!s})'.format(
                mod=__name__,
                cls=self.__class__.__name__,
                args=', '.join(args),
            )

        def check_returncode(self):
            """Check if the exit code is successful.

            :raises CalledProcessError: if the return code is non-zero.
            """
            if not self.returncode:
                return

            raise CalledProcessError(
                self.returncode,
                self.args,
                self.stdout,
                self.stderr,
            )
