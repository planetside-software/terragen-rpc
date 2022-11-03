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


"""Unit tests. To test, run pytest from a shell
"""

import sys
import os

# Set unittest_dir
this_file_path = os.path.realpath(__file__)
this_dir = os.path.dirname(this_file_path)
unittest_dir = this_dir

# Add the parent directory to sys.path
parent_dir = os.path.dirname(unittest_dir)
sys.path.append(parent_dir)
  
# Now we can import the module in the parent directory
import terragen_rpc as tg


# Test Low Level API

def test_lowlevel_call_invalid_json():

    caught = False
    try:
        tg.jsonrpc.call_with_invalid_json()
    except tg.jsonrpc.LowLevelParseError as e:
        caught = True
        assert issubclass(type(e), tg.jsonrpc.LowLevelError)  # because it's documented as such
        assert e.reply.jsonrpc_error_code == -32700
        assert e.reply.jsonrpc_error_msg == 'Parse error'

    assert caught

def test_lowlevel_call_invalid_request():
    
    caught = False
    try:
        tg.jsonrpc.call_with_invalid_request()
    except tg.jsonrpc.LowLevelInvalidRequest as e:
        caught = True
        assert issubclass(type(e), tg.jsonrpc.LowLevelError)  # because it's documented as such
        assert e.reply.jsonrpc_error_code == -32600
        assert e.reply.jsonrpc_error_msg == 'Invalid Request'

    assert caught

def test_lowlevel_call_nonexistent_method():
    
    caught = False
    try:
        tg.jsonrpc.call('nonexistent_method')
    except tg.jsonrpc.ApiMethodNotFound as e:
        caught = True
        assert issubclass(type(e), tg.jsonrpc.ApiError)  # because it's documented as such
        assert e.reply.jsonrpc_error_code == -32601
        assert e.reply.jsonrpc_error_msg == 'Method not found'

    assert caught
    
def test_lowlevel_call_invalid_params():

    def assert_invalid_params(e):
        assert issubclass(type(e), tg.jsonrpc.ApiError)  # because it's documented as such
        assert e.reply.jsonrpc_error_code == -32602
        assert e.reply.jsonrpc_error_msg == 'Invalid params'


    try:
        root = tg.jsonrpc.call('root').value
    except:
        assert False, "Couldn't complete test because it requires 'root' to be an available RPC method"

    try:
        tg.jsonrpc.call('name', [root])
    except:
        assert False, "Couldn't complete test because it requires 'name' to be an available RPC method"

    try:
        tg.jsonrpc.call('get_param_as_string', [root, 'name'])
    except:
        assert False, "Couldn't complete test because it requires 'get_param_as_string' to be an available RPC method"


    #Test 1 param when 0 are expected
    caught = False
    try:
        tg.jsonrpc.call('root', ['bad_param'])
    except tg.jsonrpc.ApiInvalidParams as e:
        caught = True
        assert_invalid_params(e)
    assert caught

    #Test 0 params when 1 is expected
    caught = False
    try:
        tg.jsonrpc.call('name')
    except tg.jsonrpc.ApiInvalidParams as e:
        caught = True
        assert_invalid_params(e)
    assert caught

    #Test 2 params when 1 is expected
    caught = False
    try:
        tg.jsonrpc.call('name', [root, 'bad_param'])
    except tg.jsonrpc.ApiInvalidParams as e:
        caught = True
        assert_invalid_params(e)
    assert caught

    #Test 0 params when 2 are expected
    caught = False
    try:
        tg.jsonrpc.call('get_param_as_string')
    except tg.jsonrpc.ApiInvalidParams as e:
        caught = True
        assert_invalid_params(e)
    assert caught

    #Test 1 param when 2 are expected
    caught = False
    try:
        tg.jsonrpc.call('get_param_as_string', [root])
    except tg.jsonrpc.ApiInvalidParams as e:
        caught = True
        assert_invalid_params(e)
    assert caught


# Test High Level API

def test_project_filepath():

    v = tg.project_filepath()
    assert v != None

def test_root():

    v = tg.root()
    assert v != None
    assert v != ""
    assert v != 0
    
def test_parent_of_camera_equals_root():

    camera = tg.node_by_path('/Render Camera')
    
    v = tg.parent(camera)
    assert v == camera.parent() # equivalence of member function and free function

    assert v != None
    assert v != ""
    assert v != 0

    parent = v

    v = tg.root()
    assert v != None
    assert v != ""
    assert v != 0

    root = v

    assert parent == root

def test_children_of_root_is_a_list():

    root = tg.root()
    v = tg.children(root)
    assert type(v) is list
    assert v == root.children() # equivalence of member function and free function

def test_children_filtered_by_class_camera_is_a_list():

    root = tg.root()
    v = tg.children_filtered_by_class(root, 'camera')
    assert type(v) is list
    assert v == root.children_filtered_by_class('camera') # equivalence of member function and free function

def test_children_filtered_by_class_camera_is_a_list_of_size_1():

    root = tg.root()
    v = tg.children_filtered_by_class(root, 'camera')
    assert type(v) is list
    assert len(v) == 1
    assert v == root.children_filtered_by_class('camera') # equivalence of member function and free function

def test_children_filtered_by_class_camera_contains_render_camera():

    root = tg.root()
    v = tg.children_filtered_by_class(root, 'camera')

    # Raises `StopIteration` if no item satysfing the condition is found.
    next(i for i in v if i.path() == '/Render Camera')

    assert v == root.children_filtered_by_class('camera') # equivalence of member function and free function

def test_param_names_of_root_is_a_list():

    root = tg.root()
    v = tg.param_names(root)
    assert type(v) is list
    assert v == root.param_names() # equivalence of member function and free function

def test_param_names_of_camera_is_a_list():

    node = tg.node_by_path('/Render Camera')

    v = tg.param_names(node)
    assert type(v) is list
    assert v == node.param_names() # equivalence of member function and free function

def test_node_by_path():

    v = tg.node_by_path('/Render Camera')
    assert v != None
    assert v != ""
    assert v != 0

def test_create_image_map_shader():

    class_name = 'image_map_shader'

    root = tg.root()

    # First, count how many nodes of this class there are.
    nodes = tg.children_filtered_by_class(root, class_name)
    original_count = len(nodes)

    # Create a new node
    v = tg.create_child(root, class_name)

    # Test the return value
    assert v

    # Test to see if the node was created
    nodes = tg.children_filtered_by_class(root, class_name)
    new_count = len(nodes)
    assert new_count == original_count + 1

    # Test that the ID returned by create_child() exists
    # in the IDs returned by children_filtered_by_class
    assert v in nodes
    
def test_create_bad_class_does_nothing_and_returns_none():

    root = tg.root()

    # First, count how many nodes there are.
    nodes = tg.children(root)
    original_count = len(nodes)

    # Attempt to create a new node with a bad class name.
    # We expect this to fail.
    v = tg.create_child(root, 'a_class_that_should_not_exist')

    # Test the return value. We expect this to be None.
    assert v == None

    # Test to make sure no nodes were created.
    nodes = tg.children(root)
    new_count = len(nodes)
    assert new_count == original_count

def test_delete_water_group():

    v = tg.node_by_path('/Water')
    assert v != None
    assert v != ""
    assert v != 0

    node = v

    tg.delete(node)

    assert tg.node_by_path('/Water') == None
    
def test_delete_three_terrain_nodes():

    node_paths = []
    node_paths.append('/Fractal warp shader 01')
    node_paths.append('/Fractal terrain 01')
    node_paths.append('/Simple shape shader 01')

    # Find nodes and test that they exist
    nodes = []
    for p in node_paths:
        v = tg.node_by_path(p)
        assert v != None
        assert v != ""
        assert v != 0
        nodes.append(v)

    # Delete nodes
    tg.delete(nodes)

    # Test that they no longer exist
    for p in node_paths:
        assert tg.node_by_path(p) == None

def test_name():
    
    node = tg.node_by_path('/Render Camera')
    v = tg.name(node)
    assert v == 'Render Camera'
    assert v == node.name() # equivalence of member function and free function
    
def test_path():

    node = tg.node_by_path('/Render Camera')
    v = tg.path(node)
    assert v == '/Render Camera'
    assert v == node.path() # equivalence of member function and free function

def test_get_param_as_string():

    node = tg.node_by_path('Render Camera')
    v = tg.get_param_as_string(node, 'position')
    assert v == node.get_param_as_string('position') # equivalence of member function and free function

    assert v == '0 10 -30'
    
def test_get_param_as_int():

    node = tg.node_by_path('Render Camera')
    v = node.get_param_as_int('perspective')

    assert type(v) is int
    assert v == 1

def test_get_param_as_float():

    node = tg.node_by_path('Render Camera')
    v = node.get_param_as_float('horizontal_fov')

    assert type(v) is float
    assert v >= 30 and v <= 100

def test_get_param_as_tuple():

    node = tg.node_by_path('Render Camera')
    v = node.get_param_as_tuple('position')

    assert type(v) is tuple
    assert v == (0, 10, -30)

def test_get_param_as_list():

    node = tg.node_by_path('Render Camera')
    v = node.get_param_as_list('position')

    assert type(v) is list
    assert v == [0, 10, -30]

def test_set_param_from_string_and_name():

    node = tg.node_by_path('/Render Camera')
    tg.set_param_from_string(node, 'name', 'TEST CAMERA TEST NAME')
    assert tg.name(node) == 'TEST CAMERA TEST NAME'
    node.set_param_from_string('name', 'Render Camera')
    assert node.name() == 'Render Camera'

def test_set_param_with_int():

    node = tg.node_by_path('/Render Camera')
    node.set_param('perspective', int(0))
    assert tg.get_param_as_string(node, 'perspective') == '0'
    node.set_param('perspective', int(1))
    assert node.get_param_as_string('perspective') == '1'

def test_set_param_with_float():

    node = tg.node_by_path('/Render Camera')
    node.set_param('horizontal_fov', 25.5)
    assert tg.get_param_as_string(node, 'horizontal_fov') == '25.5'
    node.set_param('horizontal_fov', 60.0)
    assert node.get_param_as_string('horizontal_fov') == '60'

def test_set_param_with_tuple():

    node = tg.node_by_path('/Render Camera')
    node.set_param('position', (12, 13, 14))
    assert tg.get_param_as_string(node, 'position') == '12 13 14'
    node.set_param('position', (0, 10, -30))
    assert node.get_param_as_string('position') == '0 10 -30'

def test_set_param_with_list():

    node = tg.node_by_path('/Render Camera')
    node.set_param('position', [12, 13, 14])
    assert tg.get_param_as_string(node, 'position') == '12 13 14'
    node.set_param('position', [0, 10, -30])
    assert node.get_param_as_string('position') == '0 10 -30'

def test_current_selection_is_list():

    v = tg.current_selection()
    assert type(v) is list

def test_current_selection_and_select_just_and_select_more_and_select_none():

    envirolight = tg.node_by_path('/Enviro light')
    sunlight = tg.node_by_path('/Sunlight 01')
    camera = tg.node_by_path('/Render Camera')
    renderer = tg.node_by_path('/Render 01')
    assert envirolight
    assert sunlight
    assert camera
    assert renderer
    assert envirolight != sunlight
    assert envirolight != camera
    assert envirolight != renderer
    assert sunlight != camera
    assert sunlight != renderer
    assert camera != renderer

    # Select just camera and test current_selection()
    tg.select_just(camera)
    v = tg.current_selection()
    assert len(v) == 1 and v[0] == camera

    # Select just renderer and test current_selection()
    tg.select_just(renderer)
    v = tg.current_selection()
    assert len(v) == 1 and v[0] == renderer

    # Add camera to selection and test current_selection()
    # Note: we should not have any expectations about the order of the list
    tg.select_more(camera)
    v = tg.current_selection()
    assert (len(v) == 2) and (renderer in v) and (camera in v)

    # Clear selection and test current_selection()
    tg.select_none()
    v = tg.current_selection()
    assert len(v) == 0

    # Select [camera, renderer] in one call to select(),
    # and test current_selection().
    # Note: we should not have any expectations about the order of the list
    tg.select_just([camera, renderer])
    v = tg.current_selection()
    assert (len(v) == 2) and (renderer in v) and (camera in v)

    # Add [envirolight, sunlight] to selection in one call to select_more(),
    # and test current_selection().
    # Note: we should not have any expectations about the order of the list
    tg.select_more([envirolight, sunlight])
    v = tg.current_selection()
    assert (len(v) == 4)
    assert (renderer in v) and (camera in v)
    assert (envirolight in v) and (sunlight in v)

    # Clear selection and test current_selection()
    tg.select_none()
    v = tg.current_selection()
    assert len(v) == 0

def test_new_project():

    #First we have to open a project so we will be able to test
    #whether new_project() causes it to change.

    filename = os.path.join(unittest_dir, 'project_to_test_open_project_1.tgd')
    tg.open_project(filename)
    loaded_filepath = tg.project_filepath()
    assert loaded_filepath != ''
    assert loaded_filepath != None

    #Test new_project()

    tg.new_project()

    #Verify filename is empty

    assert tg.project_filepath() == ''

def test_save_project():

    test_filepath_1 = os.path.join(unittest_dir, 'temp_saved_by_automated_test_1.tgd')
    test_filepath_2 = os.path.join(unittest_dir, 'temp_saved_by_automated_test_2.tgd')

    v = tg.save_project(test_filepath_1)
    assert tg.project_filepath() == test_filepath_1
    assert type(v) is bool
    assert v == True
    
    v = tg.save_project(test_filepath_2)
    assert tg.project_filepath() == test_filepath_2
    assert type(v) is bool
    assert v == True

def test_open_project():

    test_filepath_1 = os.path.join(unittest_dir, 'project_to_test_open_project_1.tgd')
    test_filepath_2 = os.path.join(unittest_dir, 'project_to_test_open_project_2.tgd')

    v = tg.open_project(test_filepath_1)
    assert tg.project_filepath() == test_filepath_1
    assert type(v) is bool
    assert v == True
    
    v = tg.open_project(test_filepath_2)
    assert tg.project_filepath() == test_filepath_2
    assert type(v) is bool
    assert v == True

def test_insert_clip_file():

    test_filepath_1 = os.path.join(unittest_dir, 'clip_to_test_insert_clip_file_1.tgc')
    expected_node_path = '/INSERTED FROM CLIP FILE'

    # Clean up after other tests
    cleanup = tg.node_by_path(expected_node_path)
    if cleanup:
        tg.delete(cleanup)

    # Insert clip file
    v = tg.insert_clip_file(test_filepath_1)
    assert type(v) is bool
    assert v == True

    # Test that the expected node was created
    expected_node = tg.node_by_path(expected_node_path)
    assert expected_node
    assert tg.parent(expected_node) == tg.root()

    # Clean up
    tg.delete(expected_node)

def test_insert_clip_file_after():

    def _insert_after(input_node_path):

        test_filepath_1 = os.path.join(unittest_dir, 'clip_to_test_insert_clip_file_1.tgc')
        expected_node_name = 'INSERTED FROM CLIP FILE'

        input_node = tg.node_by_path(input_node_path)
        assert input_node
        expected_node_path = tg.parent_path(input_node) + '/' + expected_node_name

        # Clean up after other tests
        cleanup = tg.node_by_path(expected_node_path)
        if cleanup:
            tg.delete(cleanup)

        # Insert clip file
        v = tg.insert_clip_file_after(test_filepath_1, input_node)
        assert type(v) is bool
        assert v == True

        # Test that the expected node was created
        expected_node = tg.node_by_path(expected_node_path)
        assert expected_node

        # Test that it's in the right place
        assert tg.get_param_as_string(expected_node, 'input_node') == input_node_path
        # Test that it has the right parent
        assert tg.parent(expected_node) == tg.parent(input_node)

        # Clean up
        tg.delete(expected_node)

    _insert_after('/Fractal terrain 01')
    _insert_after('/Background/Background shader')

def test_insert_clip_file_before():

    def _insert_before(output_node_path, output_param):

        test_filepath_1 = os.path.join(unittest_dir, 'clip_to_test_insert_clip_file_1.tgc')
        expected_node_name = 'INSERTED FROM CLIP FILE'

        output_node = tg.node_by_path(output_node_path)
        assert output_node
        expected_node_path = tg.parent_path(output_node) + '/' + expected_node_name

        # Clean up after other tests
        cleanup = tg.node_by_path(expected_node_path)
        if cleanup:
            tg.delete(cleanup)

        # Insert clip file
        v = tg.insert_clip_file_before(test_filepath_1, output_node, output_param)
        assert type(v) is bool
        assert v == True

        # Test that the expected node was created
        expected_node = tg.node_by_path(expected_node_path)
        assert expected_node

        # Test that it's in the right place
        assert tg.get_param_as_string(output_node, output_param) == expected_node_path
        # Test that it has the right parent
        assert tg.parent(expected_node) == tg.parent(output_node)

        # Clean up
        tg.delete(expected_node)

    _insert_before('/Fractal terrain 01', 'blending_shader')
    _insert_before('/Background/Background shader', 'input_node')

def test_insert_clip_file_before_with_bad_node():

    test_filepath_1 = os.path.join(unittest_dir, 'clip_to_test_insert_clip_file_1.tgc')
    expected_node_path = '/INSERTED FROM CLIP FILE'

    # Clean up after other tests
    cleanup = tg.node_by_path(expected_node_path)
    if cleanup:
        tg.delete(cleanup)

    # Insert clip file with bad params
    output_node = tg.Node('0')
    output_param = 'blending_shader'
    v = tg.insert_clip_file_before(test_filepath_1, output_node, output_param)
    assert type(v) is bool
    # Assert that bad params caused return value == False
    assert v == False

    # Test that the expected node was NOT created
    expected_node = tg.node_by_path(expected_node_path)
    assert expected_node == None

    # Clean up
    if expected_node:
        tg.delete(expected_node)

def test_insert_clip_file_before_with_bad_link():

    test_filepath_1 = os.path.join(unittest_dir, 'clip_to_test_insert_clip_file_1.tgc')
    expected_node_path = '/INSERTED FROM CLIP FILE'

    # Clean up after other tests
    cleanup = tg.node_by_path(expected_node_path)
    if cleanup:
        tg.delete(cleanup)

    # Insert clip file with bad params
    output_node = tg.node_by_path('/Fractal terrain 01')
    assert output_node
    output_param = 'SHOULD_NOT_EXIST'
    v = tg.insert_clip_file_before(test_filepath_1, output_node, output_param)
    assert type(v) is bool
    # Assert that bad params caused return value == False
    assert v == False

    # Test that the expected node was NOT created
    expected_node = tg.node_by_path(expected_node_path)
    assert expected_node == None

    # Clean up
    if expected_node:
        tg.delete(expected_node)
