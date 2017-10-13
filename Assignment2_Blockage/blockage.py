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
        # Find blocks
        for x in range(1, state.nbr):
            for y in range(1, state.nbc):
                if state.grid[x][y].islower():
                    blocks.append((x,y, state.grid[x][y]))
        # Generate successors for each block
        # Blocks can move left or right and cannot traverse another block (blocks are solid)
        for pos_x,pos_y,block in blocks:
            for i in [pos_y - 1, pos_y + 1]: # iterate over left or right position of the block
                # If the block is on target
                if state.grid[pos_x][i] != ' ':
                    continue

                new_grid = list(state.grid[:])
                row = list(new_grid[pos_x])
                row[i] = block
                row[pos_y] = ' '

                # Add a comment
                cost = pos_y - i
                comment = '(' + str(pos_x) + ',' + str(pos_y) + ') ' + 'move to '
                if cost > 0:
                    comment += 'left'
                else: comment += 'right'

                new_grid[pos_x] = tuple(row)
                # Transpose matrix to apply gravity
                transposed_grid = list(map(list, zip(*new_grid)))
                gravity_col = transposed_grid[i][:]
                for j in range(pos_x, state.nbr - 1):
                    # Fall through ' ', targets until '#' or '@' or block is found
                    # FIXME collisions with other blocks
                    if gravity_col[j + 1] == ' ':
                        gravity_col[j + 1] = block
                        gravity_col[j] = ' '
                    elif gravity_col[j + 1].isupper():
                        gravity_col[j + 1] = block
                        gravity_col[j] = gravity_col[j + 1]
                    else:
                        break
                # If we're on target, change the block to a '@'
                if self.goal.grid[j][i].lower() == block:
                    gravity_col[j] = '@'

                transposed_grid[i] = gravity_col
                gravity_applied_grid = list(map(list, zip(*transposed_grid)))
                succ.append(('move', State(grid=tuple(gravity_applied_grid), comment=comment)))

        for s in succ:
            yield s

    def goal_test(self, state):
        # We run A* until no blocks are not on target
        # FIXME not all blocks have targets, see problem a02
        blocks_remaining = False
        for row in state.grid:
            if any(char.islower() for char in row):
                blocks_remaining = True
        return not blocks_remaining

    #########################################
    # Manhattan distance Heuristic function #
    #########################################
    def heuristic(self, n):
        h = 0.0
        # ...
        # compute an heuristic value
        # ...
        return h

###############
# State class #
###############
class State:
    def __init__(self, grid, data=None, comment = ''):
        self.nbr       = len(grid)
        self.nbc       = len(grid[0])
        self.grid 	   = tuple([ tuple(grid[i]) for i in range(0,self.nbr) ])		# self.grid must be immutable (because of __hash__)
        self.comment   = comment

    def __str__(self):
        s = '' + '\033[1;36;40m' + '\u2193 ' + self.comment + '\033[0m' + '\n'
        #s = ''
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


#
# ######################
# # Heuristic function #
# ######################
# def heuristic(n):
#     h = 0.0
#     # ...
#     # compute an heuristic value
#     # ...
#     return h



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

init_state.comment = 'Init'

node = astar_graph_search(problem, problem.heuristic)

# # Example of print
path = node.path()
path.reverse()


print('Number of moves: ' + str(node.depth))
for n in path:
    # print(n.action)		# a comment line
    print(n.state) 		# assuming that the __str__ function of states output the correct format
    print()
