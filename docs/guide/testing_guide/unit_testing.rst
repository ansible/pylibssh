.. _testing_guide:
.. _unit_testing_guide:


Getting the source code
=======================

getting ansible-pylibssh source::

.. code-block:: shell-session
    $ git clone https://github.com/ansible/pylibssh.git
    $ cd pylibssh
    $ pip install tox
    $ tox -e build-dists

Running tests
==============

.. code-block:: shell-session
    $ tox -e test-binary-dists

.. seealso::

   :ref:`../installation_guide/intro_installation`
       Installation from source
