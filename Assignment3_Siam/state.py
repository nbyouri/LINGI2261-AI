
class State():

    """
    Return true if and only if the game is over.
    """
    def game_over(self):
        abstract

    """
    Return the index of the current player.
    """
    def get_cur_player(self):
        abstract

    """
    Checks if a given action is valid.
    """
    def is_action_valid(self, action):
      actions = self.get_current_player_actions()
      return action in actions

    """
    Get all the actions that the current player can perform.
    """
    def get_current_player_actions(self):
      abstract

    """
    Applies a given action to this state. It assume that the actions is
    valid. This must be checked with is_action_valid.
    """
    def apply_action(self, action):
        abstract

    """
    Return the scores of each players.
    """
    def get_scores(self):
        abstract

    """
    Get the winner of the game. Call only if the game is over.
    """
    def get_winner(self):
        abstract

    """
    Return the information about the state that is given to students.
    Usually they have to implement their own state class.
    """
    def get_state_data(self):
        abstract
