.. image:: https://img.shields.io/pypi/v/ansible-pylibssh.svg?logo=Python&logoColor=white
   :target: https://pypi.org/project/ansible-pylibssh

.. image:: https://img.shields.io/badge/license-LGPL+-blue.svg?maxAge=3600
   :target: https://pypi.org/project/ansible-pylibssh

.. image:: https://img.shields.io/pypi/pyversions/ansible-pylibssh.svg?logo=Python&logoColor=white
   :target: https://pypi.org/project/ansible-pylibssh

.. image:: https://img.shields.io/github/workflow/status/ansible/pylibssh/%F0%9F%8F%97%20%F0%9F%93%A6%20&%20test%20&%20publish/devel?label=GitHub%20Actions%20%5Btests%5D&logo=github
   :alt: GitHub Workflow Status (🏗 📦 & test & publish/devel)
   :target: https://github.com/ansible/pylibssh/actions?query=workflow%3A%22%F0%9F%8F%97+%F0%9F%93%A6+%26+test+%26+publish%22+branch%3Adevel

.. image:: https://img.shields.io/github/workflow/status/ansible/pylibssh/%F0%9F%9A%A8/devel?label=GitHub%20Actions%20%5Bquality%5D&logo=github
   :target: https://github.com/ansible/pylibssh/actions?query=workflow%3A%F0%9F%9A%A8+branch%3Adevel
   :alt: GitHub Workflow Status (🚨/devel)

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

You need Python 3.6+

pylibssh requires libssh to be installed in particular:

- libssh version 0.9.0 and later.

  To install libssh refer to its `Downloads page
  <https://www.libssh.org/get-it/>`__.


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

License
-------

This library is distributed under the terms of LGPL 2 or higher,
see file ``LICENSE.rst`` in this repository.
