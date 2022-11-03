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


import json
import socket

TCP_IP = 'localhost'
TCP_PORT = 36971
SOCKET_TIMEOUT = 10     # can be set with terragen_rpc.settimeout()

running_id = 1

def settimeout(timeout_in_seconds):
    global SOCKET_TIMEOUT
    SOCKET_TIMEOUT = timeout_in_seconds

def generate_query_string(method, params = []):
    global running_id
    msg = json.dumps(
        {
            'jsonrpc': '2.0',
            'method': method,
            'params': params,
            'id': running_id
        }
    )
    running_id += 1
    return msg

def generate_invalid_query_string(note):
    global running_id
    msg = json.dumps(
        {
            'note': note
        }
    )
    running_id += 1
    return msg

def generate_notification_string(method, params = []):
    return json.dumps(
        {
            'jsonrpc': '2.0',
            'method': method,
            'params': params
        }
    )

def send_bytes_with_length_info(msg_bytes):
    """
    Raises
    ------
    ConnectionError
    TimeoutError
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(SOCKET_TIMEOUT)
    s.connect((TCP_IP, TCP_PORT))
    
    try:
        length = len(msg_bytes)
        length_info = length.to_bytes(4, byteorder='little')
        s.send(length_info)
    
        s.send(msg_bytes)
    
        chunks = []
        chunk = s.recv(1024)
        chunks.append(chunk)
        while chunk:
            chunk = s.recv(1024)
            chunks.append(chunk)
        reply_bytes = b''.join(chunks)

        return reply_bytes

    except socket.timeout as e:
        # Note that socket.timeout is an alias for TimeoutError
        # since Python 3.10, but we catch socket.timeout here
        # and raise TimeoutError in case we're using an older
        # version.
        raise TimeoutError(e) # in case socket.timeout is not an alias for TimeoutError

    finally:
        #s.shutdown(socket.SHUT_RDWR)
        s.close()

def send_string(msg_string):
    """
    Raises
    ------
    ConnectionError
    TimeoutError
    """
    msg_bytes = msg_string.encode()
    return send_bytes_with_length_info(msg_bytes)

def deserialize_reply(reply):
    return json.loads(reply)

