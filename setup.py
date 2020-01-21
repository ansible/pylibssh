import os
import sys

from setuptools import setup
from setuptools.extension import Extension

from Cython.Build import cythonize


sys.path.insert(0, os.path.abspath('lib'))


__name__ == '__main__' and setup(
    ext_modules=cythonize([Extension("pylibssh.session", ["lib/pylibssh/session.pyx"], libraries=["ssh"]),
                           Extension("pylibssh.channel", ["lib/pylibssh/channel.pyx"], libraries=["ssh"]),
                           Extension("pylibssh.sftp", ["lib/pylibssh/sftp.pyx"], libraries=["ssh"]),
                           Extension("pylibssh.errors", ["lib/pylibssh/errors.pyx"], libraries=["ssh"])]),
)
