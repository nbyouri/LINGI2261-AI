from agent import AlphaBetaAgent
import minimax
from state_tools_basic import rocks
from constants import *

"""
Agent skeleton. Fill in the gaps.
"""


class MyAgent(AlphaBetaAgent):
    """This is the skeleton of an agent to play the game."""
    move_nbr = 0
    current_depth = 0
    last_action = []

    def revert_previous_action(self, action):
        last_move, move = self.last_action[0], action[0]
        last_cell, cell = self.last_action[1], action[1]

        try:
            last_face, face = self.last_action[2], action[2]
            # Avoid reverting rotation
            if last_move == "face" and move == "face":
                return last_cell != cell or last_face != face
        except IndexError:
            print("Index error")

        # Place and recover
        if last_move == "place" and move == "recover":
            return last_cell != cell
        # Push and recover
        if last_move == "place-push" and move == "recover":
            return last_cell != cell

        return True

    def get_action(self, state, last_action, time_left):
        """This function is used to play a move according
        to the board, player and time left provided as input.
        It must return an action representing the move the player
        will perform.
        """
        self.move_nbr += 1
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
            if state.is_action_valid(action) and self.revert_previous_action(action):
                new_state = state.copy()
                new_state.apply_action(action)
                successors.append((action, new_state))
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
        return self.evaluate_engine(self.id, state) - self.evaluate_engine(self.id - 1, state)

    def evaluate_engine(self, player_id, state):
        """The val function is the sum of (5 - # moves from p in direction f to exit) for each rock
                controlled by player where p,f are the position and the exit direction
                for each rock controlled by player"""
        val = 0
        compact_str = state.compact_str()
        if player_id == 0:
            player = [0, 1, 2, 3]
        else:
            player = [4, 5, 6, 7]

        # TODO Condition only works with depth 1
        if self.move_nbr == 1 and self.current_depth == 1:
            pos = [1, 3, 23, 21]
            for i in pos:
                if compact_str[i] in player:
                    val += 999
        if self.move_nbr == 2 and self.current_depth == 1:
            pos = [1, 3, 23, 21]
            pos_push = [6, 8, 18, 16]
            for i in range(len(pos)):
                if compact_str[pos[i]] in player and compact_str[pos_push[j]] in player:
                    val += 999

        if self.move_nbr == 3 and self.current_depth == 1:
            pos = [10, 14]
            for i in pos:
                if compact_str[i] in player:
                    val += 999

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
                raise ValueError("face= ", f, RIGHT)
            val += SIZE - dst
        return val
