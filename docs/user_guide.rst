.. _intro_getting_started:

##########
User Guide
##########

Welcome to the |project| User Guide!

This guide covers how to work with |project|.

***************
Getting Started
***************

Now that you have read the :ref:`installation guide<installation_guide>` and installed |project| on a your system.

.. contents::
   :local:

Checking libssh version
=======================

.. code-block:: python

   from pylibsshext._libssh_version import LIBSSH_VERSION

   print(LIBSSH_VERSION)

Creating a SSH session
======================

.. code-block:: python

   from pylibsshext.session import Session
   from pylibsshext.errors import LibsshSessionException

   ssh = Session()


Connecting with remote SSH server
=================================

.. code-block:: python

  HOST = "CHANGEME"
  USER = "CHANGEME"
  PASSWORD = "CHANGEME"
  TIMEOUT = 30
  PORT = 22
  try:
      ssh.connect(
          host=HOST,
          user=USER,
          password=PASSWORD,
          timeout=TIMEOUT,
          port=PORT,
      )
  except LibsshSessionException as ex:
     print(str(ex))

  print(ssh.is_connected)

Passing a command and reading response
======================================

.. code-block:: python

  chan = ssh.new_channel()
  print("stdout:\n%s\n stderr:\n%s\n returncode:\n%s\n" % (resp.stdout, resp.stderr, resp.returncode))
  chan.close()

Opening a remote shell passing command and receiving response
=============================================================
.. code-block:: python

  chan_shell = ssh.invoke_shell()
  chan_shell.sendall("ls")
  data = chan_shell.read_bulk_response(timeout=2, retry=10)
  chan_shell.close()
  print(data)

Fetch file from remote host
===========================
.. code-block:: python

  remote_file = '/etc/hosts'
  local_file = '/tmp/hosts'
  sftp = SFTP(ssh)
  sftp.get(remote_file, local_file)
  sftp.close()

Copy file from remote host
===========================
.. code-block:: python

  remote_file = '/etc/hosts'
  local_file = '/tmp/hosts'
  sftp = SFTP(ssh)
  sftp.put(remote_file, local_file)
  sftp.close()

Closing SSH session
===================

.. code-block:: python

   ssh.close()
