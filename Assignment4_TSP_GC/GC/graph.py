""" Helper module for the graph coloring problem"""


class Graph:
    """
    The Graph class contains following information:

    nb_nodes: number of nodes in the graph
    nb_edges: number of edges in the graph
    adjacent: adjacent list for each node of the graph
    edges: list of all edges in graph

    ATTENTION: index of node start from 1, i.e, if graph has V nodes,
    we will have node 1, ..., V
    """

    def __init__(self, filename):
        self.nb_nodes = 0
        self.nb_edges = 0
        self.adjacent = []
        self.edges = []

        with open(filename) as f:
            for line in f:
                if not line:
                    continue
                tokens = line.split(" ")
                if tokens[0] == 'p':
                    self.nb_nodes = int(tokens[2])
                    self.nb_edges = int(tokens[3])
                    self.adjacent = [[] for node in range(0, self.nb_nodes+1)]
                if tokens[0] == 'e':
                    node1 = int(tokens[1])
                    node2 = int(tokens[2])
                    self.adjacent[node1].append(node2)
                    self.adjacent[node2].append(node1)
                    self.edges.append([node1, node2])

    def __str__(self):
        return "Undirected graph " + str(self.nb_nodes) + " nodes " + str(self.nb_edges) + " edges"
