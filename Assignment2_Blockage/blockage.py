'''NAMES OF THE AUTHOR(S): Michael Saint-Guillain <michael.saint@uclouvain.be>'''
import time
import sys
import math
from search import *

#################  
# Problem class #
#################
class Blockage(Problem):

	def successor(self, state):
		pass

	def goal_test(self, state):
		pass

###############
# State class #
###############
class State:
	def __init__(self, grid, data=None):
		self.nbr       = len(grid)
		self.nbc       = len(grid[0])
		self.grid 		= tuple([ tuple(grid[i]) for i in range(0,self.nbr) ])		# self.grid must be immutable (because of __hash__)


	def __str__(self):
		# s = '' + '\033[1;36;40m' + '\u2193 ' + self.comment + '\033[0m' + '\n'
		s = ''
		for i in range(0, self.nbr):
			for j in range(0, self.nbc):
				s = s + str(self.grid[i][j])
			if i < self.nbr - 1:
				s = s + '\n'
		return s

	def __eq__(self, other_state):
		for i in range(0, self.nbr):
			for j in range(0, self.nbc):
				if self.grid[i][j] != other_state.grid[i][j] : return False
		return True
	def __ne__(self, other):
		return not(self == other)

	# makes a copy of the grid that this state represents
	def copyGrid(self):
		g = [ [ '.' for j in range(0, self.nbc)] for i in range(0, self.nbr) ]
		for i in range(0, self.nbr):
			for j in range(0, self.nbc):
				g[i][j] = self.grid[i][j]
		return g

	def __hash__(self):
		# return hash(tuple([ tuple(self.grid[i]) for i in range(0,len(self.grid)) ]))
		return hash(self.grid)
		

####################### 
# Auxiliary functions #
#######################
def readInstanceFile(filename):
	lines = [ line.rstrip('\n') for line in open(filename) ]
	nlines = len(lines)
	ncols = len(lines[0])
	grid = [[ lines[i][j] for j in range(0, ncols)] for i in range(0, nlines) ]

	return grid



###################### 
# Heuristic function #
######################
def heuristic(n):
	h = 0.0
	# ...
	# compute an heuristic value
	# ...
	return h






#####################
# Launch the search #
#####################
grid_init = readInstanceFile(sys.argv[1])
grid_goal = readInstanceFile(sys.argv[2])

init_state = State(grid_init)
goal_state = State(grid_goal)

problem = Blockage(init_state, goal_state)

node = astar_graph_search(problem, heuristic)

# Example of print
path = node.path()
path.reverse()

# print('Number of moves: ' + str(node.depth))
for n in path:
	print(n.action)		# a comment line
	print(n.state) 		# assuming that the __str__ function of states output the correct format
	print()


