#!/usr/bin/env python3

import sys
import graph
import gc_sol
import minisat


def default_usage():
    # The first argument must reference a GRAPH file and the second
    # argument must represent K (number of colors)
    print("Usage:", sys.argv[0], "GRAPH_INSTANCE K", file=sys.stderr)
    exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        default_usage()

    # Read instance
    k = int(sys.argv[2])
    g = graph.Graph(sys.argv[1])

    clauses = gc_sol.get_clauses(g, k)
    nb_vars = g.nb_nodes * k

    # print(nb_vars)
    # print(clauses)

    solution = minisat.minisat(nb_vars, clauses)

    # print(solution)

    no_coloring = []
    duplicated_coloring = []
    violated_adjacent = []

    # get coloring from solution
    colors = [-1 for v in range(0, g.nb_nodes + 1)]
    if solution:
        for s in solution:
            node = int((s + k - 1) / k)
            color = s - (node - 1) * k

            if colors[node] == -1:
                colors[node] = color
            else:
                duplicated_coloring.append(node)
        no_coloring = [node for node in range(1, g.nb_nodes+1) if colors[node] == -1]
        for node1 in range(1, g.nb_nodes+1):
            for node2 in g.adjacent[node1]:
                if colors[node1] == colors[node2]:
                    violated_adjacent.append([node1, node2])

        if duplicated_coloring:
            print("FAIL. Some nodes have more than one color.")
            print(duplicated_coloring)
        elif no_coloring:
            print("FAIL. Some nodes have no assigned color.")
            print(no_coloring)
        elif violated_adjacent:
            print("FAIL. Some adjacent nodes have same color.")
            print(violated_adjacent)
        elif not(duplicated_coloring or no_coloring or violated_adjacent):
            print("SOLVED. You found a " + str(k) + "-coloring for this graph with following color for each node:")
            print(colors[1:])
    else:
        print("NO SOLUTION of " + str(k) + "-coloring for this graph")