import terragen_rpc as tg

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
    print("Terragen RPC connection error: " + str(e))

except TimeoutError as e:
    print("Terragen RPC timeout error: " + str(e))

except tg.ReplyError as e:
    print("Terragen RPC server reply error: " + str(e))

except tg.ApiError:
    print("Terragen RPC API error")
    raise
