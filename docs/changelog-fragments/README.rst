.. _howto_add_change_notes:

=================================
Adding change notes with your PRs
=================================

Examples for changelog entries adding to your Pull Requests:

file ``docs/changelog-fragments/112.doc.rst``:

.. code-block:: rst

    Added a ``:user:`` role to Sphinx config -- by :user:`webknjaz`

file ``docs/changelog-fragments/105.feature.rst``:

.. code-block:: rst

    Added the support for keyboard-authentication method -- by :user:`Qalthos`

file ``docs/changelog-fragments/57.bugfix.rst``:

.. code-block:: rst

    Fixed flaky SEGFAULTs in ``pylibsshext.channel.Channel.exec_command()``
    calls -- by :user:`ganeshrn`

.. tip::

   See ``pyproject.toml`` for all available categories
   (``tool.towncrier.type``).
