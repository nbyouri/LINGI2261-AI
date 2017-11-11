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
    rocks = [ ]
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
