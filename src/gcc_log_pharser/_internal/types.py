class Leaf:
    def __init__(self, name=''):
        self.name = name
        self.start_time = 0.0
        self.end_time = 0.0
        self.total = 0.0
        self.phases = dict()


class Node:
    def __init__(self, name=''):
        self.name = name
        self.children = dict()
        self.start_time = 0.0
        self.end_time = 0.0


class PhaseStat:
    def __init__(self, seconds, percents):
        self.wall_seconds = seconds
        self.wall_percents = percents


class UnitStat:
    def __init__(self, path):
        self.path = path
        self.phases = dict()
        self.wall_total = None
