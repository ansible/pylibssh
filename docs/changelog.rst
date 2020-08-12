*********
Changelog
*********

Versions follow `Semantic Versioning`_ (``<major>.<minor>.<patch>``).
Backward incompatible (breaking) changes will only be introduced in major
versions with advance notice in the **Deprecations** section of releases.

.. _Semantic Versioning: https://semver.org/

.. towncrier-draft-entries:: |release| [UNRELEASED DRAFT]

.. towncrier release notes start

v0.1.0 (2020-08-12)
===================

Bugfixes
^^^^^^^^

- Enhanced sftp error handling code to match
  with libssh error messages -- by :user:`ganeshrn`
  (:issue:`27`)
- Fixed session timeout issue, the data type
  of timeout is expected by ``ssh_options_set``
  is of type ``long int`` -- by :user:`ganeshrn`
  (:issue:`46`)
- Fixed sftp file get issue. On py2
  The file ``write()`` method returns ``None`` on py2
  if bytes are written to file successfully, whereas
  on py3 it returns total number of bytes written
  to file. Added a fix to check for the number of
  bytes written only in the case when ``write()``
  does not return ``None`` -- by :user:`ganeshrn`
  (:issue:`58`)
- Fixed double close issue, added logic to free
  the channel allocated memory within
  `__dealloc__() <finalization_method>` -- by :user:`ganeshrn`
  (:issue:`113`)


Features
^^^^^^^^

- Added cython extension for libssh client
  API's initial commit -- by :user:`ganeshrn`
  (:issue:`1`)
- Added proxycommand support for session and
  update session exeception to ``LibsshSessionException`` -- by :user:`ganeshrn`
  (:issue:`10`)
- Added support for host key checking with
  authentication -- by :user:`ganeshrn`
  (:issue:`15`)
- Changed pylibssh dir to pylibsshext to avoid ns collision -- by :user:`ganeshrn`
  (:issue:`25`)
- Added sftp get functionality to fetch file
  from remote host -- by :user:`amolkahat`
  (:issue:`26`)
- Added support to receive bulk response
  for remote shell -- by :user:`ganeshrn`
  (:issue:`40`)
- Added the support for keyboard-authentication method -- by :user:`Qalthos`
  (:issue:`105`)


Backward incompatible changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Updated the package name to ``ansible-pylibssh`` to reflect
  that the library only intends to implement a set of APIs that
  are necessary to implement an Ansible connection plugin
  -- by :user:`ganeshrn`
  (:issue:`1`)


Documentation
^^^^^^^^^^^^^

- Documented how to compose `Towncrier
  <https://towncrier.readthedocs.io/en/actual-freaking-docs/>`__
  news fragments -- by :user:`webknjaz`
  (:issue:`124`)
- Documented how to contribute to the docs -- by :user:`webknjaz`
  (:issue:`126`)


Miscellaneous
^^^^^^^^^^^^^

- Updated requirements file to replace
  ``requirements.txt`` with ``requirements-build.in`` -- by :user:`akasurde`
  (:issue:`14`)
- Made tox's main env pick up the in-tree :pep:`517` build
  backend -- by :user:`webknjaz`
  (:issue:`72`)
- Refactored sphinx RST parsing in towncrier extension -- by :user:`ewjoachim`
  (:issue:`119`)
- Hotfixed the directive in the in-tree sphinx extension to
  always trigger the changelog document rebuilds so that it'd
  pick up any changelog fragments from disk
  -- by :user:`webknjaz`
  (:issue:`120`)
- Turned the Townrier fragments README doc title into subtitle
  -- by :user:`webknjaz`

  The effect is that it doesn't show up in the side bar as an
  individual item anymore.
  (:issue:`125`)
- Integrated Markdown support into docs via the `MyST parser
  <https://myst-parser.readthedocs.io/>`__ -- by :user:`webknjaz`
  (:issue:`126`)
- Switched the builder on `Read the Docs
  <https://readthedocs.org/>`__ to `dirhtml
  <https://www.sphinx-doc.org/en/master/usage/builders/index.html#sphinx.builders.dirhtml.DirectoryHTMLBuilder>`__
  so it now generates a dir-based URL layout for the website
  -- by :user:`webknjaz`
  (:issue:`127`)
- Enabled `sphinx.ext.autosectionlabel Sphinx extension
  <https://myst-parser.readthedocs.io/>`__ to automatically generate
  reference targets for document sections that can be linked
  against using ``:ref:`` -- by :user:`webknjaz`
  (:issue:`128`)
