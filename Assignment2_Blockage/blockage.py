'''NAMES OF THE AUTHOR(S): Michael Saint-Guillain <michael.saint@uclouvain.be>'''
import time
import sys
import math
from search import *

#################
# Problem class #
#################
class Blockage(Problem):

    def gravity(self, state, new_grid):
        transposed_grid = list(map(list, zip(*new_grid)))
        blocks = list()
        block_moved = False
        for x,row in enumerate(new_grid):
            for y,item in enumerate(row):
                if item.islower():
                    blocks.append((x,y,item))
        for pos_x,pos_y,block in blocks:
            # Transpose matrix to apply gravity
            gravity_col = transposed_grid[pos_y][:]
            for j in range(pos_x, state.nbr - 1):
                if gravity_col[j + 1] == ' ':
                    gravity_col[j + 1] = block
                    gravity_col[j] = ' '
                    block_moved = True
                else: # stop at '@', '#' or block
                    break
            # If we're on target, change the block to a '@'
            if self.goal.grid[j][pos_y].lower() == block:
                gravity_col[j] = '@'
            transposed_grid[pos_y] = gravity_col
            if block_moved:
                return self.gravity(state, list(map(list, zip(*transposed_grid))))
        return list(map(list, zip(*transposed_grid)))

    def successor(self, state):
        succ = list()
        blocks = list()
        goal_blocks = list()
        # Find blocks
        for x,row in enumerate(state.grid):
            for y,item in enumerate(row):
                if item.islower():
                    blocks.append((x,y,item))
        #Search goal blocks
        for x,row in enumerate(self.goal.grid):
            for y,item in enumerate(row):
                if item.isupper():
                    goal_blocks.append((x,y,item))
        #if self.is_dead(blocks, goal_blocks):
        #    return succ
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
                new_grid[pos_x] = tuple(row)

                # Add a comment
                cost = pos_y - i
                comment = ''.join(['(', str(pos_x), ',', str(pos_y), ') ', 'move to ', 'left' if cost > 0 else 'right'])

                gravity_applied_grid = self.gravity(state, new_grid)
                #print(State(tuple(gravity_applied_grid), comment=comment))
                succ.append(('move', State(tuple(gravity_applied_grid), comment=comment)))

        for s in succ:
            yield s

    def goal_test(self, state):
        # We run A* until targets are attained in goal
        # that is, if there are as many '@' in the current state
        # as there are upper case letters in the goal
        nb_a = 0
        nb_A = 0
        for row in state.grid:
            nb_a += row.count('@')
        for row in self.goal.grid:
            nb_A += sum(1 for c in row if c.isupper())
        return nb_a == nb_A

    def is_dead(self, blocks, goal_blocks):
        ans = False
        for x,y,item in blocks:
            if ans:
                return ans
            for x_g,y_g,item_g in goal_blocks:
                if(item == item_g.lower() and x > x_g): #With x the vertical distance
                    ans = True
                elif(item == item_g.lower() and x <= x_g):
                    ans = False
                    break
        return ans
    #########################################
    # Manhattan distance Heuristic function #
    #########################################
    def manhattan_heuristic(self, n):
        h = 0.0
        blocks = list()
        goal_blocks = list()
        state = n.state
        #Search blocks
        for x,row in enumerate(state.grid):
            for y,item in enumerate(row):
                if item.islower():
                    blocks.append((x,y,item))
        #Search goal blocks
        for x,row in enumerate(self.goal.grid):
            for y,item in enumerate(row):
                if item.isupper():
                    goal_blocks.append((x,y,item))
        for x,y,item in blocks:
            dist = list()
            for x_g,y_g,item_g in goal_blocks:
                if item == item_g.lower():
                    dist.append(math.fabs(y - y_g) + math.fabs(x - x_g)) #Change here to just compare horizontal distance to be optimal
            if dist:
                h += max(dist)
        return h

    def zero_heuristic(self, n):
        h = 0.0
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
        self.dead = False   #Set to True if the game is in a not winnable state

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


#####################
# Launch the search #
#####################
grid_init = readInstanceFile(sys.argv[1])
grid_goal = readInstanceFile(sys.argv[2])

init_state = State(grid_init)
goal_state = State(grid_goal)

problem = Blockage(init_state, goal_state)

#print('Initial grid')
#print(init_state)
#print('------------')
#print('Goal grid')
#print(goal_state)
#print('------------')

init_state.comment = 'Init'

if len(sys.argv) > 3:
    heuristic = sys.argv[3]
    if heuristic == "manhattan":
        h = problem.manhattan_heuristic
    elif heuristic == "zero":
        h = problem.zero_heuristic
    else: h = problem.manhattan_heuristic
else:
    h = problem.manhattan_heuristic

#start = time.time()
node = astar_graph_search(problem, h)
#end = time.time()


if node:
    # Example of print
    path = node.path()
    path.reverse()


#    print('Number of moves: ' + str(node.depth))
    for n in path:
        # print(n.action)		# a comment line
        print(n.state) 		# assuming that the __str__ function of states output the correct format
        print()

    #if len(sys.argv) > 3:
    #    print('A* with the %s heuristic took %.2f seconds' % (sys.argv[3], end - start))
else:
    print("No solution found")
