from agent import AlphaBetaAgent
import minimax
from state_tools_basic import rocks
from constants import*

"""
Agent skeleton. Fill in the gaps.
"""


class MyAgent(AlphaBetaAgent):
    """This is the skeleton of an agent to play the game."""

    def get_action(self, state, last_action, time_left):
        """This function is used to play a move according
        to the board, player and time left provided as input.
        It must return an action representing the move the player
        will perform.
        """
        return minimax.search(state, self)

    def successors(self, state):
        """The successors function must return (or yield) a list of
        pairs (a, s) in which a is the action played to reach the
        state s;
        """
        actions = state.get_current_player_actions()
        successors = list()
        for action in actions:
            if state.is_action_valid(action):
                new_state = state.copy()
                new_state.apply_action(action)
                successors.append((action, new_state))
        for s in successors:
            yield s

    def cutoff(self, state, depth):
        """The cutoff function returns true if the alpha-beta/minimax
        search has to stop; false otherwise.
        """
        # TODO what val for depth ?
        return depth > 1 or state.game_over()

    def evaluate(self, state):
        """The evaluate function must return an integer value
        representing the utility function of the board.
        """
        evaluate = val(state, state.get_cur_player())
        state.go_to_next_player()
        evaluate -= val(state, state.get_cur_player())
        state.go_to_next_player()
        return evaluate


def val(state, player):
    """The val function is the sum of (5 - # moves from p in direction f to exit) for each rock
            controlled by player where p,f are the position and the exit direction
            for each rock controlled by player"""
    val = 0
    controlled_rocks = rocks(state, player)
    for (y, x), f in controlled_rocks:
        if f == UP:
            val += (5 - y + 1)
        elif f == DOWN:
            val += (5 - (5 - y))
        elif f == RIGHT:
            val += (5 - (5 - x))
        elif f == LEFT:
            val += (5 - x + 1)
        else:
            raise ValueError("Wrong value given by rocks: %s", f)
    return val
