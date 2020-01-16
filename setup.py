import sys
import os
import logging

from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize

sys.path.insert(0, os.path.abspath('lib'))

setup(
    name="pylibssh",
    version="0.0.1",
    ext_modules=cythonize([Extension("pylibssh.session", ["lib/pylibssh/session.pyx"], libraries=["ssh"]),
                           Extension("pylibssh.channel", ["lib/pylibssh/channel.pyx"], libraries=["ssh"]),
                           Extension("pylibssh.sftp", ["lib/pylibssh/sftp.pyx"], libraries=["ssh"]),
                           Extension("pylibssh.errors", ["lib/pylibssh/errors.pyx"], libraries=["ssh"])]),
    package_dir={'': 'lib'},
    packages=find_packages('lib'),
    description="Python bindings for libssh client",
    classifiers=[
        "Programming Language :: Cython",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Topic :: Software Development :: Libraries :: Python Modules :: Security",
        "Operating System :: Linux:: Mac",
    ],
)
