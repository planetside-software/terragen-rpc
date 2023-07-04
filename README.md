# Terragen RPC

Terragen RPC is a remote procedure call system for certain versions of Terragen by Planetside Software. A running instance of Terragen can act as a server, allowing other programs to make remote procedure calls (RPCs) to query the open project and modify its state.

## Install for Python

```python -m pip install terragen-rpc```

## Example usage (.py)

```python
import terragen_rpc as tg

# Print the nodes at the top level of the project

project = tg.root()
children = project.children()
for c in children:
    print(c.path())

# Print the parameters of a node whose path is "/Render Camera"

camera = tg.node_by_path('/Render Camera')
if camera:
    print(camera.param_names())
else:
    print("Node not found")

# Note: Exception handling was ommitted from this example for brevity.
# See other examples for exception handling.
```

## Documentation

Complete documentation may be found here: https://planetside.co.uk/docs/terragen-rpc/
