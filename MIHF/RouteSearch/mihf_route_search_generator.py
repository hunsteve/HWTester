#!/usr/bin/python/
import math
import random
from solution import solve
import json
# psarkozy@mit.bme.hu

class Node:
    def __init__(self, id=0, location=(0, 0)):
        self.id = id
        self.location = location

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def get_distance(self, other_node):
        return math.sqrt(
            (self.location[0] - other_node.location[0]) ** 2 + (self.location[1] - other_node.location[1]) ** 2)

    def __str__(self):
        return "%d\t%d" % (self.location[0], self.location[1])


class Edge:
    def __init__(self, node_1, node_2):
        self.node_1 = node_1
        self.node_2 = node_2

    def __eq__(self, other):
        return (self.node_1 == other.node_1 and self.node_2 == other.node_2) or \
               (self.node_2 == other.node_1 and self.node_1 == other.node_2)

    def __hash__(self):
        smaller_id = min(self.node_1.id, self.node_2.id)
        larger_id = max(self.node_1.id, self.node_2.id)
        return larger_id * 10000 + smaller_id

    def __str__(self):
        return "%d\t%d" % (self.node_1.id, self.node_2.id)


class NodeGroup:
    def __init__(self, first_node_id=0, node_count=1, location=(0, 0), max_distance=500,
                 extra_edges=0):
        self.first_node_id = first_node_id
        self.node_count = node_count
        self.nodes = []
        current_node_id = self.first_node_id
        for i in xrange(self.node_count):
            location_x = random.randint(location[0] - max_distance, location[0] + max_distance)
            location_y = random.randint(location[1] - max_distance, location[1] + max_distance)
            self.nodes.append(Node(current_node_id, (location_x, location_y)))
            current_node_id += 1
        self.internal_edges = []
        self.create_internal_edges(extra_edges)

    def create_internal_edges(self, extra_edges=0):
        added_edges = [self.nodes[0]]
        for node in self.nodes[1:]:
            pair = random.choice(added_edges)
            self.internal_edges.append(Edge(node, pair))
            added_edges.append(node)

        extra_edges_created = 0
        while extra_edges_created < extra_edges:
            node_1 = random.choice(self.nodes)
            node_2 = random.choice(self.nodes)
            new_edge = Edge(node_1, node_2)
            if new_edge not in self.internal_edges and node_1 != node_2:
                self.internal_edges.append(new_edge)
                extra_edges_created += 1

    def create_intergroup_edges(self, other_group, edge_count=1):
        intergroup_edges = []

        while len(intergroup_edges) < edge_count:

            node_1 = random.choice(self.nodes)
            node_2 = random.choice(other_group.nodes)
            new_edge = Edge(node_1, node_2)
            if new_edge not in intergroup_edges:
                intergroup_edges.append(new_edge)

        return intergroup_edges

    def get_paths(self, other_group, counts):
        paths = []

        while len(paths) < counts:
            node_1 = random.choice(self.nodes)
            node_2 = random.choice(other_group.nodes)

            if node_1 != node_2 and (node_1, node_2) not in paths and (node_2, node_1) not in paths:
                if random.randint(0, 1) == 0:
                    paths.append((node_1, node_2))
                else:
                    paths.append((node_2, node_1))

        return paths


def createInput(groups, interconnects, path_categories):
    interconnect_edges = []
    for interconnect in interconnects:
        interconnect_edges.extend(
            groups[interconnect["group_1"]].create_intergroup_edges(groups[interconnect["group_2"]],
                                                                    interconnect["edge_count"]))

    node_count = 0
    edge_count = 0
    for group in groups:
        node_count += group.node_count
        edge_count += len(group.internal_edges)

    edge_count += len(interconnect_edges)

    paths_to_search = []
    for path_category in path_categories:
        paths_to_search.extend(
            groups[path_category["group_1"]].get_paths(groups[path_category["group_2"]], path_category["path_count"]))

    all_edges = []
    all_nodes = []
    for group in groups:
        all_edges.extend(group.internal_edges)
        all_nodes.extend((group.nodes))
    all_edges.extend(interconnect_edges)

    paths_string = '\n'.join(["%d\t%d" % (node_1.id, node_2.id) for (node_1, node_2) in paths_to_search])
    edges_string = '\n'.join([str(edge) for edge in all_edges])
    nodes_string = '\n'.join([str(node) for node in all_nodes])
    return '%d\n%d\n%d\n\n%s\n\n%s\n\n%s' % (
        len(paths_to_search), node_count, edge_count, paths_string, nodes_string, edges_string)


if __name__ == "__main__":
    json_output = []
    # assigment_1
    # simple 2 group problem
    groups = [NodeGroup(0, 8, (0, 0), 100, 10), NodeGroup(8, 8, (200, 0), 100, 10)]
    interconnects = [{"group_1": 0, "group_2": 1, "edge_count": 5}]
    paths = [{"group_1": 0, "group_2": 1, "path_count": 5}]
    input = createInput(groups, interconnects, paths)
    with open("test.txt", "w") as file:
        file.write(input)

    optimal_distances = solve("test.txt")
    optimal_distances = "\t".join(["%.3f" % (dist) for dist in optimal_distances])
    json_output.append({"input": input, "target": optimal_distances})

    # assigment_2
    # going around problem
    # greedy should fail
    start_group = NodeGroup(0, 60, (0, 0), 100, 20)
    deadend_group_1 = NodeGroup(60, 100, (1000, 0), 100, 10)
    deadend_group_2 = NodeGroup(160, 1000, (1100, -800), 500, 1000)
    detour_group_1 = NodeGroup(1160, 1, (-100, 400), 10, 0)
    detour_group_2 = NodeGroup(1161, 50, (900, 400), 100, 10)
    goal_group = NodeGroup(1211, 50, (1300, 0), 100, 10)
    groups = [start_group, deadend_group_1, deadend_group_2, detour_group_1, detour_group_2, goal_group]
    interconnects = [{"group_1": 0, "group_2": 1, "edge_count": 20},
                     {"group_1": 1, "group_2": 2, "edge_count": 20},
                     {"group_1": 0, "group_2": 3, "edge_count": 1},
                     {"group_1": 3, "group_2": 4, "edge_count": 1},
                     {"group_1": 4, "group_2": 5, "edge_count": 2}]
    paths = [{"group_1": 0, "group_2": 4, "path_count": 60}]
    input = createInput(groups, interconnects, paths)
    with open("greed_test.txt", "w") as file:
        file.write(input)

    optimal_distances = solve("greed_test.txt")
    optimal_distances = "\t".join(["%.3f" % (dist) for dist in optimal_distances])
    json_output.append({"input": input, "target": optimal_distances})

    # assigment_3
    # big big assignment
    # everything but A* should fail
    start_group = NodeGroup(0, 80, (0, 0), 100, 40)
    distaction_group_1 = NodeGroup(80, 800, (0, 400), 200, 500)
    distaction_group_2 = NodeGroup(880, 800, (0, -400), 200, 500)
    halfway_group = NodeGroup(1680, 100, (500, 0), 100, 30)
    goal_group = NodeGroup(1780, 30, (900, 0), 100, 10)
    groups = [start_group, distaction_group_1, distaction_group_2,halfway_group , goal_group]
    interconnects = [{"group_1": 0, "group_2": 1, "edge_count": 5},
                     {"group_1": 0, "group_2": 2, "edge_count": 5},
                     {"group_1": 0, "group_2": 3, "edge_count": 2},
                     {"group_1": 3, "group_2": 4, "edge_count": 10}]
    paths = [{"group_1": 0, "group_2": 4, "path_count": 40}]
    input = createInput(groups, interconnects, paths)
    with open("astar_test.txt", "w") as file:
        file.write(input)

    optimal_distances = solve("astar_test.txt")
    optimal_distances = "\t".join(["%.3f" % (dist) for dist in optimal_distances])
    json_output.append({"input": input, "target": optimal_distances})
    with open("tests.json","w") as file:
        json.dump(json_output,file)
