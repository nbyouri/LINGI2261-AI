from agent import AlphaBetaAgent
import minimax

"""
Agent skeleton. Fill in the gaps.
"""
class MyAgent(AlphaBetaAgent):

    """This is the skeleton of an agent to play the game."""
    
    def get_action(self, state, time_left):
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
        pass

    def cutoff(self, state, depth):
        """The cutoff function returns true if the alpha-beta/minimax
        search has to stop; false otherwise.
        """
        pass

    def evaluate(self, state):
        """The evaluate function must return an integer value
        representing the utility function of the board.
        """
        pass
