SIZE = 5

EMPTY   = -1
PLAYER0 = 0
PLAYER1 = 1
ROCK    = 2

UP    = 0
LEFT  = 1
DOWN  = 2
RIGHT = 3

PUSH_PLACE = { }
for i in range(SIZE):
    PUSH_PLACE[(i, -1)] = ((i, 0), RIGHT)
    PUSH_PLACE[(i, SIZE)] = ((i, SIZE - 1), LEFT)
    PUSH_PLACE[(-1, i)] = ((0, i), DOWN)
    PUSH_PLACE[(SIZE, i)] = ((SIZE - 1, i), UP)

OUTSIDE_LIST = [ (i, -1) for i in range(SIZE) ] + [ (i, SIZE) for i in range(SIZE) ] + [ (-1, j) for j in range(SIZE) ] + [ (SIZE, j) for j in range(SIZE) ]
BORDER_LIST = [ (0, j) for j in range(SIZE) ] + [ (SIZE - 1, j) for j in range(SIZE) ] + [ (i, 0) for i in range(1, SIZE - 1) ] + [ (i, SIZE - 1) for i in range(1, SIZE - 1) ]
BORDER = set()
for p in BORDER_LIST:
    BORDER.add(p)
 
FACE     = [UP, LEFT, DOWN, RIGHT]
FACE_STR = ['UP', 'LEFT', 'DOWN', 'RIGHT']
OPPOSITE = [DOWN, RIGHT, UP, LEFT]
DIR   = [(-1, 0), (0, -1), (1, 0), (0, 1)]
OPPOSITE_DIR = [(1, 0), (0, 1), (-1, 0), (0, -1)]

PUSH_CHAR = ['^', '<', 'v', '>']

ASCII = { EMPTY: ' ', PLAYER0: '0', PLAYER1: '1', ROCK: 'R'}

FACE_MARKER = '*'

EMPTY_MASK = 0
PLAYER_MASK = [ [1, 2, 3, 4], [5, 6, 7, 8] ]
ROCK_MASK = 9