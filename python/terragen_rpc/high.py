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


"""

Changes
-------
- 0.9.0:

  - class ``Node`` replaces ``str`` for node IDs.
  - added member functions to Node:
    ``name``, ``path``, ``parent_path``,
    ``parent``, ``children``, ``children_filtered_by_class``,
    ``param_names``, ``get_param_as_string``,
    ``get_param_as_int``, ``get_param_as_float``,
    ``get_param_as_tuple``, ``get_param_as_list``,
    ``set_param``, ``set_param_from_string``.
  - removed free functions:
    ``get_param_as_int``, ``get_param_as_float``,
    ``get_param_as_tuple``, ``get_param_as_list``,
    ``set_param``.
  - deprecated free functions:
    ``name``, ``path``, ``parent_path``,
    ``parent``, ``children``, ``children_filtered_by_class``,
    ``param_names``, ``get_param_as_string``, ``set_param_as_string``,
    ``toggle_enable_node``.

- `0.8.0 <https://planetside.co.uk/docs/terragen-rpc/version/0.8.0/>`_:

  - renamed ``name_and_path`` to ``path``
  - implemented ``parent_path``
  - implemented ``insert_clip_file``
  - implemented ``insert_clip_file_after``
  - implemented ``insert_clip_file_before``
  - implemented ``get_param_as_int``
  - implemented ``get_param_as_float``
  - implemented ``get_param_as_tuple``
  - implemented ``get_param_as_list``
  - implemented ``set_param``
  - ``delete`` accepts a node ID or a list of node IDs
  - The server-side methods 'name_and_path', 'select_one_more' and
    'select_more_as_array' are deprecated, superseded by 'path' and
    'select_more'. This Python module's methods continue to use the
    deprecated server-side methods for compatibility with servers
    0.7.x and 0.8.x.

- `0.7.0 <https://planetside.co.uk/docs/terragen-rpc/version/0.7.0/>`_:

  - Implemented ``current_selection``
  - Implemented ``select_just``
  - Implemented ``select_more``
  - Implemented ``select_none``
  - ``create_child`` returns a node ID or None
  - ``open_project`` returns True or False
  - ``save_project`` returns True or False

- `0.6.0 <https://planetside.co.uk/docs/terragen-rpc/version/0.6.0/>`_:

  - We recommend that you catch TimeoutError.
  - TimeoutError is raised by impl.send_string() if a socket timeout
    occurs. It does this in case the version of Python being used doesn't
    make socket.timeout an alias for TimeoutError.

TODO
----
- Make operations safe on invalid and deleted node ids.
- Perhaps(?) accept nodepaths anywhere a node id is accepted.
- More functions that take lists as parameters, avoiding loops of RPC calls.
- Functions that return more info about node parameters, such as type,
  or compound data including name, type and value.
"""


import terragen_rpc.jsonrpc as jr

from terragen_rpc.jsonrpc import Reply
from terragen_rpc.jsonrpc import Error, ReplyError, ApiError, LowLevelError



def settimeout(timeout_in_seconds):
    jr.settimeout(timeout_in_seconds)


# Internal utility functions

def _convert_value_0_or_empty_to_none(reply):
    mod = reply
    if reply.ok and (reply.value == '0' or reply.value == 0 or reply.value == ''):
        mod.value = None
    return mod

def _node_or_none(id_string):
    if id_string:
        return Node(id_string)
    else:
        return None

def _nodes_from_ids(id_strings):
    return [Node(i) for i in id_strings]



# Public functions:

def project_filepath():
    """Get the file path and filename of the current project.

    Returns
    -------
    str
        A string which is a file path.
    """
    return jr.call('project_filepath').value

def root():
    """Get the root node of the current project.

    Returns
    -------
    Node | None
    """
    reply = jr.call('root')
    return _node_or_none(_convert_value_0_or_empty_to_none(reply).value)

def node_by_path(path):
    """Find a node by its path in the hierarchy.

    Parameters
    ----------
    path : str
        Should begin with a forward slash.
    
    Returns
    -------
    Node | None
        A node ID if it was found, or None if it was not found.
    """
    reply = jr.call('node_by_path', [path])
    return _node_or_none(_convert_value_0_or_empty_to_none(reply).value)

def create_child(of_node, class_name):
    """Attempt to create a node as a child of an existing node.

    Warning
    -------
    If the class is an object file reader (e.g. 'obj_reader' or
    'tgo_reader') a file dialog will appear and execution will be
    blocked until the dialog is closed.
    This will be fixed in the final version.

    When loading a file into a newly created obj_reader, the only way
    to automatically set up shaders is respond to the file dialog at
    creation time. Setting the filename after the node is created will 
    not set up shaders.
    This problem will be fixed in the final version.

    Parameters
    ----------
    of_node : Node
        The ID of an existing node that will contain (be the parent of)
        the new node. To add to the top level of the project, use root().
    class_name : str
        A node class. For example 'group', 'camera',
        'sunlight', 'render', 'obj_reader', 'image_map_shader' etc.
        You can discover the class of a node by looking at the XML used
        to represent the node on the clipboard or in a TGC or TGD file.
        The class is the same as the XML element name.

    Returns
    -------
    Node | None
        The ID of the new node if it was successfully created,
        otherwise None.
    """
    reply = jr.call('create_child', [of_node.id, class_name])
    return _node_or_none(_convert_value_0_or_empty_to_none(reply).value)

def delete(node_or_nodes):
    """Delete node(s).

    Parameters
    ----------
    node_or_nodes : Node | list of Node
    """
    if type(node_or_nodes) is list:
        ids = [node.id for node in node_or_nodes]
        jr.call('delete', [ids])
    else:
        jr.call('delete', [node_or_nodes.id])

def current_selection():
    """Get a list of the nodes that are currently selected in the UI.

    Returns
    -------
    list of Node
        A list of node IDs. The order of the list is undefined. Do not
        expect the order to correspond to the order in which the nodes
        were selected.
    """
    reply = jr.call('current_selection')
    return _nodes_from_ids(reply.value)

def select_just(node_or_nodes):
    """Select node(s) in the UI by path, replacing the initial
    selection state.

    Parameters
    ----------
    node_or_nodes : Node | list of Node
        A node ID or a list of node IDs
    """
    select_none()
    select_more(node_or_nodes)

def select_more(node_or_nodes):
    """Select additional node(s) in the UI by path, adding to the current
    selection state.

    Parameters
    ----------
    node_or_nodes : Node | list of Node
        A node ID or a list of node IDs
    """
    if True:
        # The following works with server versions 0.7.x and 0.8.x,
        # but is deprecated:

        if type(node_or_nodes) is list:
            ids = [node.id for node in node_or_nodes]
            jr.call('select_more_as_array', [ids])
        else:
            jr.call('select_one_more', [node_or_nodes.id])
    else:
        # The following works with server versions 0.8.0+,
        # and we'll start using this soon:

        if type(node_or_nodes) is list:
            ids = [node.id for node in node_or_nodes]
            jr.call('select_more', [ids])
        else:
            jr.call('select_more', [node_or_nodes.id])

def select_none():
    """Clear the node selection state in the UI.
    """
    jr.call('select_none')

def new_project():
    """Close the current project without saving, and start a new project.
        """
    jr.call('new_project')

def open_project(filename):
    """Close the current project without saving, and open a project file.

    Parameters
    ----------
    filename : str
    
    Returns
    -------
    bool
        True if the method succeeds, otherwise False.

    Note
    ----
    Failure to open the project does not raise an exception, because
    success can be determined from the return value. Should we raise
    an exception instead of returning False?
    """
    return jr.call('open_project', [filename]).value

def save_project(filename):
    """Save the project as 'filename'.

    Parameters
    ----------
    filename : str
    
    Returns
    -------
    bool
        True if the method succeeds, otherwise False.

    Note
    ----
    Failure to save the project does not raise an exception, because
    success can be determined from the return value. Should we raise
    an exception instead of returning False?
    """
    return jr.call('save_project', [filename]).value

def insert_clip_file(filename):
    """Load a clip file into the project. This is similar to choosing
    "Insert Clip File..." from the File menu and clicking "Add", not
    "Insert".

    Inserting nodes from a clip file may cause the node selection state
    to change. Typically the new nodes are selected and everything else
    is deselected, but this is at the discretion of the server.

    Parameters
    ----------
    filename : str
    
    Returns
    -------
    bool
        True if the method succeeds, otherwise False.

    Note
    ----
    Failure to open the file does not raise an exception, because
    success can be determined from the return value. Should we raise
    an exception instead of returning False?

    TODO
    ----
    Implement ``auto_connect``, the option of trying to
    auto-connect it into the node graph using metadata in the file
    and/or other heuristics on the server.

    See also
    --------
    ``insert_clip_file_after``, ``insert_clip_file_before``
    """
    return jr.call('insert_clip_file', [filename]).value

def insert_clip_file_after(filename, input_node):
    """Load a clip file into the project, and connect it into the
    node graph so that ``input_node`` will become its main input and the
    inserted nodes will output to whatever downstream connection(s)
    ``input_node`` was previously outputting to.

    - Pre-state: ``input_node`` =>> downstream(s)
    - Post-state: ``input_node`` -> INSERTED_NODES =>> downstream(s)

    This is similar to what happens when the user context-clicks on the
    body of a node and chooses "Insert Clip File..." from the node
    context menu.

    Inserting nodes from a clip file may cause the node selection state
    to change. Typically the new nodes are selected and everything else
    is deselected, but this is at the discretion of the server.

    Parameters
    ----------
    filename : str
    input_node : Node
        The ID of an existing node.
    Returns
    -------
    bool
        True if the method succeeds, otherwise False.
        The method will do nothing but return False if ``input_node``
        is not valid.

    Note
    ----
    Failure to open the file does not raise an exception, because
    success can be determined from the return value. Should we raise
    an exception instead of returning False?

    See also
    --------
    ``insert_clip_file``, ``insert_clip_file_before``
    """
    return jr.call('insert_clip_file_after', [filename, input_node.id]).value

def insert_clip_file_before(filename, output_node, output_param = 'input_node'):
    """Load a clip file into the project, and connect it into the node
    graph so that the inserted nodes will output to
    ``output_param @ output_node``, and whatever node was the
    previous input to ``output_param @ output_node`` will become
    the main input to the inserted nodes.

    - Pre-state: upstream -> ``output_node``
    - Post-state: upstream -> INSERTED_NODES -> ``output_node``

    This is similar to what happens when the user context-clicks on an
    input port of a node and chooses "Insert Clip File..." from the
    connection context menu.

    Inserting nodes from a clip file may cause the node selection state
    to change. Typically the new nodes are selected and everything else
    is deselected, but this is at the discretion of the server.

    Parameters
    ----------
    filename : str
    output_node : Node
        The ID of an existing node.
    output_param : str
        The parameter name for an input port on ``output_node``.
        Defaults to 'input_node' (the node's main input port), but
        can be any parameter of ``output_node`` that is a node link
        parameter.
    
    Returns
    -------
    bool
        True if the method succeeds, otherwise False.
        The method will do nothing but return False if ``output_node``
        is not valid or does not have a port named ``output_param``.

    Note
    ----
    Failure to open the file does not raise an exception, because
    success can be determined from the return value. Should we raise
    an exception instead of returning False?

    See also
    --------
    ``insert_clip_file``, ``insert_clip_file_after``
    """
    return jr.call('insert_clip_file_before', [filename, output_node.id, output_param]).value




class Node:
    """A node ID.
    """
    id = None

    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        return bool(self.id)


    def name(self):
        """Get the name of the node.

        Returns
        -------
        str
            The name of the node.
        """
        return jr.call('name', [self.id]).value

    def path(self):
        """Get the full path in the hierarchy if the node has a parent,
        or just the name of the node if is parentless (e.g. the project root
        node or an out-of-hierarchy node).

        Returns
        -------
        str
            A string which is the full path of the node. If the node has a
            parent, the path starts with a forward slash and ends with the
            name of the node. If the node is has no parent (e.g. it's the
            root node or an out-of-hierarchy node), the path is just the
            name of the node.
        """
        if True:
            # The following works with server versions 0.7.x, 0.8.x and
            # 0.9.x, but is deprecated:
            return jr.call('name_and_path', [self.id]).value
        else:
            # The following works with server versions 0.8.0+,
            # and we'll start using this soon:
            return jr.call('path', [self.id]).value

    def parent_path(self):
        """Get the path of the node's parent in the hierarchy.

        Returns
        -------
        str
            A string which is the path of the node's parent
        """
        return jr.call('parent_path', [self.id]).value

    def parent(self):
        """Get the parent node.

        Returns
        -------
        Node | None
        """
        reply = jr.call('parent', [self.id])
        return _node_or_none(_convert_value_0_or_empty_to_none(reply).value)

    def children(self):
        """Get the children as a list of node IDs.

        Returns
        -------
        list of Node
            A list of IDs of the node's children.
        """
        reply = jr.call('children', [self.id])
        return _nodes_from_ids(reply.value)

    def children_filtered_by_class(self, class_name):
        """Get a list of nodes of a particular class.

        Parameters
        ----------
        class_name : str
            A node class to match. For example 'group', 'camera',
            'sunlight', 'render', 'obj_reader', 'image_map_shader' etc.
            You can discover the class of a node by looking at the XML used
            to represent the node on the clipboard or in a TGC or TGD file.
            The class is the same as the XML element name.
    
        Returns
        -------
        list of Node
            A list of IDs of the node's children that match the class_name.
        """
        reply = jr.call('children_filtered_by_class', [self.id, class_name])
        return _nodes_from_ids(reply.value)
    
    def param_names(self):
        """Get a list of the node's parameters.

        Returns
        -------
        list of str
            A list of names of the node's parameters.
        """
        return jr.call('param_names', [self.id]).value

    def get_param(self, param_name):
        """Get a parameter’s value, which may be a string, number or list of numbers.

        TODO
        ----
        To be implemented. Currently returns the same as ``get_param_as_string``.
        """
        return self.get_param_as_string(param_name)

    def get_param_as_string(self, param_name):
        """Get a string representation of a parameter's current value.

        Parameters
        ----------
        param_name : str
            A parameter name

        Returns
        -------
        str
            A string representation of the parameter value. For 2D vectors,
            3D vectors and colours, the string contains numbers separated
            by spaces without any leading or trailing whitespace.

        TODO
        ----
        What if the param_name is invalid?
        """
        return jr.call('get_param_as_string', [self.id, param_name]).value

    def get_param_as_int(self, param_name):
        """Get a parameter’s value as an integer.

        Parameters
        ----------
        param_name : str
            A parameter name

        Returns
        -------
        int

        TODO
        ----
        What if the param_name is invalid?
        """
        rawstring = self.get_param_as_string(param_name)
        words = rawstring.split()
        if len(words) > 0:
            return int(words[0])
        else:
            return 0

    def get_param_as_float(self, param_name):
        """Get a parameter’s value as a float.

        Parameters
        ----------
        param_name : str
            A parameter name

        Returns
        -------
        float

        TODO
        ----
        What if the param_name is invalid?
        """
        rawstring = self.get_param_as_string(param_name)
        words = rawstring.split()
        if len(words) > 0:
            return float(words[0])
        else:
            return 0.0

    def get_param_as_tuple(self, param_name):
        """Get a parameter’s value as a tuple of 1, 2, or 3 floats.

        Parameters
        ----------
        param_name : str
            A parameter name

        Returns
        -------
        tuple of float
            A tuple of the parameter's component values.

        TODO
        ----
        What if the param_name is invalid?
        """
        rawstring = self.get_param_as_string(param_name)
        words = rawstring.split()
        return tuple(float(w) for w in words)

    def get_param_as_list(self, param_name):
        """Get a parameter’s value as a list of 1, 2, or 3 floats.

        Parameters
        ----------
        param_name : str
            A parameter name

        Returns
        -------
        list of float
            A list of the parameter's component values.

        TODO
        ----
        What if the param_name is invalid?
        """
        rawstring = self.get_param_as_string(param_name)
        words = rawstring.split()
        return [float(w) for w in words]

    def set_param(self, param_name, values):
        """Set a parameter’s value using a string, number, tuple of numbers
        or list of numbers.

        Parameters
        ----------
        param_name : str
            A parameter name
        values : str | number | tuple of numbers | list of numbers
            If the type is tuple or list, it is converted to a string
            representation of the value and ``set_param_from_string`` is
            called. Other types are cast to str using str() and
            ``set_param_from_string`` is called.
        TODO
        ----
        What if the param_name is invalid?
        """
        if type(values) is tuple:
            strings = (str(i) for i in values)
            string = ' '.join(strings)
        elif type(values) is list:
            strings = [str(i) for i in values]
            string = ' '.join(strings)
        else:
            string = str(values)
        self.set_param_from_string(param_name, string)

    def set_param_from_string(self, param_name, value_string):
        """Set a parameter's value using a string representation which
        follows the same rules used by Terragen XML files.

        Parameters
        ----------
        param_name : str
            A parameter name
        value_string : str
            A string representation of the parameter value. For 2D vectors,
            3D vectors and colours, the string must contain numbers
            separated by spaces.

        TODO
        ----
        What if the param_name is invalid?
        """
        jr.call('set_param_from_string', [self.id, param_name, value_string])



# DEPRECATED


def parent(of_node):
    """DEPRECATED. Get the parent node of a node.

    Returns
    -------
    str
        A string which is the path of the node's parent

    See also
    --------
    ``Node.parent``
    """
    return of_node.parent()

def children(of_node):
    """DEPRECATED. Get the children of a node as a list of node IDs.

    Returns
    -------
    list of Node
        A list of IDs of the node's children.

    See also
    --------
    ``Node.children``
    """
    return of_node.children()

def children_filtered_by_class(of_node, class_name):
    """DEPRECATED. Get a list of nodes of a particular class.

    Returns
    -------
    list of Node
        A list of IDs of the node's children that match the class_name.

    See also
    --------
    ``Node.children_filtered_by_class``
    """
    return of_node.children_filtered_by_class(class_name)

def name(of_node):
    """DEPRECATED. Get the name of a node.

    Returns
    -------
    str
        The name of the node.

    See also
    --------
    ``Node.name``
    """
    return of_node.name()

def path(of_node):
    """DEPRECATED. Get the full path in the hierarchy for a node that has a parent,
    or just the name of a node if is parentless (e.g. the project root
    node or an out-of-hierarchy node).

    Returns
    -------
    str
        A string which is the full path of the node. If the node has a
        parent, the path starts with a forward slash and ends with the
        name of the node. If the node is has no parent (e.g. it's the
        root node or an out-of-hierarchy node), the path is just the
        name of the node.

    See also
    --------
    ``Node.path``
    """
    return of_node.path()

def parent_path(of_node):
    """DEPRECATED. Get the path of the node's parent in the hierarchy.

    Returns
    -------
    str
        A string which is the path of the node's parent.

    See also
    --------
    ``Node.parent_path``
    """
    return of_node.parent_path()

def param_names(of_node):
    """DEPRECATED. Get a list of the node's parameters.

    Returns
    -------
    list of str
        A list of names of the node's parameters.

    See also
    --------
    ``Node.param_names``
    """
    return of_node.param_names()

def get_param_as_string(node, param_name):
    """DEPRECATED. Get a string representation of a parameter's current value.

    Returns
    -------
    str
        A string representation of the parameter value. For 2D vectors,
        3D vectors and colours, the string contains numbers separated
        by spaces without any leading or trailing whitespace.

    See also
    --------
    ``Node.get_param_as_string``
    """
    return node.get_param_as_string(param_name)

def set_param_from_string(node, param_name, value_string):
    """DEPRECATED. Set a parameter's value using a string representation which
    follows the same rules used by Terragen XML files.

    Parameters
    ----------
    node : Node
        A node ID
    param_name : str
        A parameter name
    value_string : str
        A string representation of the parameter value. For 2D vectors,
        3D vectors and colours, the string must contain numbers
        separated by spaces.

    See also
    --------
    ``Node.set_param_from_string``
    """
    node.set_param_from_string(param_name, value_string)

def toggle_enable_node(node):
    """DEPRECATED. Toggle the enabled/disabled parameter of a node if it has one.

    Parameters
    ----------
    node : Node
        A node ID

    Note
    ----
    To enable or disable a node whose status you do not know,
    instead of this function use:
    node.set_param_from_string('enable', '1') or
    node.set_param_from_string('enable', '0')
    """
    jr.call('toggle_enable_node', [node.id])
