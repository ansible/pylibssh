*************
Testing Guide
*************

Welcome to the |project| Testing Guide!


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

.. code-block:: shell-session

    $ tox -e test-binary-dists
