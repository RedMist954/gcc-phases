import re
from enum import Enum
import json

from .types import Leaf, Node


class EncodeStudent(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


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
    print(json.dumps(_get_json_trace(tree_units), cls=EncodeStudent))
