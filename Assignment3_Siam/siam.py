from state import State
from constants import *

"""
Representation of actions

- Placing a piece: 
('place', position, orientation)
position: the position where the piece is placed
orientation: orientation of the piece after placement

- Rotating a piece:
('face', position, orientation)
position: the position of the piece that is rotating
orientation: the final orientation of the piece

- Moving a piece:
('move', origin, destination, orientation)
origin: the position of the piece that is moving
destination: the position where the piece will end
orientation: the final orientation of the piece

- Recovering a piece:
('recover', position)
position: the position of the piece that is being recovered

- Pushing a rock:
('push', position)
position: the position of the piece that will push

- Placing with a push:
('push-place', position, orientation)
position: the position where the piece is placed
orientation: the orientation of the piece. this must be consistent with the push action.
             only for a corner there could be more than one possible orientation.
"""


class SiamState(State):

  """
  Create a new state.
  """
  def __init__(self):
    self.nb_rows = 5
    self.nb_cols = 5
    self.reserve = [5, 5]
    self.board = [ [ EMPTY for j in range(self.nb_cols) ] for i in range(self.nb_rows) ]
    self.face  = [ [ EMPTY for j in range(self.nb_cols) ] for i in range(self.nb_rows) ]
    for j in range(1, self.nb_cols - 1):
      self.board[self.nb_rows // 2][j] = ROCK
      self.face[self.nb_rows // 2][j] = EMPTY
    self.winner = None
    self.cur_player = 0
    self.turn = 0
    self.hashcode = self.compute_hash()

  """
  Create a deep copy of the state.
  """ 
  def copy(self):
    state_copy = SiamState()
    for i in range(self.nb_rows):
      for j in range(self.nb_cols):
        state_copy.board[i][j] = self.board[i][j]
        state_copy.face[i][j] = self.face[i][j]
    for i in range(2):
      state_copy.reserve[i] = self.reserve[i]
    state_copy.winner = self.winner
    state_copy.cur_player = self.cur_player
    state_copy.turn = self.turn
    state_copy.hashcode = self.hashcode
    return state_copy    

  """
  Applies a given action to this state. It assumes that the actions is
  valid. This must be checked with is_action_valid.

  go_to_next_player if a flag used for the gui because some
  action are decomposed into several steps. You should not need
  to ever use it.

  PRE: is_action_valid(action) == True
  """
  def apply_action(self, action, go_to_next_player = True):
    if action[0] == 'place':
      self.set(action[1], self.cur_player, action[2])
      self.reserve[self.cur_player] -= 1
    elif action[0] == 'face':
      pos = action[1]
      self.face[pos[0]][pos[1]] = action[2]
    elif action[0] == 'move':
      orig = action[1]
      dest = action[2]
      face = action[3]
      # set the destination
      self.set(dest, self.board[orig[0]][orig[1]], action[3])
      # clear the origin
      self.clear(orig)
    elif action[0] == 'recover':
      orig = action[1]
      self.reserve[self.cur_player] += 1
      self.clear(orig)
    elif action[0] == 'push':
      self.perform_push(action[1], self.face[action[1][0]][action[1][1]])
    elif action[0] == 'place-push':
      self.perform_push(action[1], action[2])
      self.set(action[1], self.cur_player, action[2])
      self.reserve[self.cur_player] -= 1
    if go_to_next_player:
      # set the next player
      self.go_to_next_player()
    self.hashcode = self.compute_hash()  
    self.turn += 1

  """
  Set the current player to be the other player.
  """
  def go_to_next_player(self):
    self.cur_player = 1 - self.cur_player
    
  """
  Get all the actions that the current player can perform.
  """
  def get_current_player_actions(self):
    return self.get_player_actions(self.cur_player)

  """
  Get all the actions that the given player can perform.
  """
  def get_player_actions(self, player):
    actions = [ ]
    # check if the current player has pieces in the reserve
    # if so, add all possible placement actions
    if self.reserve[player] > 0:
      for f in FACE:
        for p in self.get_empty_border_positions():
          # cannot place in the center in the first two turns
          if p[1] != 2 or self.turn >= 2:
            actions.append(('place', p, f))
    # get the position occupied by the current player
    positions = self.get_player_piece_positions(player)
    for orig in positions:
      # add face actions
      for f in FACE:
        if f != self.face[orig[0]][orig[1]]:
          actions.append(('face', orig, f))
      # add movement actions
      for d in DIR:
        dest = (orig[0] + d[0], orig[1] + d[1])
        if self.in_bounds_pos(dest) and self.is_empty(dest):
          # add movement to adjacent position
          for f in FACE:
            actions.append(('move', orig, dest, f))
        elif not self.in_bounds_pos(dest):
          # we can recover this piece into our reserve by exiting the board
          actions.append(('recover', orig))
      # add push actions
      push_ok, _ = self.can_push(orig, self.face[orig[0]][orig[1]])
      if push_ok:
        actions.append(('push', orig))
    # add place-push actions
    for p in BORDER:
      for face in FACE:
        push_ok, _ = self.can_enter_push(p, face)
        if push_ok:
          actions.append(('place-push', p, face))
    return actions

  """
  Perform a push from the given position in a given direction.

  PRE: can_push(position, face) == True
  """
  def perform_push(self, position, face):
    i = position[0]
    j = position[1]
    direction = DIR[face]
    cur = (i + direction[0], j + direction[1])
    tmp_board_1 = self.board[i][j]
    tmp_face_1 = self.face[i][j]
    self.clear((i, j))
    # loop to shift the pieces
    # __>R^>R__    ->    ___>R^R>_
    while self.in_bounds_pos(cur) and tmp_board_1 != EMPTY:
      ii = cur[0]
      jj = cur[1]
      tmp_board_2 = self.board[ii][jj]
      tmp_face_2 = self.face[ii][jj]
      self.set((ii, jj), tmp_board_1, tmp_face_1)
      tmp_board_1 = tmp_board_2
      tmp_face_1 = tmp_face_2
      cur = (cur[0] + direction[0], cur[1] + direction[1])
    # check whether something was pushed out
    if not self.in_bounds_pos(cur) and tmp_board_1 != EMPTY:
      # something was pushed out
      out = tmp_board_1
      if out == ROCK:
        # a rock was pushed out, find who is closest to it
        direction = OPPOSITE_DIR[face]
        cur = (cur[0] + direction[0], cur[1] + direction[1])
        while self.board_value_pos(cur) == ROCK or self.face_value_pos(cur) != face:
          cur = (cur[0] + direction[0], cur[1] + direction[1])
        # set the closest looking at the rock to be the winner
        self.winner = self.board_value_pos(cur)
      else:
        # someone was pushed out
        self.reserve[out] += 1

  """
  Get the value of face[row][col].
  """
  def face_value(self, row, col):
    return self.face[row][col]

  """
  Get the value of face at a given position.
  """
  def face_value_pos(self, pos):
    return self.face[pos[0]][pos[1]]

  """
  Get the value of board[row][col].
  """
  def board_value(self, row, col):
    return self.board[row][col]

  """
  Get the value of board at a given position.
  """
  def board_value_pos(self, pos):
    return self.board[pos[0]][pos[1]]

  """
  Set the value of board and face at a given position.
  """
  def set(self, position, board_value, face_value):
    i = position[0]
    j = position[1]
    self.board[i][j] = board_value
    self.face[i][j] = face_value
  
  """
  Clear a given position of the board.
  """
  def clear(self, position):
    self.set(position, EMPTY, EMPTY)  

  """
  Check if a given position on the board is empty.
  
  PRE: in_bounds(position) == True
  """
  def is_empty(self, position):
    return self.board[position[0]][position[1]] == EMPTY

  """
  Check if a given position is within the bounds of the board.
  """
  def in_bounds_pos(self, position):
    return self.in_bounds(position[0], position[1])

  """
  Check if a (i, j) is within the bounds of the board.
  """
  def in_bounds(self, i, j):
    return 0 <= i and i < self.nb_rows and 0 <= j and j < self.nb_cols


  """
  Get all positions occupied by the given player.
  """
  def get_player_piece_positions(self, player):
    positions = [ ]
    for i in range(self.nb_rows):
      for j in range(self.nb_cols):
        if self.board[i][j] == player:
          positions.append((i, j))
    return positions
    
  """
  Get all empty positions on the border.

  PRE: none
  """
  def get_empty_border_positions(self):
    positions = [ ]
    for position in BORDER_LIST:
      if self.is_empty(position):
        positions.append(position)
    return positions

  """
  Check whether it is possible to move from a given position.
  """
  def can_move(self, position):
    i = position[0]
    j = position[1]
    if self.board[i][j] == EMPTY or self.board[i][j] == ROCK:
      return False
    desti = i + DIR[self.face[i][j]][0]
    destj = j + DIR[self.face[i][j]][1]
    if not self.in_bounds(desti, destj):
      # collect
      return True
    return self.board[desti][destj] == EMPTY
  
  """
  Get where the piece will end if moved from the given position

  PRE: self.can_move(position) = True
  """
  def get_move_dest(self, position):
    i = position[0]
    j = position[1]
    desti = i + DIR[self.face[i][j]][0]
    destj = j + DIR[self.face[i][j]][1]
    return (desti, destj)

  """
  Check whether a piece at a given positing facing a given direction
  could push something. Note that it does not requite the position
  to have someone so it can be used to check for potential push 
  positions (check can_enter_push for an example).
  """
  def can_push(self, position, face):
    face_count = 1
    oposing_count = 0
    rock_count = 0
    i = position[0] + DIR[face][0]
    j = position[1] + DIR[face][1]
    if not self.in_bounds(i, j) or self.board[i][j] == EMPTY:
      # there is nothing to push
      return False, -1
    while self.in_bounds(i, j) and not self.board[i][j] == EMPTY:
      if self.board[i][j] == ROCK:
        rock_count += 1
      elif self.face[i][j] == OPPOSITE[face]:
        oposing_count += 1
      elif self.face[i][j] == face:
        face_count += 1
      # check if we are already blocked
      delta = face_count - oposing_count
      if delta == 0 or delta < rock_count:
        return False, -1
      i += DIR[face][0]
      j += DIR[face][1]
    return True, rock_count

  """
  Check whether ('place-push', position, face) is a valid action.
  """
  def can_enter_push(self, position, face):
    i = position[0]
    j = position[1]
    if self.reserve[self.cur_player] == 0 or not self.in_bounds(i, j) or self.board[i][j] == EMPTY:
      return False, -1
    if face == UP:
      if i != self.nb_rows - 1:
        return False, -1
      return self.can_push((i + 1, j), UP)
    elif face == DOWN:
      if i != 0:
        return False, -1
      return self.can_push((i - 1, j), DOWN)
    elif face == RIGHT:
      if j != 0:
        return False, -1
      return self.can_push((i, j - 1), RIGHT)
    elif face == LEFT:
      if j != self.nb_cols - 1:
        return False, -1
      return self.can_push((i, j + 1), LEFT)
    return False, -1
    

  """
  Return true if and only if the game is over.
  """
  def game_over(self):
    return self.winner != None

  """
  Return the id of the current player.
  """
  def get_cur_player(self):
    return self.cur_player


  """
  Get the winner of the game.
  """
  def get_winner(self):
    return self.winner

  """
  Get a one line string representation of the state with 25 characters.

  - means empty space
  # means rock
  0 means rhino face up
  1 means rhino face left
  2 means rhino face down
  3 means rhino face right
  4 means elephant face up
  5 means elephant face left
  6 means elephant face down
  7 means elephant face right

  Example:

  initial state is: "-----------###-----------"

  """
  def compact_str(self):
    s = ''
    for i in range(self.nb_rows):
      for j in range(self.nb_rows):
        if self.board[i][j] == EMPTY:
          s += '-'
        elif self.board[i][j] == ROCK:
          s += '#'
        elif self.board[i][j] == PLAYER0:
          s += str(self.face[i][j])
        elif self.board[i][j] == PLAYER1:
          s += str(self.face[i][j]) + 4
        else:
          assert False
    return s

  """
  Compute a hash for the state. The hash is computed so that
  it has a unique value for each state. 
  
  You don't need to understand this so solve the problem but some
  students might want to used it.

  Note that since the state space is laege, this does not means 
  that it will avoid collisions in a hashtable (because the values are compressed).

  The hash uses 4 bits per cell in the board and is similar to the
  compact string representation.

  - -> 0000
  # -> 0001
  0 -> 0010
  1 -> 0011
  2 -> 0100
  3 -> 0101
  4 -> 0110
  5 -> 0111
  6 -> 1000
  7 -> 1001

  """
  def compute_hash(self):
    h = 0
    k = 0
    for i in range(self.nb_rows):
      for j in range(self.nb_cols):
        if self.board[i][j] == EMPTY:
          h = h | (EMPTY_MASK << k)
        elif self.board[i][j] == ROCK:
          h = h | (ROCK_MASK << k)
        else:
          h = h | (PLAYER_MASK[self.board[i][j]][self.face[i][j]] << k)
        k += 5
    return h

  """
  Return the hash of this state.
  """
  def __hash__(self):
    return self.hashcode
  
  """
  Return whether this state equal other.
  Since the hash is unique we can simple compare it.
  """
  def __eq__(self, other):
    if other == None: return False
    return self.hashcode == other.hashcode

  def get_scores(self):
    scores = [0, 0]
    if not self.game_over():
      return scores
    scores[self.winner] += 1
    return scores

  """
  Create a string representation of the state.
  """
  def __str__(self):
    # build a matrix representing the board
    n = 4 * self.nb_rows + 1
    m = 4 * self.nb_cols + 1
    S = [ [ ' ' for j in range(m) ] for i in range(n) ]
    for i in range(n):
      for j in range(m):
        if i % 4 == 0:
          if j % 4 == 0:
            S[i][j] = '+'
          else:
            S[i][j] = '-'
        elif j % 4 == 0:
          S[i][j] = '|'
    for i in range(self.nb_rows):
      for j in range(self.nb_cols):
        S[4 * i + 2][4 * j + 2] = ASCII[self.board[i][j]]
        if self.face[i][j] != EMPTY and self.board[i][j] != ROCK:
          d = DIR[self.face[i][j]]
          S[4 * i + 2 + d[0]][4 * j + 2 + d[1]] = FACE_MARKER
    # convert the matrix into a string
    s = ''
    s += 'cur player: {0}\n'.format(self.cur_player)
    s += 'reserve player 0: {0}\n'.format(self.reserve[0])
    s += 'reserve player 1: {0}\n'.format(self.reserve[1])
    for i in range(n):
      for j in range(m):
        s += S[i][j]
      s += '\n'
    s += str(self.hashcode)
    return s
