*********
Changelog
*********

..
    You should *NOT* be adding new change log entries to this file, this
    file is managed by towncrier. You *may* edit previous change logs to
    fix problems like typo corrections or such.
    To add a new change log entry, please see
    https://pip.pypa.io/en/latest/development/contributing/#news-entries
    we named the news folder "docs/changelog-fragments/".

    WARNING: Don't drop the next directive!

.. towncrier release notes start

v1.3.0a1
========

*(2025-10-11)*


Bug fixes
---------

- The bundled libssh 0.11.2 no longer fails, when the SFTP server announces
  protocol version 3, but does not provide error message and language tag
  in the ``SSH_FXP_STATUS`` message -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`222`.

- Fixed reading files over SFTP that go over the pre-defined chunk size.

  Prior to this change, the files could end up being corrupted, ending up with the last read chunk written to the file instead of the entire payload.

  -- by :user:`Jakuje`

  *Related issues and pull requests on GitHub:*
  :issue:`638`.

- Repetitive calls to ``exec_channel()`` no longer crash and return reliable output -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`658`.

- Uploading large files over SCP no longer fails -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`661`.

- Improved performance of SFTP transfers by using larger transfer chunks -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`664`.

- Fixed crash when more operations were called after ``session.close()`` -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`709`.


Features
--------

- The underlying ``SSH_OPTIONS_KEY_EXCHANGE`` option of ``libssh`` is
  now available as ``key_exchange_algorithms`` -- by :user:`NilashishC`.

  *Related issues and pull requests on GitHub:*
  :issue:`675`.

- Added a ``pylibsshext.session.connect()`` parameter
  ``open_session_retries`` -- by :user:`justin-stephenson`.

  The ``open_session_retries`` session ``connect()``
  parameter allows a configurable number of retries if
  libssh ``ssh_channel_open_session()`` returns ``SSH_AGAIN``.
  The default option value is 0, no retries will be
  attempted.

  *Related issues and pull requests on GitHub:*
  :issue:`756`.

- Added a ``pylibsshext.session.connect()`` parameter
  ``timeout_usec`` to set ``SSH_OPTIONS_TIMEOUT_USEC``.

  This allows setting the ``SSH_OPTIONS_TIMEOUT_USEC``
  ssh option, though ``SSH_OPTIONS_TIMEOUT`` is a more
  practical option.

  -- by :user:`justin-stephenson`

  *Related issues and pull requests on GitHub:*
  :issue:`756`.


Deprecations (removal in next major release)
--------------------------------------------

- The project stopped being tested under Ubuntu 20.04 VM since
  GitHub has sunset their CI images -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`708`.


Removals and backward incompatible breaking changes
---------------------------------------------------

- Dropped support for Python 3.6, 3.7 and 3.8
  -- by :user:`Qalthos` and :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`532`, :issue:`718`.

- PyPI no longer ships year-versioned manylinux wheels. One may
  have to update their version of pip to pick up the new ones.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`562`.


Improved documentation
----------------------

- Added a :ref:`Communication <communication>` section to the main
  documentation page -- by :user:`Andersson007`.

  *Related issues and pull requests on GitHub:*
  :issue:`640`.

- Fixed the argument order in the ``scp.put()`` usage example
  -- by :user:`kucharskim`.

  *Related issues and pull requests on GitHub:*
  :issue:`646`.


Packaging updates and notes for downstreams
-------------------------------------------

- PyPI now only ships :pep:`600`-compatible manylinux wheels
  -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`562`.

- The ``pytest-forked`` dependency of build, development and test environments was removed -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`658`, :issue:`760`.

- The wheels are now built in cached container images with a
  correctly set platform identifier.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`692`.

- The ``manylinux`` build scripts now limit ``cmake`` below
  version 4 -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`713`.

- Stopped skipping SCP tests in the RPM spec -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`714`.

- Started bundling a copy of libssh 0.11.1 in platform-specific
  wheels published on PyPI -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`735`.

- Updated the bundled copy of OpenSSL to the latest version 3.5.0
  in ``manylinux`` wheels -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`738`.

- Updated the bundled version of libssh to 0.11.2 in platform-specific
  wheels published on PyPI -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`753`.

- The RPM spec file no longer makes use of unpackaged dists
  from PyPI on RHEL. The configuration is almost identical to
  the one for Fedora. Only the ``setuptools-scm`` spec is
  temporarily patched to allow older versions under RHEL.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`759`.

- A workaround has been applied to the in-tree build backend that prevents
  Cython from hanging when ``libssh`` header files are missing
  -- by :user:`webknjaz`.

  The patch makes ``cythonize()`` single-threaded because :mod:`multiprocessing`
  gets stuck. The upstream will eventually fix this by migrating to
  :mod:`concurrent.futures`.

  *Related issues and pull requests on GitHub:*
  :issue:`762`, :issue:`769`, :issue:`770`.

- Updated the bundled version of libssh to 0.11.3 in platform-specific
  wheels published on PyPI -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`766`.


Contributor-facing changes
--------------------------

- The manylinux build scripts have been adjusted to resolve the
  dependency conflict between certain ``packaging`` and ``setuptools``
  versions -- by :user:`webknjaz`.

  Previously, this was making some of the CI jobs crash with a traceback
  when building said wheels.

  *Related commits on GitHub:*
  :commit:`1dfbf70fdfd99ae75068fdb3630790c96101a96a`.

- The Git archives are now immutable per the packaging recommendations.
  This allows downstreams safely use GitHub archive URLs when
  re-packaging -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`ea34887831a0c6547b32cd8c6a035bb77b91e771`.

- Manylinux wheels are no longer built using custom shell scripts.
  Instead, this is delegated to the ``cibuildwheel`` tool.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`562`.

- Updated the version of ``libssh`` to the latest release v0.11.1
  in the cached ``manylinux`` build environment container images
  -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`636`.

- All the uses of ``actions/upload-artifact@v3`` and
  ``actions/download-artifact@v3`` have been updated to use
  ``v4``. This also includes bumping
  ``re-actors/checkout-python-sdist`` to ``release/v2`` as it
  uses ``actions/download-artifact`` internally.

  -- by :user:`NilashishC` and :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`676`.

- The ``dumb-pypi``-produced static package index now renders correct
  URLs to the distribution packages -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`678`, :issue:`679`, :issue:`749`.

- The CI is now configured to use
  :external+tox:std:ref:`tox-run---installpkg` when testing
  pre-built dists. This replaces the previously existing
  tox-level hacks in ``test-binary-dists`` and
  ``test-source-dists`` environments that have now been
  removed.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`688`.

- The wheel building workflows have been updated to set the
  OCI image platform identifiers to legal values like
  ``linux/arm64``.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`692`.

- The CI is now configured to always set job timeout values.
  This will ensure that the jobs that get stuck don't consume
  all 6 hours just hanging, improving responsiveness and the
  overall CI/CD resource usage.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`706`.

- The linting is now configured to check schemas of the
  Read The Docs configuration file and the GitHub Actions
  CI/CD workflow files in addition to enforcing timeouts.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`707`.

- The ``multiarch/qemu-user-static`` image got replaced with
  ``tonistiigi/binfmt`` because the latter is no longer
  maintained and the former includes the fixed version of QEMU.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`713`.

- Added Fedora 41 and 42 to CI configuration -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`715`.

- Removed needless step from CI adjusting centos8 repositories -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`716`.

- The CI/CD infrastructure no longer pre-builds custom manylinux images
  for building wheel targeting ``manylinux1``, ``manylinux2010`` and
  ``manylinux2014`` tags.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`730`.

- The host OS is now ARM-based when building ``manylinux_*_*_aarch64``
  images for CI/CD -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`731`.

- False negative warnings reported by ``coveragepy`` when are now
  disabled. They are evident when ``pytest-cov`` runs with the
  ``pytest-xdist`` integration. ``pytest`` 8.4 gives them more
  visibility and out ``filterwarnings = error`` setting was turning
  them into errors before this change.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`732`.

- GitHub Actions CI/CD no longer runs jobs that install source
  distributions into the tox environments for testing
  -- by :user:`webknjaz`.

  This is a temporary workaround for an upstream bug in tox and
  said jobs are non-essential.

  *Related issues and pull requests on GitHub:*
  :issue:`733`.

- Updated the pre-built ``libffi`` version to 3.4.8 in the
  cached ``manylinux`` build environment container images
  -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`734`.

- Reverted workaround keeping the old CMake version installed
  as the new ``libssh`` works with newer versions -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`737`.

- The CI infrastructure now produces ``manylinux_2_31_armv7l`` base images
  with ``libssh`` and ``openssl`` pre-built -- by :user:`Jakuje` and
  :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`740`.

- Started caching ``manylinux`` build images to be used for producing ``2_34`` tagged wheels
  in ``build-manylinux-container-images`` workflow -- by :user:`KB-perByte`.

  *Related issues and pull requests on GitHub:*
  :issue:`741`.

- The :file:`reusable-cibuildwheel.yml` workflow has been refactored to
  be more generic and :file:`ci-cd.yml` now holds all the configuration
  toggles -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`750`.

- Updated the version of ``libssh`` to the latest release v0.11.2
  in the cached ``manylinux`` build environment container images
  -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`752`.

- When building wheels, the source distribution is now passed directly
  to the ``cibuildwheel`` invocation -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`754`.

- Fixed link to python3-pytest for CentOS 9 Stream as it was recently moved from
  CRB to AppStream -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`758`.

- The CI/CD jobs for smoke-testing RPMs have been simplified
  and now, they execute the same steps for all distro types.
  They make use of ``pyproject-rpm-macros`` even under RHEL.
  Installing external RPMs is the only conditional step that
  is skipped on Fedora.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`759`.

- The ``requires`` setting has been removed from :file:`tox.ini`, which
  works around the upstream tool bug. This enabled us to re-introduce
  CI jobs testing against sdist under Python 3.12 and newer
  -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`764`.

- Updated the version of ``libssh`` to the latest release v0.11.3
  in the cached ``manylinux`` build environment container images
  -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`765`.

- Changed tests to use more lightweight ECDSA keys to avoid
  timeouts -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`768`.


----


v1.2.2
======

*(2024-06-27)*


Bug fixes
---------

- Downloading files larger than 64kB over SCP no longer fails -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`621`.


----


v1.2.1
======

*(2024-06-27)*


Bug fixes
---------

- Downloading non-existent remote files via SCP no longer crashes the program -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`208`, :issue:`325`, :issue:`620`.


Packaging updates and notes for downstreams
-------------------------------------------

- The RPM specification now opts out of demanding that the
  compiled C-extensions have a Build ID present under EL
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`9053c1008bb169c8e362a92782d46c7c0d3b1c06`, :commit:`aaa12159b5cdda763a83dcf4ee920510cad83463`.

- The RPM specification has been updated to pre-build the
  vendored copy of ``setuptools-scm`` with the isolation
  disabled, addressing the build problem in EL 9
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`dd85ddefafde8f22ab0239add18a1db9ef789b50`.

- The RPM definition now runs import self-checks when it is
  built for Fedora Linux -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`615`.


Contributor-facing changes
--------------------------

- RPM builds are now also tested against UBI 9.4 in CI
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`e9ad0a7d456c99cc848b30b48569235366273672`.


----


v1.2.0.post4
============

*(2024-06-09)*


Packaging updates and notes for downstreams
-------------------------------------------

- Substituting the ``gh`` role in source distribution long
  description has been simplify to stop attempting to make
  URLs to arbitrary GitHub addresses -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`f4ad1b76`.

- The in-tree :pep:`517` build backend's regular expression
  has been hotfixed to replace the "project" substitution
  correctly -- by :user:`webknjaz`.

  Previously, it was generating a lot of noise instead of a
  nice description. But not anymore.

  *Related issues and pull requests on GitHub:*
  :issue:`92752210`.


----


v1.2.0.post2
============

*(2024-06-08)*


Packaging updates and notes for downstreams
-------------------------------------------

- The automation now replaces the "project" RST substitution
  in the long description and GitHub Discussions/Releases
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`13374a71`.

- The CI/CD automation has been fixed to include changelog
  updates into source distribution tarballs
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`627f718d`.


----


v1.2.0
======

*(2024-06-07)*


Bug fixes
---------

- |project| no longer crashes when received EOF or when channel is not explicitly
  closed -- by :user:`pbrezina`.

  Previously, |project| crashed if ``channel.recv`` was called and ``libssh``
  returned ``SSH_EOF`` error. It also crashed on some special occasions where
  channel was not explicitly closed and the session object was garbage-collected
  first.

  *Related issues and pull requests on GitHub:*
  :issue:`576`.


Features
--------

- Started exposing the ``SSH_OPTIONS_PUBLICKEY_ACCEPTED_TYPES``
  and ``SSH_OPTIONS_HOSTKEYS`` options publicly
  -- by :user:`Qalthos`.

  *Related issues and pull requests on GitHub:*
  :issue:`527`.

- The ``request_exec()`` method was added to the ``Channel`` class. It exposes an
  interface for calling the respective low-level C-API of the underlying
  ``libssh`` library -- by :user:`pbrezina`.

  Additionally, the following calls to ``libssh`` are now available in the same
  class: ``request_exec()``, ``send_eof()``, ``request_send_signal()`` and
  ``is_eof`` which is exposed as a :py:class:`property`.

  *Related issues and pull requests on GitHub:*
  :issue:`576`.


Improved documentation
----------------------

- Fixed spelling of "Connect" in the ``Session.connect()``
  docstring -- by :user:`donnerhacke`.

  *Related issues and pull requests on GitHub:*
  :issue:`474`.

- Added a tip to the :ref:`installation guide <Installing |project|>`
  on how to set compiler flags when installing from source
  -- :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`499`.

- Fixed the example of invoking remote commands by using
  ``Channel.exec_command()`` in snippets -- by :user:`pbrezina`.

  Its previously showcased version wasn't functional.

  *Related issues and pull requests on GitHub:*
  :issue:`576`.


Packaging updates and notes for downstreams
-------------------------------------------

- A flaw in the logic for copying the project directory into a
  temporary folder that led to infinite recursion when :envvar:`TMPDIR`
  was set to a project subdirectory path. This was happening in Fedora
  and its downstream due to the use of `pyproject-rpm-macros
  <https://src.fedoraproject.org/rpms/pyproject-rpm-macros>`__. It was
  only reproducible with ``pip wheel`` and was not affecting the
  ``pyproject-build`` users.

  -- by :user:`hroncok` and :user:`webknjaz`

  *Related commits on GitHub:*
  :commit:`89c9b3a`.

- From now on, the published distribution package artifacts
  for the new releases are signed via `Sigstore
  <https://sigstore.dev>`__ -- by :user:`webknjaz`.

  This is happening as a part of the GitHub Actions CI/CD
  workflow automation and the signatures are uploaded to
  the corresponding GitHub Release pages.

  *Related commits on GitHub:*
  :commit:`986988a`.

- The platform-specific macOS wheels are now built using the
  Python interpreter from https://python.org. They are tagged
  with ``macosx_10_9`` -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`333`.

- The ``toml`` build time dependency has been replaced with
  ``tomli`` -- by :user:`webknjaz`.

  The ``tomli`` distribution is only pulled in under Python
  versions below 3.11. On 3.11 and higher, the standard
  library module :py:mod:`tomllib` is now used instead.

  *Related issues and pull requests on GitHub:*
  :issue:`501`.

- Started using the built-in ``setuptools-scm`` Git archive
  support under Python 3.7 and higher -- :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`502`.

- Added support for Python 3.12 -- by :user:`Qalthos`.

  It is now both tested in the CI and is advertised through
  the Trove classifiers.

  *Related issues and pull requests on GitHub:*
  :issue:`532`.

- The ``Cython`` build time dependency now has the minimum
  version of 3.0 under Python 3.12 and higher
  -- by :user:`webknjaz`.

  The previous versions of ``Cython`` are still able to build
  the project under older Python versions.

  *Related issues and pull requests on GitHub:*
  :issue:`540`.

- :pep:`660` is now enabled -- :user:`webknjaz`.

  Previously, due to restrictive :pep:`517` hook reimports,
  our in-tree build backend was losing :pep:`non-PEP 517 <517>`
  hooks implemented in newer versions of ``setuptools`` but not
  the earlier ones. This is now addressed by reexporting
  everything that ``setuptools`` exposes with a wildcard.

  *Related issues and pull requests on GitHub:*
  :issue:`541`.

- The ``setuptools-scm`` build dependency CI pin was updated to 8.1.0 —
  this version fixes a date parsing incompatibility introduced by Git 2.45.0
  (:gh:`pypa/setuptools_scm#1038 <pypa/setuptools_scm/issues/1038>`,
  :gh:`pypa/setuptools_scm#1039 <pypa/setuptools_scm/pull/1039>`)
  -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`601`.


Contributor-facing changes
--------------------------

- The :doc:`changelog` page for the tagged release builds on
  Read The Docs does not attempt showing the draft section
  anymore -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`852d259`.

- Adjusted the publishing workflow automation to pre-configure
  Git before attempting to create a tag when building a
  source distribution -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`f07296f`.

- The CI configuration for building the macOS platform-specific
  wheels switched to using ``cibuildwheel`` -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`333`.

- The OS-level tox package was upgraded to v3.28.0 in the UBI9
  CI runtime -- by :user:`Qalthos`.

  *Related issues and pull requests on GitHub:*
  :issue:`461`, :issue:`473`.

- Fixed spelling of "Connect" in the ``Session.connect()``
  docstring -- by :user:`donnerhacke`.

  *Related issues and pull requests on GitHub:*
  :issue:`474`.

- The Packit CI access to the internet has been restored
  -- by :user:`Qalthos`.

  *Related issues and pull requests on GitHub:*
  :issue:`507`.

- Started building ``manylinux_2_28`` base images for testing and
  packaging in the CI/CD infrastructure -- by :user:`Qalthos`.

  *Related issues and pull requests on GitHub:*
  :issue:`533`.

- Switched back to using Cython's native plugin for measuring
  code coverage -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`538`.

- Added separate changelog fragment types for contributor-
  and downstream-facing patches -- by :user:`webknjaz`.

  Their corresponding identifiers are ``contrib`` and ``packaging``
  respectively. They are meant to be used for more accurate
  classification, where one would resort to using ``misc`` otherwise.

  *Related issues and pull requests on GitHub:*
  :issue:`539`.

- :pep:`660` is now enabled -- :user:`webknjaz`.

  This effectively means that the ecosystem-native editable
  install mode started working properly.

  *Related issues and pull requests on GitHub:*
  :issue:`541`.

- The duplicated jobs matrices for building manylinux wheels
  now reside in a single GitHub Actions CI/CD reusable
  workflow definition.

  -- :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`559`.

- The duplicated jobs matrices of the text jobs now reside in
  a single GitHub Actions CI/CD reusable workflow definition.

  -- :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`560`.

- Fixed the location of release workflow in the
  :ref:`Release Guide` document -- by :user:`Qalthos`.

  *Related issues and pull requests on GitHub:*
  :issue:`565`.

- The ``setuptools-scm`` build dependency CI pin was updated to 8.1.0 —
  this version fixes a date parsing incompatibility introduced by Git 2.45.0
  (:gh:`pypa/setuptools_scm#1039 <pypa/setuptools_scm/issues/1038>`,
  :gh:`pypa/setuptools_scm#1038 <pypa/setuptools_scm/pull/1039>`)
  -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`601`.

- The CI/CD configuration was fixed to allow publishing
  to PyPI and other targets disregarding the test stage
  outcome. This used to be a bug in the workflow definition
  that has now been fixed.

  -- by :user:`pbrezina` and :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`602`.


----


v1.1.0 (2022-12-05)
===================

Features
--------

- Started building ``manylinux`` wheels with ``libssh`` v0.9.6
  -- by :user:`webknjaz`
  (:issue:`441`)


Deprecations (removal in next major release)
--------------------------------------------

- The project stopped being tested under Ubuntu 18.04 VM since
  GitHub is sunsetting their CI images -- by :user:`webknjaz`
  (:issue:`381`)


Documentation
-------------

- Added a :ref:`Release Guide` for making new releases
  -- by :user:`webknjaz`
  (:issue:`413`)


Miscellaneous
-------------

- Started testing RPM packaging spec with Packit service
  -- by :user:`webknjaz` and :user:`TomasTomecek`
  (:issue:`227`,
  :issue:`246`)
- Removed the remains of Python 2 compatiblity code from the in-tree :pep:`517` build backend -- by :user:`webknjaz`
  (:issue:`377`)
- Fixed removing ``expandvars`` from ``pyproject.toml``
  in an RPM spec -- by :user:`webknjaz`

  Before this patch, the ``sed`` invocation removed entire
  ``build-system.requires`` entry from there, in rare cases
  but this won't be happening anymore.
  (:issue:`378`)
- Declared official support of CPython 3.11 -- by :user:`Qalthos`
  (:issue:`396`)
- Started shipping sdists built with Cython v0.29.32 -- by :user:`webknjaz`
  (:issue:`399`)
- Started building RPMs with Cython v0.29.32 -- by :user:`webknjaz`
  (:issue:`402`)
- Added an SSH connection re-try helper to tests -- by :user:`webknjaz`
  (:issue:`405`)


v1.0.0 (2022-09-14)
===================

Features
--------

- Added ``password_prompt`` argument to ``connect()`` to override the default
  prompt of "password:" when using keyboard-interactive authentication -- by :user:`Qalthos`
  (:issue:`331`)
- Added support for ``:fd:`` socket option -- by :user:`sabedevops`
  (:issue:`343`)


Miscellaneous
-------------

- Reworked build scripts to fix manylinux container generation -- by :user:`Qalthos`
  (:issue:`321`)
- Reenable CI building on s390x -- by :user:`Qalthos`
  (:issue:`322`)


v0.4.0 (2022-04-26)
===================

Bugfixes
--------

- Improved ``channel.exec_command`` to always use a newly created ``ssh_channel`` to avoid
  segfaults on repeated calls -- by :user:`Qalthos`
  (:issue:`280`)
- Fixed password prompt match in ``pylibsshext.session.Session.authenticate_interactive()``
  to strip whitespace, check that the prompt only ends with ``password:``, and added
  a little extra logging -- by :user:`dalrrard`
  (:issue:`311`)


Backward incompatible changes
-----------------------------

- Dropped support for Python 2.7 and 3.5, and marked support for 3.10 -- by :user:`Qalthos`
  (:issue:`314`)


v0.3.0 (2021-11-03)
===================

Bugfixes
--------

- Changed ``sftp.sftp_get`` to write files as bytes rather than assuming files are valid UTF8 -- by :user:`Qalthos`
  (:issue:`216`)


Features
--------

- Started building platform-specific ``manylinux2010``, ``manylinux2014``
  and ``manylinux_2_24`` wheels for AARCH64, ppc64le and s390x
  architectures as introduced by :pep:`599` and :pep:`600`
  -- :user:`webknjaz`
  (:issue:`187`)
- Added gssapi-with-mic support for authentication -- by :user:`Qalthos`
  (:issue:`195`)


Documentation
-------------

- Correct a link to the pip upgrade doc in our installation guide
  -- :user:`webknjaz`
  (:issue:`225`)


Miscellaneous
-------------

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
--------

- Fixed ``undefined symbol: ssh_disconnect`` and related issues when building on certain distros -- by :user:`Qalthos`
  (:issue:`63`,
  :issue:`153`,
  :issue:`158`)
- Fixed ``"Negative size passed to PyBytes_FromStringAndSize"`` when ``ssh_channel_read_nonblocking`` fails -- by :user:`Qalthos`
  (:issue:`168`)


Features
--------

- Added SCP support -- by :user:`Qalthos`
  (:issue:`151`,
  :issue:`157`)


Documentation
-------------

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
-------------

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
--------

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
--------

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
-----------------------------

- Updated the package name to ``ansible-pylibssh`` to reflect
  that the library only intends to implement a set of APIs that
  are necessary to implement an Ansible connection plugin
  -- by :user:`ganeshrn`
  (:issue:`1`)


Documentation
-------------

- Documented how to compose `Towncrier
  <https://towncrier.readthedocs.io/en/actual-freaking-docs/>`__
  news fragments -- by :user:`webknjaz`
  (:issue:`124`)
- Documented how to contribute to the docs -- by :user:`webknjaz`
  (:issue:`126`)


Miscellaneous
-------------

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
