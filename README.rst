.. image:: https://img.shields.io/pypi/v/ansible-pylibssh.svg?logo=Python&logoColor=white
   :target: https://pypi.org/project/ansible-pylibssh

.. image:: https://img.shields.io/badge/license-LGPL+-blue.svg?maxAge=3600
   :target: https://pypi.org/project/ansible-pylibssh

.. image:: https://img.shields.io/pypi/pyversions/ansible-pylibssh.svg?logo=Python&logoColor=white
   :target: https://pypi.org/project/ansible-pylibssh

.. image:: https://github.com/ansible/pylibssh/actions/workflows/ci-cd.yml/badge.svg?event=push
   :alt: 🧪 CI/CD @ devel
   :target: https://github.com/ansible/pylibssh/actions/workflows/ci-cd.yml

.. image:: https://img.shields.io/codecov/c/gh/ansible/pylibssh/devel?logo=codecov&logoColor=white
   :target: https://codecov.io/gh/ansible/pylibssh
   :alt: devel branch coverage via Codecov

.. image:: https://img.shields.io/badge/style-wemake-000000.svg
   :target: https://github.com/wemake-services/wemake-python-styleguide

.. image:: https://img.shields.io/badge/Code%20of%20Conduct-Ansible-silver.svg
   :target: https://docs.ansible.com/ansible/latest/community/code_of_conduct.html
   :alt: Ansible Code of Conduct

.. DO-NOT-REMOVE-docs-badges-END

pylibssh: Python bindings to client functionality of libssh specific to Ansible use case
========================================================================================

.. DO-NOT-REMOVE-docs-intro-START

Nightlies @ Dumb PyPI @ GitHub Pages
------------------------------------

.. DO-NOT-REMOVE-nightlies-START

We publish nightlies on tags and pushes to devel.
They are hosted on a GitHub Pages based index generated
by `dumb-pypi <https://pypi.org/project/dumb-pypi/>`_.

The web view is @ https://ansible.github.io/pylibssh/.

.. code-block:: shell-session

    $ pip install \
        --extra-index-url=https://ansible.github.io/pylibssh/simple/ \
        --pre \
        ansible-pylibssh

.. DO-NOT-REMOVE-nightlies-END


Requirements
------------

You need Python 3.9+

pylibssh requires libssh to be installed in particular:

- libssh version 0.9.0 and later.

  To install libssh refer to its `Downloads page
  <https://www.libssh.org/get-it/>`__.

.. note::

   If a pre-built wheel is not available for your Python
   version (for example, on newer Python releases),
   ``pip install ansible-pylibssh`` will compile from source
   automatically, but requires ``libssh`` development headers
   and a C compiler to be installed first. See the
   `documentation <https://ansible-pylibssh.rtfd.io/>`__
   for platform-specific commands.


Building the module
-------------------

In the local env, assumes there's a libssh shared library
on the system, build toolchain is present and env vars
are set properly:

.. code-block:: shell-session

    $ git clone https://github.com/ansible/pylibssh.git
    $ cd pylibssh
    $ pip install tox
    $ tox -e build-dists

``manylinux``-compatible wheels:

.. code-block:: shell-session

    $ git clone https://github.com/ansible/pylibssh.git
    $ cd pylibssh
    $ pip install tox
    $ tox -e build-dists-manylinux1-x86_64  # with Docker

    # or with Podman
    $ DOCKER_EXECUTABLE=podman tox -e build-dists-manylinux1-x86_64

    # to enable shell script debug mode use
    $ tox -e build-dists-manylinux1-x86_64 -- -e DEBUG=1

Communication
-------------

Join the Ansible forum:

* `Get Help <https://forum.ansible.com/c/help/6>`_: get help or help others. Please add the appropriate tags if you start new discussions, for example the ``pylibssh`` tag.
* `Posts tagged with 'pylibssh' <https://forum.ansible.com/tag/pylibssh>`_: subscribe to participate in project-related conversations.
* `News & Announcements <https://forum.ansible.com/c/news/5>`_: track project-wide announcements including social events and the `Bullhorn newsletter <https://docs.ansible.com/ansible/devel/community/communication.html#the-bullhorn>`_.
* `Social Spaces <https://forum.ansible.com/c/chat/4>`_: gather and interact with fellow enthusiasts.

For more information about getting in touch with us, see the `Ansible communication guide <https://docs.ansible.com/ansible/devel/community/communication.html>`_.

License
-------

This library is distributed under the terms of LGPL 2 or higher,
see file ``LICENSE.rst`` in this repository.
