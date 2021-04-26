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
   :end-at: ssh = Session()
   :emphasize-lines: 5


Connecting with remote SSH server
=================================

.. literalinclude:: _samples/shell.py
   :language: python
   :start-at: HOST = 'CHANGEME'
   :end-at: print(f'{ssh.is_connected=}')
   :emphasize-lines: 7-13


Connecting over GSSAPI
----------------------

.. attention::

   This requires that your libssh is compiled with GSSAPI support
   enabled.

Using GSSAPI, password or private key is not necessary, but client and
service principals may be specified.

.. literalinclude:: _samples/gssapi.py
   :language: python
   :start-at: ssh.connect(
   :end-before: except LibsshSessionException as ssh_exc:
   :dedent: 4


Passing a command and reading response
======================================

.. literalinclude:: _samples/shell.py
   :language: python
   :start-at: ssh_channel = ssh.new_channel()
   :end-at: ssh_channel.close()
   :dedent: 4
   :emphasize-lines: 3


Opening a remote shell passing command and receiving response
=============================================================

.. literalinclude:: _samples/shell.py
   :language: python
   :start-at: chan_shell = ssh.invoke_shell()
   :end-at: chan_shell.close()
   :dedent: 4
   :emphasize-lines: 3-4


Fetch file from remote host
===========================

Using SCP:

.. literalinclude:: _samples/copy_files_scp.py
   :language: python
   :lines: 26-29
   :dedent: 4
   :emphasize-lines: 3-4

Using SFTP:

.. literalinclude:: _samples/copy_files_sftp.py
   :language: python
   :lines: 26-32
   :dedent: 4
   :emphasize-lines: 3,5


Copy file to remote host
========================

Using SCP:

.. literalinclude:: _samples/copy_files_scp.py
   :language: python
   :lines: 26-27,31-32
   :dedent: 4
   :emphasize-lines: 3-4

Using SFTP:

.. literalinclude:: _samples/copy_files_sftp.py
   :language: python
   :lines: 26-27,34-38
   :dedent: 4
   :emphasize-lines: 3,5


Closing SSH session
===================

.. literalinclude:: _samples/shell.py
   :language: python
   :start-at: ssh.close()
   :dedent: 4
