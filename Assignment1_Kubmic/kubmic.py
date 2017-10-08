'''NAMES OF THE AUTHOR(S): Michael Saint-Guillain <michael.sait@uclouvain.be>, Francois Aubry'''

from search import *
from collections import deque
from copy import deepcopy
import time

#################
# Problem class #
#################
class Kubmic(Problem):
	def successor(self, state):
		succ = list()

		# Row shifts
		for x in range(0, state.nbr):
			for i in range(1, state.nbc):
				grid_copy = state.grid[:]
				shifted_row = rotate(grid_copy[x], i)
				grid_copy[x] = shifted_row
				# append tuple of act?? and the new state
				succ.append(('move',State(grid_copy, "Row " + str(x + 1) + ": +" + str(i))))

		# Column shifts
		transposed_grid = list(map(list, zip(*state.grid))) # transpose the matrix so that columns are accessible as rows
		for x in range(0, state.nbc):
			for i in range(1, state.nbr):
				transposed_grid_copy = transposed_grid[:]
				shifted_column = rotate(transposed_grid_copy[x], i)
				transposed_grid_copy[x] = shifted_column
				# append tuple of act?? and the new state
				succ.append(('move',State(list(map(list, zip(*transposed_grid_copy))), "Col " + str(x + 1) + ": +" + str(i))))

		for s in succ:
			yield s

	def predecessor(self, state):
		succ = list()

		# Row shifts
		for x in range(0, state.nbr):
			for i in range(1, state.nbc):
				grid_copy = state.grid[:]
				shifted_row = rotate(grid_copy[x], i)
				grid_copy[x] = shifted_row
				# append tuple of act?? and the new state
				succ.append(('move',State(grid_copy, "Row " + str(x + 1) + ": -" + str(i))))

		# Column shifts
		transposed_grid = list(map(list, zip(*state.grid))) # transpose the matrix so that columns are accessible as rows
		for x in range(0, state.nbc):
			for i in range(1, state.nbr):
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

def bidirectional_tree_search(problem, fringe_top, fringe_bottom):

	fringe_top.append(Node_ext(problem.initial))
	fringe_bottom.append(Node_ext(problem.goal))
	explored_top, explored_bottom = dict(), dict()
	while fringe_top and fringe_bottom:
		node_ext_top = fringe_top.pop()
		node_ext_bottom = fringe_bottom.pop()

		ret = problem.check_test(node_ext_top, explored_bottom)
		if ret != None:
			return ret
		ret = problem.check_test(node_ext_bottom, explored_top)
		if ret != None:
			return reversed(ret)
		if not explored_top.__contains__(tuple(map(tuple, node_ext_top.state.grid))):
			explored_top[tuple(map(tuple, node_ext_top.state.grid))] = node_ext_top
		if not explored_bottom.__contains__(tuple(map(tuple, node_ext_bottom.state.grid))):
			explored_bottom[tuple(map(tuple, node_ext_bottom.state.grid))] =  node_ext_bottom
		fringe_top.extend(node_ext_top.expand_top(problem))
		fringe_bottom.extend(node_ext_bottom.expand_bottom(problem))
	return None


def bidirectional_breadth_first_tree_search(problem):
	return bidirectional_tree_search(problem, FIFOQueue(), FIFOQueue())

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
# nbel = 0
# print("\nHORIZ\n")
# for (act,node) in problem.successor(init_state):
# 	if nbel == 12:
# 		print("\nVERT\n")
# 	print(node,'\n')
# 	nbel += 1
#
# print(nbel)
# print(init_state)
#start_time = time.time()
#node = iterative_deepening_search(problem)
#node = breadth_first_tree_search(problem)
(node_ext_top, node_ext_bottom) = bidirectional_breadth_first_tree_search(problem)
#end_time = time.time()

path = node_ext_top.path()
path.reverse()

def comments(comm):
	return '\033[1;36;40m' + comm + '\033[0m'

#print('Number of moves: ' + str(node.depth))
for n in path:
	print(comments('\u2193 ' + n.state.comment))	# assuming the comment attribute of state contains a relevant string (e.g. describing the current move)
	print(n.state,'\n') #assuming that the __str__ function of state outputs the correct format

path = node_ext_bottom.path()

for n in path[:-1]:
	print(comments('\u2193 ' + n.state.comment))	# assuming the comment attribute of state contains a relevant string (e.g. describing the current move)
	print(n.parent.state,'\n') #assuming that the __str__ function of state outputs the correct format

#print("Took %.2f seconds" % (end_time - start_time))
