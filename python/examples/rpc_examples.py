import terragen_rpc as tg
import traceback

try:
    # Print the nodes at the top level of the project

    root = tg.root()
    children = root.children()
    for c in children:
        print(c.path())

    # Print the parameters of a node whose path is "/Render Camera"

    camera = tg.node_by_path('/Render Camera')
    if camera:
        print(camera.param_names())
    else:
        print("Node not found")

except ConnectionError as e:
    # A built-in Python exception raised by the socket.
    # This probably means that Terragen isn't running or
    # there is a misconfiguration in Terragen or this client.
    print("Terragen RPC connection error: " + str(e))
    # Extra handling here...
    # ...

except TimeoutError as e:
    # A built-in Python exception raised either by the socket
    # or by this module when a socket timeout occurs.
    # This could mean that the current instance of Terragen failed
    # to respond or that a previous instance has crashed without
    # properly closing the socket.
    print("Terragen RPC timeout error: " + str(e))
    # Extra handling here...
    # ...

except tg.ReplyError as e:
    # The server responded, but the data it returned could not be parsed.
    print("Terragen RPC server reply error: " + str(e))
    # Extra handling here...
    # ...

except tg.ApiError:
    # The server responded indicating that there was an API misuse. If
    # using the High Level API this probably means the server is running
    # a version of the API that is incompatible with this particular call.
    # Exception subclasses include ApiMethodNotFound and ApiInvalidParams.
    print("Terragen RPC API error")
    # Extra handling here...
    # Let's print something useful for debugging.
    print(traceback.format_exc()) # requires import traceback
    # The program continues running after this.
