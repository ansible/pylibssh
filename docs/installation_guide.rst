********************
Installing |project|
********************

This page describes how to install |project| using
:std:doc:`pip:index`. Consult with :std:doc:`pip docs
<pip:installing>` if you are not sure whether you have it
set up.

.. contents::
  :local:

Pre-compiled binary distributions
=================================

|project| contains :std:doc:`Cython <cython:index>`-based
:std:term:`CPython C-extension modules <python:extension
module>`. Unlike :std:term:`pure-Python modules
<python:module>`, these must be pre-compiled
before consumption.

We publish :std:ref:`platform-specific wheels <platform
wheels>` to PyPI. They are built against different arch,
CPython and OS versions so in 99% of cases, you may
seamlessly install |project| not needing any external
dependencies on your system.

It should be enough for you to just have Python 3.9+ and
a recent :std:doc:`pip <pip:index>` installed.

.. note::

    Pre-built wheels are not yet available for Python 3.13 and
    3.14. When no wheel is available,
    ``pip install`` will automatically
    attempt to compile the package from source. For this to
    succeed, you must first install the system dependencies
    listed in :ref:`install-from-source` below.

.. attention::

    Please make sure you have the latest version of
    :std:doc:`pip <pip:index>` before installing |project|.

    If you have a version of :std:doc:`pip <pip:index>`
    older than 8.1, it'll be unable to pick up OS-specific
    Python package distributions from PyPI and will try to
    fall back to building it from source which would require
    more extra dependencies to succeed.
    You can upgrade by following :std:doc:`pip's upgrade
    instructions <pip:user_guide>`.

To install |project|, just run:

.. parsed-literal::

    $ pip install --user |project|

.. tip::

    Avoid running :std:doc:`pip <pip:index>` with
    :command:`sudo` as this will make global changes to the
    system. Since :std:doc:`pip <pip:index>` does not
    coordinate with system package managers, it could make
    changes to your system that leaves it in an inconsistent
    or non-functioning state. This is particularly true for
    macOS. Installing with :std:ref:`\-\\\\-user
    <pip:install_--user>` is recommended unless you
    understand fully the implications of modifying global
    files on the system.

.. _install-from-source:

Installing |project| from source distribution (PyPI)
====================================================

Installing |project| from source is a bit more complicated.
First, pylibssh requires libssh to be compiled against, in
particular, version 0.9.0 or newer. Make sure that you have
the development headers too.

You will also need a C compiler such as GCC. Below are the
install commands for common platforms:

**macOS**:

.. code-block:: shell-session

    $ xcode-select --install  # one-time setup for the C compiler
    $ brew install libssh

**Debian / Ubuntu**:

.. code-block:: shell-session

    $ sudo apt-get install libssh-dev build-essential python3-dev

**RHEL / Fedora / CentOS Stream**:

.. code-block:: shell-session

    $ sudo dnf install libssh-devel gcc python3-devel

For other platforms, refer to the `libssh Downloads page
<https://www.libssh.org/get-it/>`__.

.. note::

    Python 3.13 requires ``Cython >= 3.0.11`` and Python 3.14
    requires ``Cython >= 3.1.0`` to compile the C-extensions.
    When building from source via :std:doc:`pip <pip:index>`,
    the correct version is pulled automatically by the
    :pep:`517` build backend.

Once you have the build prerequisites, the following command
should download the tarball, build it and then install into
your current env:

.. parsed-literal::

    $ pip install \\
        --user \\
        --no-binary |project| \\
        |project|

.. tip::

  When your copy of ``libssh-dev`` is installed into a
  non-default directory, make sure to prepend the compiler
  environment variables (e.g
  ``CFLAGS=-I/usr/local/include``) right before the
  ``pip install`` command. For the macOS users who install
  it using Homebrew, it should be enough to set
  ``CFLAGS="-I $(brew --prefix)/include -I ext
  -L $(brew --prefix)/lib -lssh"``

Building |project| dists from the ``devel`` branch in Git
=========================================================

Since our build processes are tox_-centric, let's
install it first:

.. code-block:: shell-session

    $ python -m pip install 'tox >= 3.19.0' --user

.. _tox: https://tox.readthedocs.io

Now, let's grab the source of |project|:

.. code-block:: shell-session

    $ git clone https://github.com/ansible/pylibssh.git ~/src/github/ansible/pylibssh
    $ # or, if you use SSH:
    $ git clone git@github.com:ansible/pylibssh.git ~/src/github/ansible/pylibssh
    $ cd ~/src/github/ansible/pylibssh
    [dir:pylibssh] $

Finally, you can build the dists for the current env using:

.. code-block:: shell-session

    [dir:pylibssh] $ tox -e build-dists

If you want to generate the whole matrix of ``manylinux``-\
compatible wheels, use:

.. code-block:: shell-session

    [dir:pylibssh] $ tox r -e cibuildwheel

.. seealso::

   :ref:`Getting Started with |project|`
       Examples of getting started

   :ref:`Continuous delivery`
       Using nightly builds to test your project against
