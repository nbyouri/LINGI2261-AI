'''NAMES OF THE AUTHOR(S): Michael Saint-Guillain <michael.sait@uclouvain.be>, Francois Aubry'''

from search import *
from collections import deque
from copy import deepcopy
import time


counter = 0
#################
# Problem class #
#################
class Kubmic(Problem):

    def __eq__(x,y):
        return x.grid == y.grid

    def __hash__(self):
        return hash(str(self.grid))

    def successor(self, state):
        succ = list()
        global counter
        counter += 1
        # Row shifts
        for x in range(0, state.nbr):
            for i in range(1, state.nbc):
                if len(set(state.grid[x])) > 1:
                    if len(state.grid[x]) >= 5 or len(state.grid[x]) == 4 and state.grid[x][:2] != state.grid[x][2:]:
                        grid_copy = state.grid[:]
                        shifted_row = rotate(grid_copy[x], i)
                        grid_copy[x] = shifted_row
                        # append tuple of act?? and the new state
                        succ.append(('move',State(grid_copy, "Row " + str(x + 1) + ": +" + str(i))))

        # Column shifts
        transposed_grid = list(map(list, zip(*state.grid))) # transpose the matrix so that columns are accessible as rows
        for x in range(0, state.nbc):
            for i in range(1, state.nbr):
                if len(set(transposed_grid[x])) > 1:
                    if len(transposed_grid[x]) >= 5 or len(transposed_grid[x]) == 4 and transposed_grid[x][:2] != transposed_grid[x][2:]:
                        transposed_grid_copy = transposed_grid[:]
                        shifted_column = rotate(transposed_grid_copy[x], i)
                        transposed_grid_copy[x] = shifted_column
                        # append tuple of act?? and the new state
                        succ.append(('move',State(list(map(list, zip(*transposed_grid_copy))), "Col " + str(x + 1) + ": +" + str(i))))

        for s in succ:
            yield s

    def predecessor(self, state):
        succ = list()
        global counter
        counter += 1
        # Row shifts
        for x in range(0, state.nbr):
            for i in range(1, state.nbc):
                if len(set(state.grid[x])) > 1:
                    if len(state.grid[x]) >= 5 or len(state.grid[x]) == 4 and state.grid[x][:2] != state.grid[x][2:]:
                        grid_copy = state.grid[:]
                        shifted_row = rotate(grid_copy[x], i)
                        grid_copy[x] = shifted_row
                        # append tuple of act?? and the new state
                        succ.append(('move',State(grid_copy, "Row " + str(x + 1) + ": -" + str(i))))

        # Column shifts
        transposed_grid = list(map(list, zip(*state.grid))) # transpose the matrix so that columns are accessible as rows
        for x in range(0, state.nbc):
            for i in range(1, state.nbr):
                if len(set(transposed_grid[x])) > 1:
                    if len(transposed_grid[x]) >= 5 or len(transposed_grid[x]) == 4 and transposed_grid[x][:2] != transposed_grid[x][2:]:
                        transposed_grid_copy = transposed_grid[:]
                        shifted_column = rotate(transposed_grid_copy[x], i)
                        transposed_grid_copy[x] = shifted_column
                        # append tuple of act?? and the new state
                        succ.append(('move',State(list(map(list, zip(*transposed_grid_copy))), "Col " + str(x + 1) + ": -" + str(i))))

        for s in succ:
            yield s

    def goal_test(self, state):
        return state.grid == self.goal.grid

    def check_test(self, node_ext, explored):
        try:
            return (node_ext, explored.pop(tuple(map(tuple, node_ext.state.grid))))
        except KeyError:
            return None


class Node_ext(Node):
    def expand_top(self, problem):
        for (act,next) in problem.successor(self.state):
            yield Node_ext(next, self, act,
                problem.path_cost(self.path_cost, self.state, act, next))
    def expand_bottom(self, problem):
        for (act,next) in problem.predecessor(self.state):
            yield Node_ext(next, self, act,
                problem.path_cost(self.path_cost, self.state, act, next))
    def path_bottom(self):
        "Create a list of nodes from the root to this node."
        x, result = self, [self]
        while x.parent:
            result.append(x.parent)
            x = x.parent
        return result
###############
# State class #
###############

class State:
    def __init__(self, grid, comment = ''):
        self.nbr       = len(grid)
        self.nbc       = len(grid[0])
        self.grid      = grid
        self.comment   = comment

    def __str__(self):
        s = ''
        for i in range(0, self.nbr):
            for j in range(0, self.nbc):
                s = s + str(self.grid[i][j])
            if i < self.nbr - 1:
                s = s + '\n'
        return s

class FIFOQueue_ext(FIFOQueue):
    def peek(self):
        return self.A[self.start]

######################
# Auxiliary function #
######################
def readInstanceFile(filename):
    lines = [ line.rstrip('\n') for line in open(filename) ]
    n = math.floor(len(lines) / 2)
    m = len(lines[0])
    grid_init = [[ lines[i][j] for j in range(0, m)] for i in range(0, n) ]
    grid_goal = [[ lines[i][j] for j in range(0, m)] for i in range(n+1, len(lines)) ]

    return grid_init, grid_goal

########################
# Bidirectional Search #
########################
def bidirectional_add_hashmap(node_ext, explored):
    if not explored.__contains__(tuple(map(tuple, node_ext.state.grid))):
        explored[tuple(map(tuple, node_ext.state.grid))] = node_ext

#def bidirectional_tree_check_depth(problem, explored_top, explored_bottom, fringe_top, fringe_bottom, ret):
#	depth = ret[0].depth + ret[1]
def concat_node(tuple):
    (node_top, node_bottom) = tuple
    path_top = node_top.path()
    path_bottom = node_bottom.path()

    path_top.reverse()
    for n in path_bottom[:-1]:
        n.parent.state.comment = n.state.comment
    return(path_top + path_bottom[1:])
def bidirectional_tree_search(problem, fringe_top, fringe_bottom):

    fringe_top.append(Node_ext(problem.initial))
    fringe_bottom.append(Node_ext(problem.goal))
    explored_top, explored_bottom = dict(), dict()
    ret = None
    depth_top, depth_bottom = 0, 0
    while fringe_top and fringe_bottom:
#		node_ext_top = fringe_top.pop()
#		node_ext_bottom = fringe_bottom.pop()
        while (fringe_top.peek().depth == depth_top):
            node_ext_top = fringe_top.pop()
            ret = problem.check_test(node_ext_top, explored_bottom)
            if ret != None:
                return concat_node(ret)
            bidirectional_add_hashmap(node_ext_top, explored_top)
            fringe_top.extend(node_ext_top.expand_top(problem))
            depth_top = node_ext_top.depth
        depth_top +=1
        while (fringe_bottom.peek().depth == depth_bottom):
            node_ext_bottom = fringe_bottom.pop()
            ret = problem.check_test(node_ext_bottom, explored_top)
            if ret != None:
                return concat_node(reversed(ret))
            bidirectional_add_hashmap(node_ext_bottom, explored_bottom)
            fringe_bottom.extend(node_ext_bottom.expand_bottom(problem))
            depth_bottom = node_ext_bottom.depth
        depth_bottom +=1
    return ret


def bidirectional_breadth_first_tree_search(problem):
    return bidirectional_tree_search(problem, FIFOQueue_ext(), FIFOQueue_ext())

#####################
# Launch the search #
#####################

grid_init, grid_goal = readInstanceFile(sys.argv[1])
init_state = State(grid_init)
goal_state = State(grid_goal)
#print('- Instance: --')
#print(init_state)
#print('')
#print(goal_state)
#print('--------------')

# Row shifting
def rotate(array, n):
    return array[-n:] + array[:-n]


problem = Kubmic(init_state, goal_state)

init_state.comment = "Init"

## Search Algorithm argument
algo = sys.argv[2]
print("Instance " + str(sys.argv[1]) + ", Algorithm: " + str(sys.argv[2]) + "\n")
start_time = time.time()
if algo == "breadth_first_tree_search":
    path = breadth_first_tree_search(problem).path()
    path.reverse()
elif algo == "breadth_first_graph_search":
    path = breadth_first_graph_search(problem).path()
    path.reverse()
elif algo == "depth_first_tree_search":
    path = depth_first_tree_search(problem).path()
    path.reverse()
elif algo == "depth_first_graph_search":
    path = depth_first_graph_search(problem).path()
    path.reverse()
elif algo == "iterative_deepening_search":
    path = iterative_deepening_search(problem).path()
    path.reverse()
else: path = bidirectional_breadth_first_tree_search(problem)
end_time = time.time()


def comments(comm):
    return '\033[1;36;40m' + comm + '\033[0m'

print('Number of moves: ' + str(len(path) - 1))
print("Nodes visited: " + str(counter + 1))
print("Finished in %.2f seconds" % (end_time - start_time))
print("\n\n")
