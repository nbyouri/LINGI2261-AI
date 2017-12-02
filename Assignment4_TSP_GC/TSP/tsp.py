#! /usr/bin/env python3
################################################################################
#
# Implementation of the TSP problem class
#
################################################################################
from search import *
import sys


#################
# Problem class #
#################
class TSP(Problem):

    """TSP skeleton. Fill in the gaps."""
    def __init__(self, instance):
        # Read data
        lines = [line.rstrip('\n') for line in open(instance)]
        self.n = int(lines[0])
        self.cities = []
        for i in range(1, self.n + 1):
            part = lines[i].split()
            self.cities.append((float(part[0]), float(part[1])))

        def dist(city1, city2):
            return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)

        # Compute distance matrix
        self.dist = []
        for i in range(self.n):
            dist_ = []
            for j in range(self.n):
                dist_.append(dist(self.cities[i], self.cities[j]))
            self.dist.append(dist_)

        # Greedy initial solution
        cur_city = 0
        self.initial = [0]
        while len(self.initial) < self.n:
            cost = min(x for i, x in enumerate(self.dist[cur_city]) if i not in self.initial)
            cur_city = self.dist[cur_city].index(cost)
            self.initial.append(cur_city)

    def successor(self, state):
        """
        For successor(self, state) function, you should return a list of (act, succ) 
        where the state succ is obtained by apply the action act, in this case, act = (i, j) 
        consists in applying 2-opt swap on the two edges (state[i-1], state[i]) and  (state[j], state[j+1]). 
        (state here is an ordered sequence of visited cities)

        For example, consider the following state:
        state = [7, 2, 1, 5, 4, 3, 0, 6]
        One possible successor of this state could be ((1,5), succ), with:
        succ = [7, 3, 4, 5, 1, 2, 0, 6]
        Since act = (1, 5), it means that the two edges (7, 2) and (3,0) have been swapped in succ. 
        You should try to visualize this example, it will be more easier to see.
        You should reverse path between index i and index j to preserve other edges.
        """
        succ = []
        for i in range(len(state)):
            for j in range(i + 1, len(state)):
                r = list(reversed(state[i:j+1]))
                succ.append(((i, j), state[:i] + r + state[j+1:]))
        for s in succ:
            yield s

    def value(self, state):
        """
        The value function must return an integer value
        representing the length of TSP route.
        """
        val = 0
        for i in range(len(state) - 1):
            val += self.dist[state[i]][state[i + 1]]
        val += self.dist[state[0]][state[-1]]
        return val

#################
# Local Search #
#################


def maxvalue(problem, limit=100, callback=None):
    current = LSNode(problem, problem.initial, 0)

    for step in range(limit):
        if callback is not None:
            callback(current)
        successors = current.expand()
        current = min(successors, key=lambda x: x.problem.value(x.state))
    return current


def randomized_maxvalue(problem, limit=100, callback=None):
    # use this line to submit on INGInious
    # random.seed(12)
    current = LSNode(problem, problem.initial, 0)
    best = current
    # Put your code here!


    return best


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], "tsp_instance", file=sys.stderr)
        exit(1)

    tsp = TSP(sys.argv[1])
    node = maxvalue(tsp, 100)

    # prepare output data to printout
    print('Initial')
    output_data = '%.2f' % tsp.value(tsp.initial) + '\n'
    output_data += ' '.join(map(str, tsp.initial)) + '\n'
    print(output_data)

    print('maxvalue')
    output_data = "%.2f" % node.value() + '\n'
    output_data += ' '.join(map(str, node.state)) + '\n'
    print(output_data)

    # random walk
    print('Random Walk')
    node = random_walk(tsp, 100)
    output_data = '%.2f' % node.value() + '\n'
    output_data += ' '.join(map(str, node.state)) + '\n'
    print(output_data)

    # simulated annealing
    print('Simulated Annealing')
    node = simulated_annealing(tsp)
    output_data = '%.2f' % node.value() + '\n'
    output_data += ' '.join(map(str, node.state)) + '\n'
    print(output_data)
