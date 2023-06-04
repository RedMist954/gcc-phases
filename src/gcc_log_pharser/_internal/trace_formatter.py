import re
from enum import Enum
import json

from .types import Leaf, Node


def _convert_path_to_list(path):
    path_list = re.sub(r'/CMakeFiles/.*?.dir', '', path).split('/')

    if path_list[-1][-1] != 'o':
        raise RuntimeError('Incorrect end of path')

    return path_list


def _convert_flat_data_to_tree(units: dict) -> Node:
    root = Node('TU')

    for path, unit in units.items():
        current_node = root
        path_list = _convert_path_to_list(path)

        for i in range(len(path_list)):
            path_segment = path_list[i]

            if i == len(path_list) - 1:
                leaf = Leaf(path_segment)
                # leaf.phases = unit.phases
                leaf.total = unit.wall_total

                current_node.children[path_segment] = leaf

            if path_segment in current_node.children:
                current_node = current_node.children[path_segment]
            else:
                current_node.children[path_segment] = Node(path_segment)
                current_node = current_node.children[path_segment]

    return root


def _calculate_time(tree_units, start_time=0):
    tree_units.start_time = start_time
    tree_units.end_time = start_time

    if isinstance(tree_units, Leaf):
        tree_units.end_time += tree_units.total
    else:
        for _, child in tree_units.children.items():
            tree_units.end_time += _calculate_time(child, tree_units.end_time)

    return tree_units.end_time - tree_units.start_time


class EventType(str, Enum):
    START = 'B'
    END = 'E'


def _gen_standard_event(name, type_enet: EventType, time):
    return {'name': name, 'cat': 'COMPILING', 'ph': type_enet.value, 'ts': time * 1000, 'pid': 0, 'tid': 0}


def _get_events_list(tree_units):
    event_list = [_gen_standard_event(tree_units.name, EventType.START, tree_units.start_time, ),
                  _gen_standard_event(tree_units.name, EventType.END, tree_units.end_time)]

    if isinstance(tree_units, Leaf):
        event_list[0]['args'] = tree_units.phases
        event_list[1]['args'] = tree_units.phases
    else:
        for _, child in tree_units.children.items():
            event_list = event_list + _get_events_list(child)

    return event_list


def _get_json_trace(tree_units):
    return {'displayTimeUnit': 'ns', 'traceEvents': _get_events_list(tree_units)}


def print_json(units):
    tree_units = _convert_flat_data_to_tree(units)
    _calculate_time(tree_units)
    print(json.dumps(_get_json_trace(tree_units)))


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
