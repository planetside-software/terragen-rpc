High Level Python API
=====================

The terragen_rpc module provides a Python API for making remote procedure calls to Terragen. It is intended to be a high level wrapper that lets you code stuff without thinking about TCP sockets or the JSON-RPC protocol.

Example usage:

.. literalinclude:: ../../rpc_examples.py

.. note::

   For more detailed information about exception handling, jump to :ref:`high-py-api:exceptions/errors`.
    


Module: terragen_rpc
-------------------------

.. automodule:: terragen_rpc.high
   :members:
   :member-order: bysource
   :exclude-members: Reply, Error, ReplyError, ApiError, LowLevelError

   
Exceptions/Errors
-----------------

We think that in production it's appropriate to handle at least **ConnectionError** and **TimeoutError** (the built-in Python exceptions) and **terragen_rpc.ReplyError**. These indicate issues that might be resolvable by the user at runtime, for example by restarting the server (Terragen) or resolving a network issue. A handler for these exceptions should give the user the opportunity to resolve them.

These and other exceptions are documented below.

Example:

.. code-block:: python

    import terragen_rpc as tg

    try:
        root = tg.root()
        # etc...
		
    except ConnectionError:
        # A built-in Python exception raised by the socket.
        # This probably means that Terragen isn't running or
        # there is a misconfiguration in Terragen or this client.
        print("Terragen RPC connection error")
        # Extra handling here...
        # ...
    except TimeoutError:
        # A built-in Python exception raised either by the socket
        # or by this module when a socket timeout occurs.
        # This could mean that the current instance of Terragen failed
        # to respond or that a previous instance has crashed without
        # properly closing the socket.
        print("Terragen RPC timeout error")
        # Extra handling here...
        # ...
    except tg.ReplyError:
        # The server responded, but the data it returned could not be parsed.
        print("Terragen RPC server reply error")
        # Extra handling here...
        # ...
    except tg.ApiError:
        # The server responded indicating that there was an API misuse. If
        # using the High Level API this probably means the server is running
        # a version of the API that is incompatible with this particular call.
        # Exception subclasses include ApiMethodNotFound and ApiInvalidParams.
        print("Terragen RPC API error")
        raise
    
**Base Class**

.. autoexception:: terragen_rpc.Error
   :members:

**Main Exceptions**

.. autoexception:: terragen_rpc.ReplyError
   :members:

.. autoexception:: terragen_rpc.ApiError
   :members:

.. autoexception:: terragen_rpc.LowLevelError
   :members:
   
**More Detailed Error Handling**

More exception subclasses and the ``Reply`` class are documented in :ref:`Low Level API Exceptions<low-py-api:exceptions>`.