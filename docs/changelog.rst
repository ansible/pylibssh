*********
Changelog
*********

Versions follow `Semantic Versioning`_ (``<major>.<minor>.<patch>``).
Backward incompatible (breaking) changes will only be introduced in major
versions with advance notice in the **Deprecations** section of releases.

.. _Semantic Versioning: https://semver.org/

.. towncrier-draft-entries:: |release| [UNRELEASED DRAFT]

.. towncrier release notes start

v1.0.0 (2022-09-14)
===================

Features
^^^^^^^^

- Added ``password_prompt`` argument to ``connect()`` to override the default
  prompt of "password:" when using keyboard-interactive authentication -- by :user:`Qalthos`
  (:issue:`331`)
- Added support for ``:fd:`` socket option -- by :user:`sabedevops`
  (:issue:`343`)


Miscellaneous
^^^^^^^^^^^^^

- Reworked build scripts to fix manylinux container generation -- by :user:`Qalthos`
  (:issue:`321`)
- Reenable CI building on s390x -- by :user:`Qalthos`
  (:issue:`322`)


v0.4.0 (2022-04-26)
===================

Bugfixes
^^^^^^^^

- Improved ``channel.exec_command`` to always use a newly created ``ssh_channel`` to avoid
  segfaults on repeated calls -- by :user:`Qalthos`
  (:issue:`280`)
- Fixed password prompt match in ``pylibsshext.session.Session.authenticate_interactive()``
  to strip whitespace, check that the prompt only ends with ``password:``, and added
  a little extra logging -- by :user:`dalrrard`
  (:issue:`311`)


Backward incompatible changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Dropped support for Python 2.7 and 3.5, and marked support for 3.10 -- by :user:`Qalthos`
  (:issue:`314`)


v0.3.0 (2021-11-03)
===================

Bugfixes
^^^^^^^^

- Changed ``sftp.sftp_get`` to write files as bytes rather than assuming files are valid UTF8 -- by :user:`Qalthos`
  (:issue:`216`)


Features
^^^^^^^^

- Started building platform-specific ``manylinux2010``, ``manylinux2014``
  and ``manylinux_2_24`` wheels for AARCH64, ppc64le and s390x
  architectures as introduced by :pep:`599` and :pep:`600`
  -- :user:`webknjaz`
  (:issue:`187`)
- Added gssapi-with-mic support for authentication -- by :user:`Qalthos`
  (:issue:`195`)


Documentation
^^^^^^^^^^^^^

- Correct a link to the pip upgrade doc in our installation guide
  -- :user:`webknjaz`
  (:issue:`225`)


Miscellaneous
^^^^^^^^^^^^^

- Started building AARCH64 base images with Buildah+Podman in GitHub
  Actions CI/CD -- :user:`webknjaz`
  (:issue:`181`)
- Switched using `pep517 <https://pep517.rtfd.io>`__ lib to
  `build <https://pypa-build.rtfd.io>`__ CLI -- :user:`webknjaz`
  (:issue:`199`)
- Restructured the in-tree :pep:`517` build backend into multiple
  submodules moving the entry-point to ``pep517_backend.hooks``
  that also facilitates extraction of user-defined
  ``config_settings`` passed by the end-user (packager)
  via the ``build`` CLI command -- :user:`webknjaz`
  (:issue:`200`)
- Updated manylinux build script to build libssh with GSSAPI
  enabled -- :user:`Qalthos`
  (:issue:`203`)
- Added an initial RPM spec continuously tested in the CI -- :user:`webknjaz`
  (:issue:`205`)
- Added additional details when SFTP write errors are raised -- by :user:`Qalthos`
  (:issue:`216`)
- Made ``auditwheel`` only keep one platform tag in the produced wheel
  names -- :user:`webknjaz`
  (:issue:`224`)
- Improved manylinux build scripts to expect dual-aliased manylinux tags
  produced for versions 1/2010/2014 along with their :pep:`600`
  counterparts after ``auditwheel repair`` -- :user:`webknjaz`
  (:issue:`226`)
- Enabled self-test checks in the RPM spec for Fedora
  -- :user:`webknjaz`
  (:issue:`228`)
- Enabled self-test checks in the RPM spec for CentOS
  -- :user:`webknjaz`
  (:issue:`235`)
- Enabled self-test checks in the RPM spec for RHEL
  -- :user:`webknjaz`
  (:issue:`236`)
- Added ``NAME = "VALUE"`` to flake8-eradicate whitelist to work around test false positive introduced in flake8-eradicate 1.1.0 -- by :user:`Qalthos`
  (:issue:`258`)
- Stopped testing ``pylibssh`` binary wheels under Ubuntu 16.04 in GitHub
  Actions CI/CD because it is EOL now -- :user:`webknjaz`
  (:issue:`260`)
- Fixed failing fast on problems with ``rpmbuild`` in GitHub Actions CI/CD
  under Fedora -- :user:`webknjaz`
  (:issue:`261`)
- Declare ``python3-pip`` a build dependency under Fedora fixing the RPM
  creation job in GitHub Actions CI/CD under Fedora -- :user:`webknjaz`
  (:issue:`262`)
- Replaced git protocols in pre-commit config with https now that GitHub has turned
  off git protocol access -- :user:`Qalthos`
  (:issue:`266`)


v0.2.0 (2021-03-01)
===================

Bugfixes
^^^^^^^^

- Fixed ``undefined symbol: ssh_disconnect`` and related issues when building on certain distros -- by :user:`Qalthos`
  (:issue:`63`,
  :issue:`153`,
  :issue:`158`)
- Fixed ``"Negative size passed to PyBytes_FromStringAndSize"`` when ``ssh_channel_read_nonblocking`` fails -- by :user:`Qalthos`
  (:issue:`168`)


Features
^^^^^^^^

- Added SCP support -- by :user:`Qalthos`
  (:issue:`151`,
  :issue:`157`)


Documentation
^^^^^^^^^^^^^

- Added the initial user guide to docs
  -- by :user:`ganeshrn` and :user:`webknjaz`
  (:issue:`141`)
- Added the initial testing guide to docs
  -- by :user:`ganeshrn` and :user:`webknjaz`
  (:issue:`142`)
- Added the initial installation guide to docs
  -- by :user:`ganeshrn` and :user:`webknjaz`
  (:issue:`145`)


Miscellaneous
^^^^^^^^^^^^^

- Migrated the "draft changelog" plugin to the external
  `sphinxcontrib-towncrier implementation
  <https://github.com/sphinx-contrib/sphinxcontrib-towncrier>`__
  -- by :user:`webknjaz`
  (:issue:`123`)
- Declared official support of CPython 3.9 -- by :user:`webknjaz`
  (:issue:`152`)


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
  :ref:`__dealloc__() <finalization_method>` -- by :user:`ganeshrn`
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
