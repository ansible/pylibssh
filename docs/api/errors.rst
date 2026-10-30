Exceptions
==========

.. py:module:: pylibsshext.errors

.. py:exception:: LibsshChannelEOFError

   Raised when the remote side has closed a channel and all buffered data
   has been returned. Currently, ``Channel.read_bulk_response()`` raises
   it.

   It inherits from ``LibsshChannelReadFailure``, and therefore from
   :exc:`ConnectionError`, as well as from :exc:`EOFError`, so it can be
   handled as any of them.
