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


Before you start
================

  1. **Check for existing work.** Search open `pull requests`_ and
     `issues`_ to see if someone is already working on the same area.
     This avoids duplicate effort and conflicting changes.

  2. **Review the** ``devel`` **branch.** Look at recent commits and
     in-flight PRs to understand what is currently being worked on.

  3. **Discuss scope first.** If your change touches multiple areas
     (e.g. CI, packaging, and documentation), open an issue to
     discuss the approach before writing code. Smaller, focused
     changes are easier to review and merge.


How to contribute
=================

  1. Fork the repository.

  2. Create a branch, push your changes there. Don't forget to
     :ref:`include news files for the changelog <Adding change
     notes with your PRs>`.

  3. Send it to us as a PR. Fill out the `pull request template`_
     completely — including **SUMMARY**, **ISSUE TYPE**, and
     **ADDITIONAL INFORMATION**.

  4. Iterate on your PR, incorporating the requested improvements
     and participating in the discussions.


Pull request expectations
=========================

- **Prefer focused, atomic PRs** that address a single concern.
  Mixing unrelated changes (e.g. dependency bumps with test
  infrastructure changes) makes review harder and slows down
  the merge process.

- **Fill out the PR template.** PRs that do not use the template
  may be asked to resubmit. The template helps reviewers
  understand the rationale and scope of the change.

- **Include changelog fragments** for user-visible changes.
  See :ref:`Adding change notes with your PRs` for the format,
  categories, and available reStructuredText roles.

- **Understand the project context.** ansible-pylibssh is a
  Cython-based C-extension project with a custom :pep:`517`
  build backend. If your change touches the build system,
  CI workflows, or packaging, take time to understand how the
  existing pieces fit together before proposing changes.


CI and merge process
====================

- Before submitting, make sure the linters pass locally:

  .. code-block:: shell-session

     $ tox -e lint

- All GitHub Actions lint, test, and build checks should pass
  on your PR.

- Packit (RPM) checks may have pre-existing failures on
  ``devel``. If your PR shows Packit failures that also exist
  on the base branch, note this in a PR comment.

- The maintainer may fast-track infrastructure and packaging
  changes without external review. External contributions go
  through a full review cycle.


AI-assisted contributions
=========================

AI tools may be used to assist with contributions. However:

- **The PR author is solely accountable** for every line
  submitted. "The AI generated it" is not a justification
  for incorrect or inappropriate changes. Be ready to discuss
  your changes and justify every line.

- **Authors must demonstrate understanding** of the changes
  and familiarity with the project context. PRs that appear
  to lack project-specific understanding may be asked for
  clarification or closed.

- **Communicate as yourself.** When interacting in issues,
  pull requests, and discussions, do not use AI tools to speak
  for you (except for translation or grammar edits).
  Human-to-human communication is foundational to open source
  communities.

- **No autonomous submissions.** The use of agents that write
  code and submit pull requests without human review is not
  permitted.

- **Respect the project's conventions.** AI tools may not be
  aware of this project's build system, changelog format, or
  PR template. Review AI-generated output against the
  guidelines in this document before submitting.

- **Try to be brief.** Recognize when less is more. Aim for
  changes that reduce complexity rather than add to it.

.. note::

   Issues labeled ``good first issue`` are intended as learning
   opportunities for new contributors. Please be considerate of
   those who may benefit from these opportunities, and refrain
   from asking an AI tool to produce a complete solution.

.. caution::

   In extreme cases, low-quality PRs may be closed as spam.


Prerequisites
=============

  1. Have libssh_.

  2. Use tox_ to build the C-extension, docs and run the tests.


.. _libssh: https://www.libssh.org
.. _tox: https://tox.readthedocs.io
.. _pull requests: https://github.com/ansible/pylibssh/pulls
.. _issues: https://github.com/ansible/pylibssh/issues
.. _pull request template: https://github.com/ansible/pylibssh/blob/devel/.github/PULL_REQUEST_TEMPLATE.md
