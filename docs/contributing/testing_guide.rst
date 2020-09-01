*************
Testing Guide
*************

Welcome to the |project| Testing Guide!

This page contains information on how to test |project|
locally as well as some notes of how the automated testing and linting is implemented.


Mandatory tooling
=================

All build and test processes use tox_-centric workflow. So
first of all, let's install it:

.. code-block:: shell-session

    $ python -m pip install 'tox >= 3.19.0' --user

.. note::

    This will install tox_ in :doc:`user-global
    site-packages <pip:user_guide>`. To make it
    discoverable, you may need to add :command:`export
    PATH="$HOME/.local/bin:$PATH"` to your :file:`~/.bashrc`
    or :file:`~/.zshrc`.

    The examples below will use the :py:mod:`python:runpy`
    syntax (CLI option :option:`python:-m`) to avoid the
    need to put scripts into the search :envvar:`PATH`.

.. tip::

    While the example above uses pip, alternatively you may
    install tox_ via your OS package manager (e.g.
    :program:`apt`, :program:`dnf`, :program:`emerge`,
    :program:`packman`, :program:`yum`, :program:`zypper`
    etc.).

    It is important to have at least `version 3.8.0 <tox
    v3.8.0_>`_ because it'll allow tox_ to auto-provison a
    newer version of itself just for |project|.

Tox_ will take care of the Python dependencies but it's up
to you to make the external ecosystem dependencies available.

|project|'s core dependency is  libssh_. |project| links
against it and so the development headers must be present
on your system for build to succeed.

The next external build-time dependency is `Cython
<cython:index>` and `using it
<cython:src/quickstart/install>` requires presense of GCC_.
Consult with your OS's docs to figure out how to get it onto
your machine.

.. _GCC: https://gcc.gnu.org
.. _libssh: https://libssh.org
.. _tox: https://tox.readthedocs.io
.. _tox v3.8.0:
   https://tox.readthedocs.io/en/latest/changelog.html#v3-8-0-2019-03-27

.. seealso::

   :ref:`Installing |project|`
       Installation from source

Getting the source code
=======================

Once you sort out the toolchain, get |project|'s source:

.. code-block:: shell-session

    $ git clone https://github.com/ansible/pylibssh.git ~/src/github/ansible/pylibssh
    $ # or, if you use SSH:
    $ git clone git@github.com:ansible/pylibssh.git ~/src/github/ansible/pylibssh
    $ cd ~/src/github/ansible/pylibssh
    [dir:pylibssh] $

.. attention::

    All following commands assume the working dir to be the
    Git checkout folder (\
    :file:`~/src/github/ansible/pylibssh` in the example)

Running tests
==============

To run tests under your current Python interpreter, run:

.. code-block:: shell-session

    [dir:pylibssh] $ python -m tox

If you want to target some other Python version, do:

.. code-block:: shell-session

    [dir:pylibssh] $ python -m tox -e py38

Continuous integration
^^^^^^^^^^^^^^^^^^^^^^

In the CI, the testing is done slightly differently. First,
the Python package distributions are built with:

.. code-block:: shell-session

    [dir:pylibssh] $ python -m tox -e build-dists

Then, they are tested in a matrix of separate jobs across
different OS and CPython version combinations:

.. code-block:: shell-session

    [dir:pylibssh] $ python -m tox -e test-binary-dists

Quality and sanity
^^^^^^^^^^^^^^^^^^

Additionally, there's a separate workflow that runs linting\
-related checks that can be reproduced locally as follows:

.. code-block:: shell-session

    [dir:pylibssh] $ python -m tox -e build-docs  # Sphinx docs build
    [dir:pylibssh] $ python -m tox -e lint  # pre-commit.com tool

Continuous delivery
===================

Besides testing and linting, |project| also has `GitHub
Actions workflows CI/CD`_ set up to publish those same
Python package distributions **after** they've been tested.

Commits from ``devel`` get published to
https://test.pypi.org/project/ansible-pylibssh/ and tagged
commits are published to
https://pypi.org/project/ansible-pylibssh/.

Besides, if you want to test your project against unreleased
versions of |project|, you may want to go for nightlies.

.. include:: ../../README.rst
   :start-after: DO-NOT-REMOVE-nightlies-START
   :end-before: DO-NOT-REMOVE-nightlies-END

.. _GitHub Actions workflows CI/CD: https://github.com/features/actions
