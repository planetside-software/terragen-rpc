# MIT License
#
# Copyright (c) 2022 Planetside Software
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import terragen_rpc.impl as impl


class Error(Exception):
    """Base class for exceptions raised when an RPC call fails after
    making a successful connection.

    Has subclasses including ``ReplyError``, ``ApiError`` and
    ``LowLevelError``.

    Attributes
    ----------
    reply : Reply
        The Reply object being created when the exception was raised.
    """
    def __init__(self, reply, msg = ""):
        self.reply = reply
        super().__init__(msg)


class ReplyError(Error):
    """An exception raised when the server responds with data that
    could not be parsed. **We recommend that you catch and handle this
    exception.**

    A subclass of ``Error``.

    Attributes
    ----------
    reply : Reply
        The Reply object being created when the exception was raised.
    """
    def __init__(self, reply, msg = "Terragen RPC server responded with data that cannot be parsed."):
        super().__init__(reply, msg)


class ApiError(Error):
    """An exception raised when the reply from the server contains an
    error code that suggests an API mismatch between client and server
    or an incorrect use of the API. **We recommend that you catch and
    handle this exception.**

    A subclass of ``Error``.
    
    Has subclasses including ``ApiInvalidParams`` and
    ``ApiMethodNotFound``.

    Attributes
    ----------
    reply : Reply
        The Reply object being created when the exception was raised.
    """
    def __init__(self, reply):
        super().__init__(reply)


class LowLevelError(Error):
    """An exception raised when the reply from the server contains an
    error code that suggests a problem with its implementation, or when
    this module encounters an internal error.

    A subclass of ``Error``.

    Has subclasses including ``LowLevelParseError``,
    ``LowLevelInvalidRequest``, ``LowLevelInternalError`` and
    ``LowLevelServerError``.

    Attributes
    ----------
    reply : Reply
        The Reply object being created when the exception was raised.
    """
    def __init__(self, reply):
        super().__init__(reply, "Terragen RPC low level error.")


class Reply:
    """Data returned by low-level RPC calls, which may include error
    info.

    Raises
    ------
    ReplyError
        Raised if the response from the server cannot be decoded and parsed.
    ApiError (subclass thererof)
        Raised if the reply from the server contains an error code that
        suggests an API mismatch between client and server or an
        incorrect use of the API.
    LowLevelError (subclass thereof)
        Raised if the reply from the server contains an error code that
        suggests a problem with its implementation, or if this module
        encounters an internal error.

    Attributes
    ----------
    ok : bool
        Whether the call was successful.
    value
        If ``ok`` is `True`, ``value`` is the main value of interest, whose type
        depends on the function that was called. Should be equal to
        ``raw_dict['result']``.
    jsonrpc_error_code : int
        An error code returned by the server if the response was parsed.
        It is either the error code returned by the server or -32603 for
        an internal error. It is expected to follow the JSON-RPC 2.0
        specification (https://www.jsonrpc.org/specification).
        Possible values include:
        -32700 (Parse error);
        -32600 (Invalid Request);
        -32601 (Method not found);
        -32602 (Invalid params);
        -32603 (Internal error);
        -32000 to -32099 (Server error).
    jsonrpc_error_msg : str or None
        An error message returned by the server if the response was
        parsed, or 'Internal error' if the response was not parsed,
        or `None` if no error occurred.
        If not `None` it is expected to follow the JSON-RPC 2.0
        specification (https://www.jsonrpc.org/specification).
        Possible values include:
        'Parse error';
        'Invalid Request';
        'Method not found';
        'Invalid params';
        'Internal error';
        'Server error'.
    more_error_info : str or None
        May be a string with more information about an error,
        or may be None.
    raw_bytes : byte array
        The byte array returned by the server, which is expected to
        conform to JSON-RPC 2.0 protocol. Not normally needed, but could
        be useful for debugging.
    raw_dict : dict
        A dictionary representation of the JSON object returned by the
        server. Not normally needed, but could be useful for debugging.
    """
    
    ok = False
    value = None
    raw_bytes = None
    raw_dict = None
    more_error_info = None

    def __init__(self, reply_bytes, method, params):
        self.raw_bytes = reply_bytes
        self._method = method
        self._params = params
        try:
            self.raw_dict = impl.deserialize_reply(reply_bytes)
        except Exception as e:
            self.ok = False
            raise ReplyError(self)
        
        if 'error' in self.raw_dict:

            self.ok = False
            self.error_msg = self.raw_dict['error']['message']

            if 'more_info' in self.raw_dict['error']:
                self.more_error_info = self.raw_dict['error']['more_info'] 

            raise _create_jsonrpc_error(self)

        elif 'result' not in self.raw_dict:

            self.ok = False
            raise ReplyError(self)

        else:

            self.ok = True
            self.value = self.raw_dict['result']
    
    @property
    def jsonrpc_error_code(self):
        if 'error' in self.raw_dict:
            return self.raw_dict['error']['code']
        else:
            return 0

    @property
    def jsonrpc_error_msg(self):
        if 'error' in self.raw_dict:
            return self.raw_dict['error']['message']
        else:
            return None


def settimeout(timeout_in_seconds):
    impl.settimeout(timeout_in_seconds)

def call(method, params = []):
    """Generate an RPC query string, send it to the Terragen RPC server
    and return a `Reply` object.

    Raises
    ------
    ConnectionError
        Raised by socket if a connection error occurs.
    TimeoutError
        Raised by impl.send_string() if a socket timeout occurs.
    ReplyError
        Raised if the response from the server cannot be decoded and
        parsed.
    ApiError (subclass thererof)
        Raised if the reply from the server contains an error code that
        suggests an API mismatch between client and server or an
        incorrect use of the API.
    LowLevelError (subclass thereof)
        Raised if the reply from the server contains an error code that
        suggests a problem with its implementation, or if this module
        encounters an internal error.
    """
    msg = impl.generate_query_string(method, params)
    reply_bytes = impl.send_string(msg)
    return Reply(reply_bytes, method, params)

def call_with_invalid_json():
    """Test the RPC server with deliberately invalid JSON and attempt
    to return a `Reply` object, which should raise an exception.

    Raises
    ------
    ConnectionError
        Raised by socket if a connection error occurs.
    TimeoutError
        Raised by impl.send_string() if a socket timeout occurs.
    ReplyError
        Raised if the response from the server cannot be decoded and
        parsed.
    LowLevelParseError
        Raised if the connection is successful and the server responds
        correctly to unparseable JSON with error code -32700.
    """
    msg = "This is a test of invalid JSON" \
    ", and if the server is compliant it should respond with a JSON-RPC object with error code -32700"
    reply_bytes = impl.send_string(msg)
    return Reply(reply_bytes, None, None)

def call_with_invalid_request():
    """Test the RPC server with a deliberately invalid request and
    attempt to return a `Reply` object, which should raise an exception.

    Raises
    ------
    ConnectionError
        Raised by socket if a connection error occurs.
    TimeoutError
        Raised by impl.send_string() if a socket timeout occurs.
    ReplyError
        Raised if the response from the server cannot be decoded and
        parsed.
    LowLevelInvalidRequest
        Raised if the connection is successful and the server responds
        correctly to an invalid request with error code -32600.
    """
    msg = impl.generate_invalid_query_string("This is a test of an invalid request" \
    ", and if the server is compliant it should respond with a JSON-RPC object with error code -32600")
    reply_bytes = impl.send_string(msg)
    return Reply(reply_bytes, None, None)


# Low Level API/JSON-RPC Errors


class ApiMethodNotFound(ApiError):
    """An exception raised when the server responds with JSON-RPC error code -32601.

    A subclass of ``ApiError``.

    Attributes
    ----------
    reply : Reply
        The Reply object being created when the exception was raised.
    """
    def __init__(self, reply):
        super().__init__(reply)

class ApiInvalidParams(ApiError):
    """An exception raised when the server responds with JSON-RPC error code -32602.

    A subclass of ``ApiError``.

    Attributes
    ----------
    reply : Reply
        The Reply object being created when the exception was raised.
    """
    def __init__(self, reply):
        super().__init__(reply)

class LowLevelParseError(LowLevelError):
    """An exception raised when the server responds with JSON-RPC error code -32700.

    A subclass of ``LowLevelError``.

    Attributes
    ----------
    reply : Reply
        The Reply object being created when the exception was raised.
    """
    def __init__(self, reply):
        super().__init__(reply)

class LowLevelInvalidRequest(LowLevelError):
    """An exception raised when the server responds with JSON-RPC error code -32600.

    A subclass of ``LowLevelError``.

    Attributes
    ----------
    reply : Reply
        The Reply object being created when the exception was raised.
    """
    def __init__(self, reply):
        super().__init__(reply)

class LowLevelInternalError(LowLevelError):
    """A subclass of ``LowLevelError``.

    Attributes
    ----------
    reply : Reply
        The Reply object being created when the exception was raised.
    """
    def __init__(self, reply):
        super().__init__(reply)

class LowLevelServerError(LowLevelError):
    """An exception raised when the server responds with a JSON-RPC error code
    between -32099 and -32000.

    A subclass of ``LowLevelError``.

    Attributes
    ----------
    reply : Reply
        The Reply object being created when the exception was raised.
    """
    def __init__(self, reply):
        super().__init__(reply)


# Error creation help function

def _create_jsonrpc_error(reply):
    code = reply.jsonrpc_error_code
    if code == -32700:
        return LowLevelParseError(reply)
    elif code == -32600:
        return LowLevelInvalidRequest(reply)
    elif code == -32601:
        return ApiMethodNotFound(reply)
    elif code == -32602:
        return ApiInvalidParams(reply)
    elif code == -32603:
        return LowLevelInternalError(reply)
    elif code >= -32099 and code <= -32000:
        return LowLevelServerError(reply)
    else:
        return Error(reply)

