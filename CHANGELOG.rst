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

v1.5.0a3
========

*(2026-10-19)*


Bug fixes
---------

- Removed non-mandatory EOF check after the SCP download procedure, which was causing race conditions with some Cisco devices -- by :user:`timway`.

  *Related issues and pull requests on GitHub:*
  :issue:`785`, :issue:`786`.

- The version detection fallback, used when the build-time generated
  version module is missing, now relies on :mod:`importlib.metadata`
  instead of ``pkg_resources`` that is unavailable with recent
  ``setuptools`` releases -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`900`.


Features
--------

- Formalized the ``SFTP.get()`` and ``SFTP.put()`` API to accept
  :class:`os.PathLike` type in addition to :class:`str` type for
  local paths -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`885`.


Removals and backward incompatible breaking changes
---------------------------------------------------

- Changed the ``Channel.write()`` API to accept only :class:`bytes` type.
  Previously, this API used to accept anything that could have been converted
  to a pointer using :c:func:`PyBytes_AS_STRING` and that would implement
  :meth:`~object.__len__()` interface, which could result in unexpected behavior
  even for UTF8 strings. Anything else than :class:`bytes` now raises
  :exc:`TypeError` -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`875`.

- Changed the ``SFTP.get()`` and ``SFTP.put()`` API to accept only
  :class:`str` type for remote paths.

  Previously, this API used to accept also raw :class:`bytes` type, which
  required something on the way to guess the real encoding. Anything other
  than :class:`str` now raises :exc:`TypeError` -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`885`.


Improved documentation
----------------------

- Added docstrings for ``SFTP.get()`` and ``SFTP.put()``
  methods -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`870`.


Packaging updates and notes for downstreams
-------------------------------------------

- The macOS wheels are now ``universal2``, running natively on both Intel
  and Apple Silicon. They bundle ``libssh`` 0.12.2 with a statically linked
  OpenSSL, built by the project's own CI as in :issue:`884`, instead of the
  Homebrew ones, which also lowers their minimum macOS version from 15.0 to
  10.12, or what the Python version requires -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`73`, :issue:`207`, :issue:`917`.

- The source distribution now ships a minimal generated
  :file:`setup.cfg` with the core packaging metadata, so that
  downstreams can still build it with ``setuptools`` older than 61,
  which cannot read :pep:`621` metadata -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`812`.

- The RPM spec now relaxes the ``setuptools`` requirement and the
  :pep:`639` license metadata on RHEL 10 and older, whose
  ``setuptools`` releases predate their support -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`812`.

- The core packaging metadata is now declared in the :pep:`621`
  ``[project]`` table of :file:`pyproject.toml` instead of
  :file:`setup.cfg`, with the license expressed per :pep:`639`, which
  requires ``setuptools`` 77.0.1 or newer -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`812`.

- Removed the :pypi:`expandvars` build dependency while preserving existing
  compiler and linker flags -- by :user:`f321x`.

  *Related issues and pull requests on GitHub:*
  :issue:`888`.

- Fixed the Linux wheels being compiled without optimization. The
  ``cibuildwheel`` configuration set ``CFLAGS`` to point at the bundled
  ``libssh`` headers, and the build backend set it to add the Cython
  line tracing macro for coverage builds; ``setuptools`` replaces the
  interpreter's own compiler flags with a ``CFLAGS`` environment variable
  instead of extending them, so ``-O3`` was dropped. Both now go through
  ``CPPFLAGS``, which ``setuptools`` appends to the interpreter's flags
  -- by :user:`bdraco`.

  *Related issues and pull requests on GitHub:*
  :issue:`890`.

- The test suite now optionally depends on :pypi:`proxy.py`. The tests
  needing it are skipped when it is not installed, and the RPM spec does
  not pull it in, since it is not packaged downstream yet -- by
  :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`894`.

- The core packaging metadata now reflects that we test the project under
  Python 3.15 (with GIL enabled) -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`911`.


Contributor-facing changes
--------------------------

- The in-tree guidance for agents on house style, silenced checks,
  and the house rules now keeps project-specific examples apart from
  the rules shared with other projects
  -- steered by :user:`webknjaz`, typed by a robot that errs.

  *Related commits on GitHub:*
  :commit:`122a1f1f`.

- The in-tree guidance for AI agents now asks for commit messages
  that pass ``gitlint``
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`807a23e`.

- Claude Code now prompts the human operator before applying edits or
  running commands that look like they silence linters or tests, or that
  change tool configuration -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`083858a9`.

- Claude Code now also asks the operator before an agent edits the
  ``codespell``, ``darglint``, ``isort``, ``nitpick`` and
  ``pylint`` configs, and the ``.mypy.ini`` file that it previously
  missed
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`5ab7c57`.

- The in-tree guidance for AI agents now requires an explicit decision
  from the human operator, case by case, before any check gets silenced
  -- whether by adding linter suppressions, relaxing tool configuration,
  or skipping, removing or weakening tests -- and asks for tool
  configuration changes to be kept in standalone commits
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`a55c74ff`.

- Codespell now has a dedicated settings file in the tree with a few
  currated dictionaries set up and preselected exclusions allowed
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`9b135663`.

- The in-tree guidance for AI agents now spells out the project's
  structural constraints and its Python, YAML and Markdown style
  conventions, including those not enforced by any linter
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`2b149b58`.

- Restored coverage collection for the Cython modules in CI, which had
  reported nothing since :pr:`688` -- by :user:`rodrigobnogueira`.

  *Related commits on GitHub:*
  :commit:`3b3d4d11`, :commit:`5919568ed1f2f88751491d105932360071132e7b`.

- The in-tree guidance for agents on PRs and change notes now keeps
  project-specific facts apart from the rules shared with other
  projects
  -- steered by :user:`webknjaz`, typed by a robot that errs.

  *Related commits on GitHub:*
  :commit:`bbad5215`.

- The in-tree guidance for AI agents now covers the commit message
  shape, the use of long ``tox`` subcommands without invented flags,
  and flagging generic tooling changes for reuse across the
  maintainer's other projects. It also clarifies that agents are never
  credited as co-authors, with an optional ``Assisted-by`` trailer
  for disclosing AI assistance
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`9be75f22`.

- The in-tree guidance for AI agents now mentions the Claude Code
  hook that asks the operator before license changes
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`cd8009e`.

- The in-tree guidance for AI agents now states that license terms,
  license metadata and license headers only change with the
  maintainer's explicit approval, and that code copied in from
  elsewhere keeps its original license
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`03dec85`.

- The in-tree guidance for AI agents now asks for the authors of
  incorporated patches to be credited via ``Co-Authored-By`` trailers
  and leaves the change note byline off fully agentic work
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`1227e231`.

- The in-tree guidance for AI agents now requires the human operator to
  agree on how to proceed before an agent acts on review comments,
  suggested patches or discussion input from others, and forbids agents
  from force-pushing mid-review -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`5105e647`.

- Claude Code now asks the operator before an agent edits license
  files, drops license notices or changes license metadata
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`2e985de`.

- The emulated Linux wheel builds stopped rebuilding the ``aarch64``
  and ``x86_64`` wheels that native runners already produce, which had
  pushed the release job past its time limit.

  *Related commits on GitHub:*
  :commit:`364f7f9`.

- The Codecov statuses now display separate measurements for Cython and
  Python modules in the library, in addition on the overall number
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`5f974f89`.

- The in-tree guidance for AI agents now gives a reading order for
  getting oriented in the repository and a map of its less obvious
  directories
  -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`9faac80a`.

- The in-tree guidance for agents on testing now keeps
  project-specific facts apart from the rules shared with other
  projects, and no longer claims that ``darglint`` checks test
  docstrings
  -- steered by :user:`webknjaz`, typed by a robot that errs.

  *Related commits on GitHub:*
  :commit:`f97d68ec`.

- The CI now runs testing against ARM Ubuntu VMs that
  GitHub Actions CI/CD provide -- by :user:`webknjaz`.

  The dists are now built under native runners instead
  of QEMU which makes the CI resources use efficient.

  *Related issues and pull requests on GitHub:*
  :issue:`674`, :issue:`761`.

- Traced builds of the Cython modules now define ``CYTHON_USE_SYS_MONITORING=0``,
  so that the ``Cython.Coverage`` plugin receives line events on CPython 3.13 and
  newer -- by :user:`rodrigobnogueira`.

  *Related issues and pull requests on GitHub:*
  :issue:`781`.

- Added Centos 10 Stream image to the CI/CD pipeline -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`830`.

- Added Centos 9 Stream image to the CI/CD pipeline -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`831`.

- Updated the version of ``libssh`` to the latest release v0.12.1
  in the cached ``manylinux`` build environment container images
  -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`846`.

- Updated the bundled version of libssh to 0.12.2 in platform-specific
  wheels published on PyPI -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`847`.

- Fixed Packit CI caused by ``setuptools_scm`` version mismatch
  in build environment -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`848`.

- Updated the version of ``libssh`` to the latest release v0.12.2
  in the cached ``manylinux`` build environment container images
  -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`851`.

- Dropped the EOL Fedora 42 from CI targets -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`852`.

- The repository now has initial infrastructure for pet agents to lurk in and
  understand how to interact with the project in a useful, constructive and
  collaborative manner while being exposed to the same quality development
  tools their humans are -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`867`.

- Added the UBI 9.8 container image to the CI test matrix -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`876`.

- Added a scheduled GitHub Actions workflow that builds a prebuilt shared
  ``libssh`` library with a statically linked OpenSSL for macOS
  ``x86_64``, ``arm64`` and ``universal2``, storing them as workflow
  artifacts, following the pattern established by `pyca/infra
  <https://github.com/pyca/infra>`_. This artifact is not yet consumed by
  the wheel build process -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`883`, :issue:`884`.

- The ``test_open_session_small_timeout`` test now withholds the sshd
  replies through a TCP relay instead of racing a local sshd, which
  made it flaky with line tracing enabled -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`894`.

- The test suite gained a home for test doubles of the components that
  end-to-end tests intercept, under :file:`tests/_stubs/`. Each of them
  exposes its fixtures through a ``fixtures.py`` module, which gets
  loaded as a local pytest plugin automatically -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`894`.

- The test coverage measurement now includes code running in processes
  started via :py:mod:`multiprocessing`, which ``pytest-cov`` 7 stopped
  measuring on its own -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`898`.

- The ``lint`` :std:doc:`tox <tox:index>` environment has been renamed to
  ``pre-commit`` -- invoke it as ``tox run -e pre-commit`` now
  -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`899`.

- The linting jobs in CI now run through the ``reusable-tox.yml`` workflow
  shared with other projects, and cache the ``pre-commit`` virtualenvs
  between runs -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`899`.

- The Python code is now type-checked with MyPy in strict mode
  against every supported Python version, as a part of the
  ``pre-commit`` setup -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`901`.

- The test suite now gives up waiting for the ephemeral ``sshd``
  to become ready after a bounded number of connection attempts,
  instead of hanging when it never comes up -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`902`.

- Ruff now targets Python 3.9, the oldest Python version supported
  by the project, instead of its own default -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`903`.

- The in-tree :pep:`517` build backend has been adjusted to pass
  strict type checking for every supported Python version
  -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`904`.

- The test suite now waits for up to 10 seconds for the ephemeral
  ``sshd`` to become ready, instead of giving up after a fixed number
  of connection attempts that fast-failing machines could exhaust
  early -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`905`.

- The MyPy type coverage reports are now uploaded to Coveralls from
  CI, summarized on the workflow run pages and linked to after local
  runs -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`906`.

- Added an expected-to-fail test documenting that
  ``pylibsshext.channel.Channel.read_bulk_response()`` keeps returning
  empty bytes after the remote side closes the channel, instead of
  signaling the end of the stream -- by :user:`Ajithkumar2000`.

  *Related issues and pull requests on GitHub:*
  :issue:`907`.

- The RPM builds in UBI 9 and CentOS Stream 9 containers are no longer
  required to pass in CI, since these only provide tox 3 that cannot
  parse the project's tox 4 configuration -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`909`.

- The CI job building the emulated ``manylinux`` wheels now gets up
  to 3 hours, since optimized builds take over twice as long under
  QEMU -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`910`.

- The CI now tests wheels built for Python 3.15 -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`911`.

- The RPM smoke tests in CI now live in a reusable workflow, configured
  through inputs, with the container matrix kept in the main workflow
  -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`912`.

- The CI job building the macOS wheels now gets up to 15 minutes, since
  it occasionally ran out of time right before finishing the last
  wheels -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`913`.

- The in-tree guidance for agents now asks them to re-read it as it
  evolves, to verify claims instead of relying on memory, to fill in
  the PR template, to add change notes for every affected audience,
  to check in on how involved the human operator feels before
  crediting them, and to let the operator confirm any force-push
  command they run -- steered by :user:`webknjaz`, typed by a robot
  that errs.

  *Related issues and pull requests on GitHub:*
  :issue:`915`.

- The Claude Code guard against silencing checks now also covers
  edits in other Git worktrees of the repository -- steered by
  :user:`webknjaz`, typed by a robot that errs.

  *Related issues and pull requests on GitHub:*
  :issue:`915`.

- The test jobs now download only the distribution packages instead of
  every workflow artifact -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`918`.

- The manylinux container images used for building the wheels no longer
  compile a custom Perl, which was only ever meant for the ``manylinux1``
  images -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`920`.

- The in-tree guidance for agents on running the project's tooling
  now keeps project-specific examples apart from the rules shared
  with other projects
  -- steered by :user:`webknjaz`, typed by a robot that errs.

  *Related issues and pull requests on GitHub:*
  :issue:`31154463`.


Miscellaneous internal changes
------------------------------

- Removed the needless use of CPython internal API
  :c:func:`PyBytes_AS_STRING` throughout the code to simplify code
  and improve the compatibility with limited Python API -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`875`.


----


v1.4.0
======

*(2026-03-15)*


Bug fixes
---------

- Fixed the log level mapping to cover the entire ``libssh`` range
  -- by :user:`Jakuje` and :user:`webknjaz`.

  Previously it was not possible to set the most verbose ``libssh`` log level
  ``SSH_LOG_TRACE`` to get the most verbose log messages useful for debugging
  connection issues.

  *Related issues and pull requests on GitHub:*
  :issue:`597`.


Features
--------

- Made ``libssh`` use the Python :external+python:mod:`logging` system
  -- by :user:`Jakuje` and :user:`webknjaz`.

  Previously the underlying ``libssh`` library was writing its logs directly
  from the C-level into ``stderr``, which caused inconsistent behavior.

  The default log level is now set to :data:`ANSIBLE_PYLIBSSH_TRACE`
  and the downstream loggers are able to trim the verbosity down.
  If you need performance, it is possible to disable logging on the ``libssh``
  side at the source by setting a lower logging value, for example:

  .. code-block:: python

     ssh_session.set_log_level(ANSIBLE_PYLIBSSH_NOLOG)

  Additionally, the log level can be now be set also through the session initializer:

  .. code-block:: python

     ssh = Session(log_verbosity=ANSIBLE_PYLIBSSH_TRACE)


  or the ``connect()`` method arguments:

  .. code-block:: python

     ssh.connect(log_verbosity=ANSIBLE_PYLIBSSH_TRACE)

  Setting any levels imported from :external+python:mod:`!logging` is also supported.

  *Related issues and pull requests on GitHub:*
  :issue:`597`.


Packaging updates and notes for downstreams
-------------------------------------------

- Started shipping binary ``armv7l`` wheels -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`648`.

- Upgrading :pypi:`cibuildwheel` to v2.22.0 also picked up Python 3.13
  and enabled respective wheels to be built -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`648`.

- The CI/CD/packaging infrastructure has been updated to produce
  :external+packaging:term:`source distribution <Source Distribution (or "sdist")>`
  file names consistent with the requirement of uploading artifacts
  compliant with the core packaging metadata 2.2 or newer to PyPI and
  TestPyPI -- by :user:`webknjaz`.

  Along with that, the infrastructure has been adjusted to expect
  :pep:`625`-conforming names in its guard rails checks
  -- with some :user:`cidrblock`\ s help.

  *Related issues and pull requests on GitHub:*
  :issue:`808`, :issue:`809`.

- Upgrading :pypi:`cibuildwheel` to v3.1.0 also picked up Python 3.14
  and enabled respective wheels to be built -- by :user:`webknjaz`.

  Building the free-threaded wheels remains disabled, though.

  *Related issues and pull requests on GitHub:*
  :issue:`809`, :issue:`823`.

- While upgrading :pypi:`cibuildwheel` to v3.1.4, its defaults changed to
  attempt building wheels for the RISC-V architecture. This target is now
  disabled explicitly due to the lack of infrastructure
  -- by :user:`webknjaz`.

  We may enable it at a later time as a separate dedicated effort.

  *Related issues and pull requests on GitHub:*
  :issue:`809`, :issue:`824`.

- Due to :pypi:`cibuildwheel` to v3 bundling :pypi:`delocate` 0.13.0 that
  enforces deployment-target consistency with the brew-installed copy of
  the ``libssh`` in the build jobs, the macOS wheels we build now require
  macOS version 15.0 or newer.

  -- by :user:`cidrblock` and :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`809`, :issue:`824`.

- The core packaging metadata now reflects that we test the project under
  Python 3.13 and 3.14 (with GIL enabled)
  -- by :user:`cidrblock` and :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`809`, :issue:`825`.

- The pre-cached ``armv7l`` images we build for the packaging
  infrastructure are now correctly tagged with the ``linux/arm/v7``
  OCI platform tag -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`810`.

- The build backend configuration no longer sets the deprecated
  ``bdist_wheel.universal`` setting -- by :user:`webknjaz`.

  This does not influence the packaging artifacts in any way.

  *Related issues and pull requests on GitHub:*
  :issue:`811`.

- The build backend has been configured to exclude
  :file:`.git_archival.txt` from source distributions built from Git
  -- by :user:`webknjaz`.

  This reduces the number of false positive warning the backend outputs.

  *Related issues and pull requests on GitHub:*
  :issue:`811`.


Contributor-facing changes
--------------------------

- The repository is now set up to auto-format Python files with Ruff.
  Cython keeps being formatted by ``cython-lint``.

  -- by :user:`webknjaz`

  *Related commits on GitHub:*
  :commit:`234a2d34`, :commit:`a63b6028`, :commit:`0e385696`.

- The linting configuration now uses Ruff to run additional checks on
  pure Python modules -- by :user:`webknjaz`.

  *Related commits on GitHub:*
  :commit:`817095443f6afa4b3822780110712db148693075`.

- ``cibuildwheel`` started making use of the ``armv7l`` container image
  following its upgrade to v2.22.0 -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`648`.

- Increased the amount of retries in test to avoid possible timeouts
  on slower systems -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`777`.

- The SSHD start probe client command is now shielded from external
  environmnent and will no longer attempt using an SSH agent on the
  machine where the tests are involved, nor will it use alternative
  authentication methods -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`782`.

- Now that the ``macos-13`` runner VM image has been decommissioned, the CI and CD jobs have been migrated to use ``macos-15-intel`` -- by :user:`komaldesai13`.

  This includes giving the macOS build job more time to complete as the new version is a little slower.

  *Related issues and pull requests on GitHub:*
  :issue:`791`.

- Updated the version of ``libssh`` to the latest release v0.12.0
  in the cached ``manylinux`` build environment container images
  -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`797`.

- Updated the bundled version of libssh to 0.12.0 in platform-specific
  wheels published on PyPI -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`798`.

- Added Fedora and ubi9 images to CI/CD pipeline that are relevant in 2026
  and removed EOL Fedora versions -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`801`.

- The ``pre-commit`` framework configuration has been updated to be in
  sync with ``awx-plugins`` and other projects. It now has a few
  additional linters and a workaround for the outdated ones.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`803`.

- The standalone mentions of ``pylibssh`` have been replaced with
  ``ansible-pylibssh`` in file license headers -- by :user:`Jakuje`.

  *Related issues and pull requests on GitHub:*
  :issue:`804`.

- The CI/CD/packaging infrastructure has been updated to produce
  :external+packaging:term:`source distribution <Source Distribution (or "sdist")>`
  file names consistent with the requirement of uploading artifacts
  compliant with the core packaging metadata 2.2 or newer to PyPI and
  TestPyPI -- by :user:`webknjaz`.

  Along with that, the infrastructure has been adjusted to expect
  :pep:`625`-conforming names in its guard rails checks
  -- with some :user:`cidrblock`\ s help.

  *Related issues and pull requests on GitHub:*
  :issue:`808`, :issue:`809`.

- :pypi:`cibuildwheel` has been upgraded to v3.1.4 -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`809`, :issue:`820`, :issue:`821`, :issue:`823`, :issue:`824`.

- The coverage measurement infrastructure now uses the ``ctrace``
  :external+coveragepy:std:ref:`measurement core <config_run_core>`
  across all the Python versions consistently -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`809`, :issue:`825`.

- The CI now tests wheels built for Python 3.13 and 3.14
  -- by :user:`cidrblock` and :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`809`, :issue:`825`.

- The pre-cached ``armv7l`` images we build for the packaging
  infrastructure are now correctly tagged with the ``linux/arm/v7``
  OCI platform tag -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`810`.

- The build backend configuration no longer sets the deprecated
  ``bdist_wheel.universal`` setting -- by :user:`webknjaz`.

  This does not influence the packaging artifacts in any way.

  *Related issues and pull requests on GitHub:*
  :issue:`811`.

- The CI/CD infrastructure has been set up to avoid parts of the template
  injection problem in GitHub Actions workflow definitions. The shell
  entry point has been set to bash for any scripts with extra strictness
  enabled.

  -- by :user:`webknjaz`

  *Related issues and pull requests on GitHub:*
  :issue:`816`.

- The CI/CD and packaging infrastructure now sources the PyPI project name
  from :file:`setup.cfg` rather than hardcoding it -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`817`.

- The documentation building infrastructure now integrates GitHub-related
  RST roles using the :pypi:`sphinx-issues` extension -- by :user:`webknjaz`.

  *Related issues and pull requests on GitHub:*
  :issue:`818`.


----


v1.3.0
======

*(2025-10-12)*


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
  (:issue:`pypa/setuptools_scm#1038`, :pr:`pypa/setuptools_scm#1039`)
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
  (:issue:`pypa/setuptools_scm#1038`, :pr:`pypa/setuptools_scm#1039`)
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
- Removed the remains of Python 2 compatibility code from the in-tree :pep:`517` build backend -- by :user:`webknjaz`
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
- Re-enable CI building on s390x -- by :user:`Qalthos`
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
  update session exception to ``LibsshSessionException`` -- by :user:`ganeshrn`
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
