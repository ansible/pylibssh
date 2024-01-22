---------------------------------
Adding change notes with your PRs
---------------------------------

It is very important to maintain a log for news of how
updating to the new version of the software will affect
end-users. This is why we enforce collection of the change
fragment files in pull requests as per `Towncrier philosophy`_.

The idea is that when somebody makes a change, they must record
the bits that would affect end-users only including information
that would be useful to them. Then, when the maintainers publish
a new release, they'll automatically use these records to compose
a change log for the respective version. It is important to
understand that including unnecessary low-level implementation
related details generates noise that is not particularly useful
to the end-users most of the time. And so such details should be
recorded in the Git history rather than a changelog.

-----------------------------------------
Alright! So how do I add a news fragment?
-----------------------------------------

To submit a change note about your PR, add a text file into the
``docs/changelog-fragments/`` folder. It should contain an
explanation of what applying this PR will change in the way
end-users interact with the project. One sentence is usually
enough but feel free to add as many details as you feel necessary
for the users to understand what it means.

**Use the past tense** for the text in your fragment because,
combined with others, it will be a part of the "news digest"
telling the readers **what changed** in a specific version of
the library *since the previous version*. You should also use
RST syntax for highlighting code (inline or block), linking
parts of the docs or external sites.
At the end, sign your change note by adding ``-- by
:user:`github-username``` (replace ``github-username`` with
your own!).

Finally, name your file following the convention that Towncrier
understands: it should start with the number of an issue or a
PR followed by a dot, then add a patch type, like ``feature``,
``doc``, ``contrib`` etc., and add ``.rst`` as a suffix. If you
need to add more than one fragment, you may add an optional
sequence number (delimited with another period) between the type
and the suffix.

In general the name will follow ``<pr_number>.<category>.rst`` pattern,
where the categories are:

- ``bugfix``: A bug fix for something we deemed an improper undesired
  behavior that got corrected in the release to match pre-agreed
  expectations.
- ``feature``: A new behavior, public APIs. That sort of stuff.
- ``deprecation``: A declaration of future API removals and breaking
  changes in behavior.
- ``breaking``: When something public gets removed in a breaking way.
  Could be deprecated in an earlier release.
- ``doc``: Notable updates to the documentation structure or build
  process.
- ``packaging``: Notes for downstreams about unobvious side effects
  and tooling. Changes in the test invocation considerations and
  runtime assumptions.
- ``contrib``: Stuff that affects the contributor experience. e.g.
  Running tests, building the docs, setting up the development
  environment.
- ``misc``: Changes that are hard to assign to any of the above
  categories.

A pull request may have more than one of these components, for example
a code change may introduce a new feature that deprecates an old
feature, in which case two fragments should be added. It is not
necessary to make a separate documentation fragment for documentation
changes accompanying the relevant code changes.

-----------------------------------------------------------
Examples for changelog entries adding to your Pull Requests
-----------------------------------------------------------

File ``docs/changelog-fragments/112.doc.rst`` (could be symlinked to
``docs/changelog-fragments/112.contrib.rst`` so it shows up in several
changelog sections):

.. code-block:: rst

    Added a ``:user:`` role to Sphinx config -- by :user:`webknjaz`.

    This change allows the contributors to be credited for their submitted
    patches in a more prominent manner.

File ``docs/changelog-fragments/105.feature.rst``:

.. code-block:: rst

    Added the support for keyboard-authentication method -- by :user:`Qalthos`.

File ``docs/changelog-fragments/57.bugfix.rst``:

.. code-block:: rst

    Fixed flaky SEGFAULTs in ``pylibsshext.channel.Channel.exec_command()``
    calls -- by :user:`ganeshrn`.

.. tip::

   See ``pyproject.toml`` for all available categories
   (``tool.towncrier.type``).

.. _Towncrier philosophy:
   https://towncrier.readthedocs.io/en/actual-freaking-docs/#philosophy
