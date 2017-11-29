import sys
import traceback
import time
import random
import signal
import math
import datetime
import sys
from siam import SiamState

def handler(signum, frame):
    raise Exception('end of time')

def play_game(initial_state, names, players, total_time, verbose, output):
    f = open(output, 'w')
    # create the initial state
    state = initial_state
    # initialize the time left for each player
    time_left = [ total_time for i in range(len(players)) ]
    timedout = -1
    crashed = -1
    invalidaction = -1
    quit = -1
    exception = ''
    action = None
    last_action = None
    # loop until the game is over
    while crashed == -1 and timedout == -1 and invalidaction == -1 and not state.game_over():
        f.write(str(state) + '\n')
        cur_player = state.get_cur_player()
        start = 0
        end = 0
        try:
            # get the start time
            start = time.time()
            action = get_action_timed(players[cur_player], state, last_action, int(time_left[cur_player]) + 1)
            # get the end time
            end = time.time()
        except TimeoutError:
            # set that the current player timed out
            timedout = cur_player
            # write on the log that the current player timed out
            f.write(str(cur_player) + ' timeout\n')
        except Exception as e:
            trace = traceback.format_exc().split('\n')
            exception = trace[len(trace) - 2]
            # set that the current player crashed
            crashed = cur_player
            # write that the current player crashed
            f.write(str(cur_player) + ' crashed (' + str(e) + ')\n')
        else:
            # compute enlapsed time
            enlapsed = end - start
            # update time
            time_left[cur_player] = time_left[cur_player] - enlapsed
            # check if the action is valid
            try:
                if state.is_action_valid(action):
                    # the action is valid so we can apply the action to the state
                    # write the action of the current player on the log
                    f.write(str(action) + '\n')
                    state.apply_action(action)
                    last_action = action
                else:
                    # set that the current player gave an invalid action
                    invalidaction = cur_player
                    f.write(str(cur_player) + ' invalid action\n')
                    break
            except Exception as e:
                crashed = cur_player
                f.write(str(cur_player) + ' could not apply action: ' + str(e) + '\n')
                break
    # output the result of the game: 0 if player 0 wins, 1 if player 1 wins and -1 if it is a draw
    # first check if there was timeout, crash, invalid action or quit
    if timedout != -1:
        return (1 - timedout, names[timedout] + ' timed out', total_time - time_left[0], total_time - time_left[1], state.get_scores())
    elif crashed != -1:
        return (1 - crashed, names[crashed] + ' crashed: ' + exception, total_time - time_left[0], total_time - time_left[1], state.get_scores())
    elif invalidaction != -1:
        return (1 - invalidaction, names[invalidaction] + ' gave an invalid action: ' + str(action), total_time - time_left[0], total_time - time_left[1], state.get_scores())
    elif quit != -1:
        return (1 - quit, names[quit] + ' rage quit', total_time - time_left[0], total_time - time_left[1], state.get_scores())    
    else:
        f.write('winner: ' + str(state.winner))
        f.close()
        # all is ok, output the winner
        return (state.get_winner(), total_time - time_left[0], total_time - time_left[1], state.get_scores())

"""
Define behavior in case of timeout.
"""
def handle_timeout(signum, frame):
    raise TimeoutError()

"""
Get an action from player with a timeout.
"""
def get_action_timed(player, state, last_action, time_left):
    signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(time_left)
    try:
        action = player.get_action(state.copy(), last_action, time_left)
    finally:
        signal.alarm(0)
    return action

def make_match(agents, time, output):
    initial_state = SiamState()
    names = [a.get_name() for a in agents]
    return play_game(initial_state, names, agents, time, False, output)

if __name__ == "__main__":
    agent1 = getattr(__import__(sys.argv[1]), 'MyAgent')()
    agent1.set_id(0)
    agent2 = getattr(__import__(sys.argv[2]), 'MyAgent')()
    agent2.set_id(1)
    make_match([agent1, agent2], int(sys.argv[3]), sys.argv[4])


