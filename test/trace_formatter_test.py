from gcc_log_pharser._internal.trace_formatter import *
from gcc_log_pharser._internal.types import *


def _one_layer_test(layer, test_childrens):
    for child in test_childrens:
        if child not in layer.children:
            return False

    return True


def _convert_to_tree_test():
    leaf_1 = Leaf()
    leaf_1.phases = {'template instantiation': 9.0, 'deferred': 10.0}
    leaf_1.wall_total = 1

    leaf_2 = Leaf()
    leaf_2.phases = {'template instantiation': 100, 'deferred': 5.0}
    leaf_2.wall_total = 4

    units = {'evo_motion_control/CMakeFiles/motion_control.dir/src/utils.cpp.o': leaf_1,
             'evo_motion_control/motion_control/CMakeFiles/motion_control.dir'
             '/src/torque_controllers/auto_controller/transmission_smooth_start.cpp.o': leaf_1,
             'evo_motion_control/motion_control/CMakeFiles/motion_control.dir'
             '/src/torque_controllers/joy_controller/joy_torque_controller.cpp.o': leaf_2,
             'evo_motion_control/motion_control/CMakeFiles/motion_control.dir'
             '/src/torque_controllers/auto_controller/adaptive_controller.cpp.o': leaf_2,
             'evo_motion_control/motion_control/CMakeFiles/motion_control.dir'
             '/src/motion_control_sources_manager.cpp.o': leaf_2}

    tree_units = _convert_flat_data_to_tree(units)

    if tree_units.name != 'TU':
        return False

    if 'evo_motion_control' not in tree_units.children:
        return False

    if not _one_layer_test(tree_units.children['evo_motion_control'], ['src', 'motion_control']):
        return False

    if not _one_layer_test(tree_units.children['evo_motion_control'].children['motion_control'].children['src'],
                           ['torque_controllers', 'motion_control_sources_manager.cpp.o']):
        return False

    return True


def _gen_standard_tree():
    leaf_1 = Leaf('leaf_1')
    leaf_1.total = 5
    leaf_1.phases = {'a': 'b', 'c': 'd'}

    leaf_2 = Leaf('leaf_2')
    leaf_2.total = 3

    leaf_3 = Leaf('leaf_3')
    leaf_3.total = 1

    leaf_4 = Leaf('leaf_4')
    leaf_4.total = 10
    leaf_4.phases = {'sd': 'fk', 'n1': 'bd'}

    node_1 = Node('node_1')
    node_2 = Node('node_2')
    node_3 = Node('node_3')

    node_1.children = {'node_2': node_2, 'node_3': node_3}
    node_2.children = {'leaf_1': leaf_1, 'leaf_2': leaf_2}
    node_3.children = {'leaf_3': leaf_3, 'leaf_4': leaf_4}

    return node_1


def _calculate_time_test():
    standard_tree = _gen_standard_tree()

    _calculate_time(standard_tree)

    if standard_tree.start_time != 0 or standard_tree.end_time != 19:
        return False

    if standard_tree.children['node_2'].start_time != 0 or standard_tree.children['node_2'].end_time != 8:
        return False

    if standard_tree.children['node_3'].start_time != 8 or standard_tree.children['node_3'].end_time != 19:
        return False

    return True


def _convert_json_trace_test():
    standard_tree = _gen_standard_tree()
    _calculate_time(standard_tree)
    json_events = _get_json_trace(standard_tree)['traceEvents']

    test_event_list = [{'name': 'node_1', 'cat': 'COMPILING', 'ph': 'B', 'ts': 0, 'pid': 0, 'tid': 0},
                       {'name': 'node_1', 'cat': 'COMPILING', 'ph': 'E', 'ts': 19000, 'pid': 0, 'tid': 0},
                       {'name': 'node_2', 'cat': 'COMPILING', 'ph': 'B', 'ts': 0, 'pid': 0, 'tid': 0},
                       {'name': 'node_2', 'cat': 'COMPILING', 'ph': 'E', 'ts': 8000, 'pid': 0, 'tid': 0},
                       {'name': 'leaf_1', 'cat': 'COMPILING', 'ph': 'B', 'ts': 0, 'pid': 0, 'tid': 0,
                        'args': {'a': 'b', 'c': 'd'}},
                       {'name': 'leaf_1', 'cat': 'COMPILING', 'ph': 'E', 'ts': 5000, 'pid': 0, 'tid': 0,
                        'args': {'a': 'b', 'c': 'd'}},
                       {'name': 'leaf_2', 'cat': 'COMPILING', 'ph': 'B', 'ts': 5000, 'pid': 0, 'tid': 0, 'args': {}},
                       {'name': 'leaf_2', 'cat': 'COMPILING', 'ph': 'E', 'ts': 8000, 'pid': 0, 'tid': 0, 'args': {}},
                       {'name': 'node_3', 'cat': 'COMPILING', 'ph': 'B', 'ts': 8000, 'pid': 0, 'tid': 0},
                       {'name': 'node_3', 'cat': 'COMPILING', 'ph': 'E', 'ts': 19000, 'pid': 0, 'tid': 0},
                       {'name': 'leaf_3', 'cat': 'COMPILING', 'ph': 'B', 'ts': 8000, 'pid': 0, 'tid': 0, 'args': {}},
                       {'name': 'leaf_3', 'cat': 'COMPILING', 'ph': 'E', 'ts': 9000, 'pid': 0, 'tid': 0, 'args': {}},
                       {'name': 'leaf_4', 'cat': 'COMPILING', 'ph': 'B', 'ts': 9000, 'pid': 0, 'tid': 0,
                        'args': {'sd': 'fk', 'n1': 'bd'}},
                       {'name': 'leaf_4', 'cat': 'COMPILING', 'ph': 'E', 'ts': 19000, 'pid': 0, 'tid': 0,
                        'args': {'sd': 'fk', 'n1': 'bd'}}]

    return json_events == test_event_list


def test_():
    if not _convert_to_tree_test():
        print("Incorrect tree conversion")
    if not _calculate_time_test():
        print("Incorrect time calculating")
    if not _convert_json_trace_test():
        print('Incorrect json conversion')


if __name__ == '__main__':
    test_()

