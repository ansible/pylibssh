******************
Installation Guide
******************

Welcome to the |project| Installation Guide!


Installing |project|
====================

This page describes how to install |project| on different platforms.

.. contents::
  :local:

Prerequisites
==============
You need Python 2.7 or 3.5+

pylibssh requires libssh to be installed in particular:

- libssh version 0.9.0 and later.

  To install libssh refer to its `Downloads page
  <https://www.libssh.org/get-it/>`__.

Installing |project| with ``pip``
=================================

|project| can be installed with ``pip``, the Python package manager.  If ``pip`` isn't already available on your system of Python, run the following commands to install it::

    $ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    $ python get-pip.py --user

Then install |project|:

.. parsed-literal::

    $ pip install --user |project|

.. note::

    Running ``pip`` with ``sudo`` will make global changes to the system. Since ``pip`` does not coordinate with system package managers, it could make changes to your system that leaves it in an inconsistent or non-functioning state. This is particularly true for macOS. Installing with ``--user`` is recommended unless you understand fully the implications of modifying global files on the system.

.. note::

    Older versions of ``pip`` default to http://pypi.python.org/simple, which no longer works.
    Please make sure you have the latest version of ``pip`` before installing |project|.
    If you have an older version of ``pip`` installed, you can upgrade by following `pip's upgrade instructions <https://pip.pypa.io/en/stable/installing/#upgrading-pip>`_ .


Running |project| from source (devel)
============================================

|project| can be installed from source::

    $ git clone https://github.com/ansible/pylibssh.git
    $ cd pylibssh
    $ pip install tox
    $ tox -e build-dists

``manylinux``-compatible wheels::

    $ git clone https://github.com/ansible/pylibssh.git
    $ cd pylibssh
    $ pip install tox
    $ tox -e build-dists-manylinux  # with Docker

    # or with Podman
    $ DOCKER_EXECUTABLE=podman tox -e build-dists-manylinux

    # to enable shell script debug mode use
    $ tox -e build-dists-manylinux -- -e DEBUG=1

|project| also uses the following Python modules that need to be installed:

.. code-block:: bash

    $ pip install --user -r ./requirements.txt

.. seealso::

   :ref:`Getting Started with |project|`
       Examples of getting started

