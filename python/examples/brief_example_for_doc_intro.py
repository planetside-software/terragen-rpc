import terragen_rpc as tg

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

# Note: Exception handling was omitted from this example for brevity.
# See other examples for exception handling.
