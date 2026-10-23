Exceptions
==========

.. py:module:: pylibsshext.errors

.. py:exception:: LibsshChannelEOFError

   Raised by ``Channel.read_bulk_response()`` once the remote side has
   closed the channel and all buffered data has been returned.

   It inherits from ``LibsshChannelReadFailure``, and therefore from
   :exc:`ConnectionError`, as well as from :exc:`EOFError`, so it can be
   handled as any of them.
