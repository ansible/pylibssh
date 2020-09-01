********************
Installing |project|
********************

This page describes how to install |project| using
:std:doc:`pip:index`. Consult with :std:doc:`pip docs
<pip:installing>` if you are not sure whether you have it
set up.

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

Now, let's install |project|:

.. parsed-literal::

    $ pip install --user |project|

.. note::

    Running ``pip`` with ``sudo`` will make global changes to the system. Since ``pip`` does not coordinate with system package managers, it could make changes to your system that leaves it in an inconsistent or non-functioning state. This is particularly true for macOS. Installing with ``--user`` is recommended unless you understand fully the implications of modifying global files on the system.

.. attention::

    Older versions of :std:doc:`pip <pip:index>` default to
    http://pypi.python.org/simple, which no longer works.

    Please make sure you have the latest version of
    :std:doc:`pip <pip:index>` before installing |project|.

    If you have an older version of :std:doc:`pip
    <pip:index>` installed, you can upgrade by following
    :std:ref:`pip's upgrade instructions <pip:upgrading
    pip>`.


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

