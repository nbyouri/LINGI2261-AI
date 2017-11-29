from agent import AlphaBetaAgent
import minimax
from state_tools_basic import rocks
from constants import *


class MyAgent(AlphaBetaAgent):
    current_depth = 0
    last_action = None

    def get_name(self):
        return "super_IA_pas_dutout_faite_le_29_novembre"

    def revert_previous_action(self, action):
        if self.last_action:
            last_move, move = self.last_action[0], action[0]
            last_cell, cell = self.last_action[1], action[1]
            try:
                last_face, face = self.last_action[2], action[2]
                # Avoid reverting rotation
                if last_move == "face" and move == "face":
                    return last_cell != cell or last_face != face
            except IndexError or TypeError:
                pass
            # Place and recover
            if last_move == "place" and move == "recover":
                return last_cell != cell
            # Push and recover
            if last_move == "place-push" and move == "recover":
                return last_cell != cell

            return True
        else:
            return True

    """
    " Avoid doing a place on a block we moved out of the border zone, ignore corners "
    """
    def dumb_place(self, action):
        corners = [(0, 0), (0, 4), (4, 0), (4, 4)]

        if not self.last_action:
            return True
        else:
            last_move = self.last_action[0]
            if last_move == "move":
                last_cell_orig = self.last_action[1]
                move = action[0]
                if move == "place" and last_cell_orig not in corners:
                    cell = action[1]
                    return last_cell_orig == cell


    def get_action(self, state, last_action, time_left):
        """This function is used to play a move according
        to the board, player and time left provided as input.
        It must return an action representing the move the player
        will perform.
        """
        " Optimal initial move "
        if state.turn in [0, 1]:
            if state.is_empty((0, 1)):
                return tuple(("place", (0, 1), 0))
            elif state.is_empty((0, 3)):
                return tuple(("place", (0, 3), 0))
            elif state.is_empty((4, 1)):
                return tuple(("place", (4, 1), 0))
            else:
                return tuple(("place", (4, 3), 0))
        self.last_action = last_action
        return minimax.search(state, self)

    def successors(self, state):
        """The successors function must return (or yield) a list of
        pairs (a, s) in which a is the action played to reach the
        state s;
        """
        actions = state.get_current_player_actions()
        successors = list()
        for action in actions:
            if state.is_action_valid(action):  # and self.revert_previous_action(action):
                new_state = state.copy()
                new_state.apply_action(action)
                successors.append((action, new_state))
        " Sort the tree to allow better pruning "
        successors.sort()
        for s in successors:
            yield s

    def cutoff(self, state, depth):
        """The cutoff function returns true if the alpha-beta/mini max
        search has to stop; false otherwise.
        """
        self.current_depth = depth
        return state.game_over() or depth >= 1

    def evaluate(self, state):
        """The evaluate function must return an integer value
        representing the utility function of the board.
        """
        if state.game_over():
            if state.get_winner() == self.id:
                return float("inf")
            else:
                return -1 * float("inf")

        return self.evaluate_engine(self.id, state) - self.evaluate_engine(self.id - 1, state)

    def evaluate_engine(self, player_id, state):
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
