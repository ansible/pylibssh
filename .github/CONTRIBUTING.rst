================================
Contributing to ansible-pylibssh
================================

.. attention::

   ansible-pylibssh project exists solely to allow Ansible connection
   plugins to use libssh_ SSH implementation by importing it in
   Python-land. At the moment we don't accept any contributions, nor
   feature requests that are unrelated to this goal.

   But if you want to contribute a bug fix or send a pull-request
   improving our CI, testing and packaging, we will gladly review it.


In order to contribute, you'll need to:

  1. Fork the repository.

  2. Create a branch, push your changes there. Don't forget to
     :ref:`include news files for the changelog <Adding change
     notes with your PRs>`.

  3. Send it to us as a PR.

  4. Iterate on your PR, incorporating the requested improvements
     and participating in the discussions.

Prerequisites:

  1. Have libssh_.

  2. Use tox_ to build the C-extension, docs and run the tests.

  3. Before sending a PR, make sure that the linters pass:

     .. code-block:: shell-session

        $ tox -e lint


.. _libssh: https://www.libssh.org
.. _tox: https://tox.readthedocs.io
