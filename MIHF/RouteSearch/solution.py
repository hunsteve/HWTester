import math
import time

# This class represents a node
class Node:
    # Initialize the class
    def __init__(self, id, location):
        self.id = id
        self.location = location
        self.neighbours = []
        self.parent = None
        self.g = 0  # Distance to start node
        self.h = 0  # Distance to goal node
        self.f = 0  # Total cost

    def add_neighbour(self, node):
        self.neighbours.append(node)

    def set_parent(self,parent):
        self.parent = parent

    # Compare nodes
    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    # Sort nodes
    def __lt__(self, other):
        return self.f < other.f

    # Print node
    def __repr__(self):
        return ('({0})'.format(self.id))

    def get_distance(self, other_node):
        return math.sqrt(
            (self.location[0] - other_node.location[0]) ** 2 + (self.location[1] - other_node.location[1]) ** 2)


# A* search
def astar_search(nodes, start, end):
    # Create lists for open nodes and closed nodes
    open = []
    closed = []
    # Create a start node and an goal node
    start_node = nodes[start]
    goal_node = nodes[end]
    # Add the start node
    open.append(start_node)
    start_node.h = 0
    start_node.g = 0
    start_node.f = 0

    # Loop until the open list is empty
    while len(open) > 0:
        # Sort the open list to get the node with the lowest cost first
        open.sort()
        # Get the node with the lowest cost
        current_node = open.pop(0)
        # Add the current node to the closed list
        closed.append(current_node)

        # Check if we have reached the goal, return the path
        if current_node == goal_node:
            path = []
            while current_node != start_node:
                path.append(current_node)
                current_node = current_node.parent
            # path.append(start)
            # Return reversed path
            return path[::-1]
        # Unzip the current node position
        # Get neighbors
        neighbors = current_node.neighbours
        # Loop neighbors
        for neighbor in neighbors:
            if (neighbor in closed):
                continue

            g = current_node.g + current_node.get_distance(neighbor)
            h = neighbor.get_distance(goal_node)
            f = h + g
            # Check if neighbor is in open list and if it has a lower f value
            if add_to_open(open, neighbor, f) == True:
                # Everything is green, add neighbor to open list
                open.append(neighbor)
                neighbor.parent = current_node
                neighbor.g = g
                neighbor.h = h
                neighbor.f = f
    # Return None, no path is found
    return None


# Check if a neighbor should be added to open list
def add_to_open(open, neighbor, f):
    for node in open:
        if (neighbor == node and f >= node.f):
            return False
    return True

def get_path_distance(path):
    distance = 0
    current_node = path[0]
    for node in path[1:]:
        distance+= current_node.get_distance(node)
        current_node = node
    return distance

# The main entry point for this module
def solve(input_file):
    start_time = time.time()
    fp = open(input_file, 'r')



    path_count = int(fp.readline().strip())
    node_count = int(fp.readline().strip())
    edge_count = int(fp.readline().strip())

    fp.readline()
    paths_to_search = []
    for i in xrange(path_count):
        line = fp.readline().strip().split("\t")
        paths_to_search.append((int(line[0]), int(line[1])))

    fp.readline()
    nodes = []
    for i in xrange(node_count):
        line = fp.readline().strip().split("\t")
        nodes.append(Node(i,(int(line[0]), int(line[1]))))

    fp.readline()
    for i in xrange(edge_count):
        line = fp.readline().strip().split("\t")
        node_1 = nodes[int(line[0])]
        node_2 = nodes[int(line[1])]
        node_1.add_neighbour(node_2)
        node_2.add_neighbour(node_1)

    # Close the file pointer
    fp.close()
    distances = []
    # Find the closest path from start(@) to end($)
    for start,end in paths_to_search:
        path = astar_search(nodes, start, end)
        distance = get_path_distance(path)
        distances.append(distance)
        print path
        print 'Steps to goal: %d, distance:%f' % (len(path), distance)

    print("--- %s seconds ---" % (time.time() - start_time))
    return distances

# Tell python to run main method
if __name__ == "__main__":
    solve("greedy_test.json")
