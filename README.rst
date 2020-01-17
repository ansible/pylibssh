.. image:: https://img.shields.io/pypi/v/pylibssh.svg?logo=Python&logoColor=white
   :target: https://pypi.org/project/pylibssh

.. image:: https://img.shields.io/badge/license-LGPL+-blue.svg?maxAge=3600
   :target: https://pypi.org/project/pylibssh

.. image:: https://img.shields.io/pypi/pyversions/pylibssh.svg?logo=Python&logoColor=white
   :target: https://pypi.org/project/pylibssh

pylibssh: Python bindings to client functionality of libssh
===========================================================

Requirements
------------

You need Python 2.7 or 3.5+

pylibssh requires libssh to be installed in particular:

  - libssh version 0.9.0 and later.

    To install libssh refer to its `Downloads page
    <https://www.libssh.org/get-it/>`__.


Building the module
-------------------

Build the extension:

.. code-block:: python

    git clone https://github.com/ansible/pylibssh.git
    cd pylibssh
    python3 setup.py build_ext --inplace

License
-------

This library is distributed under the terms of LGPL 2.1,
see file COPYING in this repository.
