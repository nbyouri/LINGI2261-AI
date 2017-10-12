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
        succ = list()
        blocks = list()
        # Find blocks FIXME optimize with enumerate
        for x in range(1, len(state.grid)):
            for y in range(1, len(state.grid[x])):
                if state.grid[x][y].islower():
                    blocks.append((x,y, state.grid[x][y]))
                # FIXME check if already in goal position
        # Generate successors for each block
        # Blocks can move left or right and cannot traverse another block (blocks are solid)
        for block in blocks:
            for i in range(block[1] - 1, block[1] + 2):
                if i == block[1] or state.grid[block[0]][i] == '#' or state.grid[block[0]][i].islower():
                    continue
                new_grid = list(state.grid[:])
                row = list(new_grid[block[0]])
                row[i] = block[2]
                # FIXME check whether we're on the goal
                row[block[1]] = ' '
                # Add a comment
                cost = block[1] - i
                comment = '(' + str(block[0]) + ',' + str(block[1]) + ') ' + 'move to '
                if cost > 0:
                    comment += 'left'
                else: comment += 'right'
                # comment += ' (' + block[2] + ')'
                new_grid[block[0]] = tuple(row)
                # Transpose matrix to apply gravity
                transposed_grid = list(map(list, zip(*new_grid)))
                gravity_col = transposed_grid[i][:]
                for j in range(block[0], len(gravity_col) - 1):
                    # FIXME goal blocks are solid too!
                    # Fall until a # or another block is found
                    if gravity_col[j+1] == '#' or gravity_col[j+1].islower(): break
                    elif gravity_col[j + 1] == ' ':
                        gravity_col[j + 1] = block[2]
                        gravity_col[j] = ' '
                transposed_grid[i] = gravity_col
                gravity_applied_grid = list(map(list, zip(*transposed_grid)))
                succ.append(('move', State(grid=tuple(gravity_applied_grid), comment=comment)))

        for s in succ:
            yield s

    def goal_test(self, state):
        return state.grid == self.goal.grid

###############
# State class #
###############
class State:
    def __init__(self, grid, data=None, comment = ''):
        self.nbr       = len(grid)
        self.nbc       = len(grid[0])
        self.grid 		= tuple([ tuple(grid[i]) for i in range(0,self.nbr) ])		# self.grid must be immutable (because of __hash__)
        self.comment   = comment

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

print('Initial grid')
print(init_state)
print('------------')
print('Goal grid')
print(goal_state)
print('------------')

print('Successors')
for (act,nextS) in problem.successor(init_state):
    print(nextS.comment)
    print(nextS,'\n')
# node = astar_graph_search(problem, heuristic)

# Example of print
# path = node.path()
# path.reverse()
#
# # print('Number of moves: ' + str(node.depth))
# for n in path:
# 	print(n.action)		# a comment line
# 	print(n.state) 		# assuming that the __str__ function of states output the correct format
# 	print()
#

