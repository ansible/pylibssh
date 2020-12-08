******************************
Getting Started with |project|
******************************

Now that you have read the :ref:`installation guide <Installing |project|>` and
installed |project| on a your system.

.. contents::
   :local:


.. tip::

   The examples on this page use Python 3.8. If your interpreter
   is older, you may need to modify the syntax when copying the
   snippets.


Checking software versions
==========================

.. literalinclude:: _samples/get_version.py
   :language: python


Creating a SSH session
======================

.. attention::

   The APIs that are shown below, are low-level. You should
   take a great care to ensure you process any exceptions that
   arise and always close all the resources once they are no
   longer necessary.

.. literalinclude:: _samples/shell.py
   :language: python
   :lines: -5
   :emphasize-lines: 5


Connecting with remote SSH server
=================================

.. literalinclude:: _samples/shell.py
   :language: python
   :lines: 7-23
   :emphasize-lines: 7-13


Passing a command and reading response
======================================

.. literalinclude:: _samples/shell.py
   :language: python
   :lines: 25-30
   :emphasize-lines: 2


Opening a remote shell passing command and receiving response
=============================================================

.. literalinclude:: _samples/shell.py
   :language: python
   :lines: 32-36
   :emphasize-lines: 2-3


Fetch file from remote host
===========================

Using SCP:

.. literalinclude:: _samples/copy_files_scp.py
   :language: python
   :lines: 25-28
   :emphasize-lines: 3-4

Using SFTP:

.. literalinclude:: _samples/copy_files_sftp.py
   :language: python
   :lines: 25-29
   :emphasize-lines: 3-4


Copy file to remote host
========================

Using SCP:

.. literalinclude:: _samples/copy_files_scp.py
   :language: python
   :lines: 30-33
   :emphasize-lines: 3-4

Using SFTP:

.. literalinclude:: _samples/copy_files_sftp.py
   :language: python
   :lines: 31-35
   :emphasize-lines: 3-4


Closing SSH session
===================

.. literalinclude:: _samples/shell.py
   :language: python
   :lines: 38
