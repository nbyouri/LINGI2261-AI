from agent import AlphaBetaAgent
import minimax
# from state_tools_basic import rocks
from constants import *
from siam import *
import db

class MyAgent(AlphaBetaAgent):
    hit = 0.0
    rate = 0.0
    def get_name(self):
        return "super_IA_pas_dutout_faite_le_29_novembre"

    def revert_previous_action(self, state, action):
        last_action = state.last_action[self.id]
        if last_action:
            last_move, move = last_action[0], action[0]
            last_cell, cell = last_action[1], action[1]
            try:
                last_face, face = last_action[2], action[2]
                # Avoid reverting rotation
                if last_move == "face" and move == "face":
                    return last_cell != cell or last_face != face
            except IndexError or TypeError:
                pass
            # Place and recover
            if last_move == "place" and move == "recover":
                return last_cell == cell
            # Push and recover
            if last_move == "place-push" and move == "recover":
                return last_cell == cell
        return False

    """
    Avoid doing a place on a block we moved out of the border zone, ignore corners
    """

    def dumb_place(self, state, action):
        corners = [(0, 0), (0, 4), (4, 0), (4, 4)]
        last_action = state.last_action[self.id]

        if not last_action:
            return False
        else:
            last_move = last_action[0]
            if last_move == "move":
                last_cell_orig = last_action[1]
                move = action[0]
                if move == "place" and last_cell_orig not in corners:
                    cell = action[1]
                    return last_cell_orig == cell
            return False

    """
    Avoid moving into a position where you can't push
    """

    def powerless_push(self, state, action):
        move = action[0]
        weight = 0
        if move == "move":
            cell_i, cell_j, face = action[2][0], action[2][1], action[3]
            " Do we need to look vertically or horizontally "
            if face == LEFT:
                for row_index in range(0, cell_j):
                    ptype = state.board_value_pos((cell_i, row_index))
                    face = state.face[cell_i][row_index]
                    if ptype == ROCK:
                        weight += 1
                    elif ptype != ROCK and face == RIGHT:
                        weight += 2
                    elif ptype != ROCK and face == LEFT:
                        weight -= 2
            elif face == RIGHT:
                for row_index in range(cell_j, 4):
                    ptype = state.board_value_pos((cell_i, row_index))
                    face = state.face[cell_i][row_index]
                    if ptype == ROCK:
                        weight += 1
                    elif ptype != ROCK and face == LEFT:
                        weight += 2
                    elif ptype != ROCK and face == RIGHT:
                        weight -= 2
            elif face == DOWN:
                for col_index in range(cell_i, 4):
                    ptype = state.board_value_pos((col_index, cell_j))
                    face = state.face[col_index][cell_j]
                    if ptype == ROCK:
                        weight += 1
                    elif ptype != ROCK and face == UP:
                        weight += 2
                    elif ptype != ROCK and face == DOWN:
                        weight -= 2
            elif face == UP:
                for col_index in range(0, cell_i):
                    ptype = state.board_value_pos((col_index, cell_j))
                    face = state.face[col_index][cell_j]
                    if ptype == ROCK:
                        weight += 1
                    elif ptype != ROCK and face == DOWN:
                        weight += 2
                    elif ptype != ROCK and face == UP:
                        weight -= 2
        return weight > 0

    def get_action(self, state, last_action, time_left):
        """This function is used to play a move according
        to the board, player and time left provided as input.
        It must return an action representing the move the player
        will perform.
        """
        " Optimal initial move "
        # optimal_initial_positions = [(0, 1), (0, 3), (4, 1), (4, 3)]
        # optimal_tertiary_positions = [(2, 0), (2, 4)]
        # if state.turn in [0, 1]:
        #     for pos in optimal_initial_positions:
        #         if state.is_empty(pos):
        #             return tuple(("place", pos, DOWN if pos[0] == 0 else UP))
        #
        # " Optimal secondary move "
        # if state.turn in [2, 3]:
        #     for pos in optimal_initial_positions:
        #         if state.board_value_pos(pos) == self.id:
        #             return tuple(("place-push", pos, DOWN if pos[0] == 0 else UP))
        #
        # " Optimal tertiary move "
        # if state.turn in [4, 5]:
        #     for i, j in optimal_initial_positions:
        #         if state.board_value_pos((i, j)) == self.id:
        #             if j == 1 and state.is_empty(optimal_tertiary_positions[0]):
        #                 return tuple(("place", optimal_tertiary_positions[0], RIGHT))
        #             elif state.is_empty(optimal_tertiary_positions[1]):
        #                 return tuple(("place", optimal_tertiary_positions[1], LEFT))

        return minimax.search(state, self)

    def successors(self, state):
        """The successors function must return (or yield) a list of
        pairs (a, s) in which a is the action played to reach the
        state s;
        """

        state = ContestSiamState(state)
        actions = state.get_current_player_actions()
        successors = list()
        for action in actions:
            if state.is_action_valid(action) and not self.revert_previous_action(state, action) \
                    and not self.dumb_place(state, action) \
                    and not self.powerless_push(state, action):
                new_state = state.copy()
                new_state.apply_action(action)
                if new_state.compact_str() in db.database:
                    successors.append((action, new_state))
        " Sort the tree to allow better pruning "
        successors = sorted(successors, key=self.cmp_successors)
        for s in sorted(successors, reverse=True, key=self.cmp_successors):
            yield s

    def cmp_successors(self, elem):
        elem = elem
        return self.evaluate(elem[1])

    def cutoff(self, state, depth):
        """The cutoff function returns true if the alpha-beta/mini max
        search has to stop; false otherwise.
        """
        return state.game_over() or depth >= 2

    def evaluate(self, state):
        """The evaluate function must return an integer value
        representing the utility function of the board.
        """
        if state.game_over():
            if state.get_winner() == self.id:
                return float("inf")
            else:
                return -1 * float("inf")
        eval = self.evaluate_db(state)
        if eval:
            return eval

        return self.evaluate_rocks(self.id, state) - self.evaluate_rocks(self.id - 1, state) + self.evaluate_token_nbr(state)

    def evaluate_db(self, state):
        compact_str = state.compact_str()

        if db.database.__contains__(compact_str):
            if self.id == 0:
                return db.database[compact_str][0] / db.database[compact_str][1]
            elif self.id == 1:
                return -1*db.database[compact_str][0] / db.database[compact_str][1]
        else:
            return None


    def evaluate_token_nbr(self, state):
        if not state.reserve[self.id] == 0:
            return 2
        return 0



    def evaluate_rocks(self, player_id, state):
        """The val function is the sum of (5 - # moves from p in direction f to exit) for each rock
                controlled by player where p,f are the position and the exit direction
                for each rock controlled by player"""
        val = 0
        # TODO
        # compact_str = state.compact_str()
        # if player_id == 0:
        #     player = [0, 1, 2, 3]
        # else:
        #     player = [4, 5, 6, 7]
        #
        # if self.move_nbr == 1:  # + self.current_depth == 2:
        #     pos = [1, 3, 23, 21]
        #     for i in pos:
        #         if compact_str[i] in player:
        #             val += 999
        # if self.move_nbr == 2:  # + self.current_depth == 3:
        #     pos = [1, 3, 23, 21]
        #     pos_push = [6, 8, 18, 16]
        #     for i in range(len(pos)):
        #         if compact_str[pos[i]] in player and compact_str[pos_push[i]] in player:
        #             val += 999
        #
        # if self.move_nbr == 3:  # + self.current_depth == 4:
        #     pos = [10, 14]
        #     for i in pos:
        #         if compact_str[i] in player:
        #             val += 999

        controlled_rocks = rocks(state, player_id)
        for (x, y), f in controlled_rocks:
            if f == 0:
                dst = x + 1
            elif f == 1:
                dst = y + 1
            elif f == 2:
                dst = SIZE - x
            elif f == 3:
                dst = SIZE - y
            else:
                raise ValueError("face= ", f)
            val += SIZE - dst
        return val


"""
    Implementation of siam state
"""


class ContestSiamState(SiamState):
    def __init__(self, state):
        self.nb_rows = state.nb_rows
        self.nb_cols = state.nb_cols
        self.reserve = state.reserve
        self.board = state.board
        self.face = state.face
        self.winner = state.winner
        self.cur_player = state.cur_player
        self.turn = state.turn
        self.hashcode = state.hashcode
        self.last_action = [None, None]

    def apply_action(self, action, go_to_next_player=True):
        self.last_action[self.cur_player] = action
        super().apply_action()


from siam import *

"""
A player is said to control a push or place-push if he is the closest
facing the rock (in other words, if the rock went out of the board that
player would win the game).

Given a state and a player compute, for each push or place-push action
controlled by that player, distance between those rocks and the board
of the game.
"""


def rocks(state, player):
    rocks = []
    push_value = 0
    # get the player action
    actions = state.get_player_actions(player)
    # loop to find push or place-push actions
    for action in actions:
        if action[0] == 'push' or action[0] == 'place-push':
            # push or place-push found
            # get the position
            position = action[1]
            # get the face
            face = state.face_value_pos(position)
            if action[0] == 'place-push':
                # for a place-push the face is given in the action
                face = action[2]
            direction = DIR[face]
            # initialize the position of the last rock found
            last_rock = None
            # initialize the player closest to the rock
            last_piece_facing_rock = player
            while state.in_bounds_pos(position) and state.board_value_pos(position) != EMPTY:
                board_value = state.board_value_pos(position)
                if board_value == ROCK:
                    # we found a rock
                    last_rock = position
                elif state.face_value_pos(position) == face:
                    # we found a piece facing the rock
                    last_piece_facing_rock = board_value
                position = (position[0] + direction[0], position[1] + direction[1])
            if last_rock != None and last_piece_facing_rock == player:
                # we found a rock and player if the closest facing the rock
                # compute the distance between the rock and the distance
                rocks.append((last_rock, face))
    return rocks


"""
Database of 18 games of siam
"""

