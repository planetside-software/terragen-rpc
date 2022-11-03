Low Level Python API
====================


Module: terragen_rpc.jsonrpc
----------------------------

.. automodule:: terragen_rpc.jsonrpc
   :members:
   :member-order: bysource
   :exclude-members: Reply, Error, ReplyError, ApiError, ApiMethodNotFound, ApiInvalidParams, LowLevelError, LowLevelParseError, LowLevelInvalidRequest, LowLevelInternalError, LowLevelServerError

   
   
Exceptions
----------

We think that in production it's appropriate to handle at least **ConnectionError** and **TimeoutError** (the built-in Python exceptiona) and **terragen_rpc.ReplyError**. These indicate issues that might be resolvable by the user at runtime, for example by restarting the server (Terragen) or resolving a network issue. A handler for these exceptions should give the user the opportunity to resolve them.

These and other exceptions are documented below.

**Base Class**

.. autoexception:: terragen_rpc.jsonrpc.Error
   :members:

**Main Exceptions**

.. autoexception:: terragen_rpc.jsonrpc.ReplyError
   :members:

.. autoexception:: terragen_rpc.jsonrpc.ApiError
   :members:

.. autoexception:: terragen_rpc.jsonrpc.LowLevelError
   :members:
   
**Subclasses**

The following exceptions are subclasses of the main exception classes above. It is not expected that you catch these directly.

.. autoexception:: terragen_rpc.jsonrpc.ApiMethodNotFound
   :members:
    
.. autoexception:: terragen_rpc.jsonrpc.ApiInvalidParams
   :members:
    
.. autoexception:: terragen_rpc.jsonrpc.LowLevelParseError
   :members:
    
.. autoexception:: terragen_rpc.jsonrpc.LowLevelInvalidRequest
   :members:
    
.. autoexception:: terragen_rpc.jsonrpc.LowLevelInternalError
   :members:
    
.. autoexception:: terragen_rpc.jsonrpc.LowLevelServerError
   :members:


Reply Class
-----------

.. autoclass:: terragen_rpc.jsonrpc.Reply
   :members:
