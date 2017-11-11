import math
import pygame
import sys
import os
import random
import argparse
import time
import signal
from pygame.locals import *
from siam import *
from threading import Thread
from tkinter import *
from tkinter import messagebox


def get_action_threaded(state, last_action, agent, timeleft):
  result = [ None ]
  thread = Thread(target=get_action, args=(state, last_action, agent, timeleft, result))
  thread.start()
  return result

def get_action(state, last_action, agent, timeleft, result):
  action = agent.get_action(state, last_action, timeleft)
  result[0] = action

class Button():

  def __init__(self, siam, img_active, img_inactive, x, y, width, height):
    self.siam = siam
    self.img_active = img_active
    self.img_inactive = img_inactive
    self.x = x
    self.y = y
    self.width = width
    self.height = height

  def get_image(self):
    if self.is_active():
      return self.img_active
    return self.img_inactive
  
  def position(self):
    return (self.x, self.y)

  def contains_pos(self, pos):
    return self.x <= pos[0] and pos[0] <= self.x + self.width and self.y <= pos[1] and pos[1] <= self.y + self.height

  def is_active(self):
    pass
  
  def action(self):
    pass

class UndoButton(Button):

  def __init__(self, siam, img_active, img_inactive, x, y, width, height):
    super(UndoButton, self).__init__(siam, img_active, img_inactive, x, y, width, height)
  
  def is_active(self):
    if not siam.player_type[siam.state.get_cur_player()] == 'human': return False
    return True
  
  def action(self):
    self.siam.undo()
  
class MoveButton(Button):

  def __init__(self, siam, img_active, img_inactive, x, y, width, height):
    super(MoveButton, self).__init__(siam, img_active, img_inactive, x, y, width, height)
  
  def is_active(self):
    if not siam.player_type[siam.state.get_cur_player()] == 'human': return False
    if siam.placed or siam.moved or siam.selected_cell == None:
      return False
    return siam.temporary_state.can_move(siam.selected_cell)
  
  def action(self):
    orig = siam.selected_cell
    dest = siam.temporary_state.get_move_dest(orig)
    if not siam.temporary_state.in_bounds_pos(dest):
      # recover
      action = ('recover', orig)
      siam.last_action = action
      siam.temporary_state.apply_action(action, False)
      siam.finish_human_play()
    else:
      # move
      action = ('move', orig, dest, siam.temporary_state.face[orig[0]][orig[1]])
      siam.last_action = action
      siam.temporary_state.apply_action(action, False)
      siam.selected_cell = dest
      siam.moved = True

class PushButton(Button):

  def __init__(self, siam, img_active, img_inactive, x, y, width, height):
    super(PushButton, self).__init__(siam, img_active, img_inactive, x, y, width, height)
  
  def is_active(self):
    if not siam.player_type[siam.state.get_cur_player()] == 'human': return False
    rotated = False
    if siam.selected_cell != None:
      i = siam.selected_cell[0]
      j = siam.selected_cell[1]
      rotated = siam.state.face[i][j] != siam.temporary_state.face[i][j]
    if rotated or siam.moved or siam.placed or siam.selected_cell == None:
      return False
    return siam.temporary_state.can_push(siam.selected_cell, siam.state.face[i][j])[0]
  
  def action(self):
    action = ('push', siam.selected_cell)
    siam.last_action = action
    siam.temporary_state.apply_action(action, False)
    siam.finish_human_play()

class RotateButton(Button):

  def __init__(self, siam, img_active, img_inactive, x, y, width, height):
    super(RotateButton, self).__init__(siam, img_active, img_inactive, x, y, width, height)
  
  def is_active(self):
    if not siam.player_type[siam.state.get_cur_player()] == 'human': return False
    if siam.selected_cell == None:
      return False
    return True
    
  def action(self):
    i = siam.selected_cell[0]
    j = siam.selected_cell[1]
    action = ('face', siam.selected_cell, (siam.temporary_state.face[i][j] + 1) % 4)
    siam.last_action = action
    siam.temporary_state.apply_action(action, False)

class FinishButton(Button):

  def __init__(self, siam, img_active, img_inactive, x, y, width, height):
    super(FinishButton, self).__init__(siam, img_active, img_inactive, x, y, width, height)
  
  def is_active(self):
    if not siam.player_type[siam.state.get_cur_player()] == 'human': return False
    return True
  
  def action(self):
    siam.finish_human_play()


MIN_HEIGHT = 500
TOP_MARGIN = 50
BUTTON_HEIGHT = 60
BUTTON_WIDTH = 200


MIN_WINDOW_HEIGHT = 500
MENU_WIDTH = 300
BUTTON_MARGIN = 20
MARGIN = 20

class Siam():

  def __init__(self, total_time, wait, quit, player_type, agents, scale, verbose):
    self.total_time = total_time
    self.nb_rows = 5
    self.nb_cols = 5
    self.wait = wait
    self.quit = quit
    self.player_type = player_type
    self.agents = agents
    self.scale = scale
    self.verbose = verbose

  def run(self):
    self.left_margin = 200
    self.initialize_game()
    # initialize pygame
    pygame.init()
    # initialize time variables
    self.time_left = [total_time for _ in range(2)]
    # initialize the state
    self.state = SiamState()
    # precompute the hexagons
    # compute the size the grid will take on the window
    # create the screen
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    self.screen_size = (self.window_width, self.window_height)
    self.screen = pygame.display.set_mode(self.screen_size)
    # initialize fonts
    self.score_points_font = pygame.font.SysFont("monospace", 30, True)
    self.end_points_font = pygame.font.SysFont("monospace", 30, True)
    # flag to know if the ai thread has been started
    self.ai_thinking = False
    self.over_cell = None
    self.selected_cell = None
    self.over_button = None
    self.rotation = 0
    self.move = None
    self.temporary_state = None
    self.moved = False
    self.placed = False
    self.ai_thinking = False
    self.action = [None]
    self.start = 0
    self.end = 0
    self.last_action = None
    self.history = [ ]
    # time
    start = 0
    end = 0
    while not self.state.game_over():
      self.draw_screen()
      if self.player_type[self.state.get_cur_player()] == 'human':
        self.handle_human()
      else:
        self.handle_ai()
    if not self.quit:
      self.draw_screen()
      self.wait_for_window_close()
      #pygame.draw.rect(self.screen, (255, 255, 255), [150, 10, 50, 20])
      #time.sleep(1)

  def initialize_game(self):
    if(self.verbose): print('loading resources')
    # load resources
    self.tile             = pygame.image.load('./resources/grass.png')
    self.rhino            = pygame.image.load('./resources/rhino.png')
    self.rhino_reserve    = pygame.image.load('./resources/rhino_reserve.png')
    self.elephant         = pygame.image.load('./resources/elephant.png')
    self.elephant_reserve = pygame.image.load('./resources/elephant_reserve.png')
    self.rock             = pygame.image.load('./resources/rock.png')
    self.arrow            = pygame.image.load('./resources/green_arrow.png')
    self.arrow_over       = pygame.image.load('./resources/yellow_arrow.png')
    self.over_aura        = pygame.image.load('./resources/yellow_aura.png')
    self.black_aura       = pygame.image.load('./resources/black_aura.png')
    self.selected_aura    = pygame.image.load('./resources/blue_aura.png')
    self.cur_player_aura  = pygame.image.load('./resources/green_aura.png')
    self.score_lbl        = pygame.image.load('./resources/score.png')
    self.button_push_g    = pygame.image.load('./resources/button_push_g.png')
    self.button_rotate_g  = pygame.image.load('./resources/button_rotate_g.png')
    self.button_move_g    = pygame.image.load('./resources/button_move_g.png')
    self.button_finish_g  = pygame.image.load('./resources/button_finish_g.png')
    self.button_undo_g    = pygame.image.load('./resources/button_undo_g.png')
    self.button_push_r    = pygame.image.load('./resources/button_push_r.png')
    self.button_rotate_r  = pygame.image.load('./resources/button_rotate_r.png')
    self.button_move_r    = pygame.image.load('./resources/button_move_r.png')
    self.button_finish_r  = pygame.image.load('./resources/button_finish_r.png')
    self.button_undo_r    = pygame.image.load('./resources/button_undo_r.png')
    
    # compute sizes
    # compute piece dimensions
    rect = self.tile.get_rect()
    self.W = int(rect.width * self.scale)
    self.H = int(rect.height * self.scale)
    self.menu_width = int(MENU_WIDTH * self.scale)
    self.button_width = int(MENU_WIDTH * self.scale)
    self.button_height = int(BUTTON_HEIGHT * self.scale)
    # scale resources
    self.tile             = pygame.transform.scale(self.tile, (self.W, self.H))
    self.rhino            = pygame.transform.scale(self.rhino, (self.W, self.H))
    self.rhino_reserve    = pygame.transform.scale(self.rhino_reserve, (self.menu_width, self.menu_width))
    self.elephant         = pygame.transform.scale(self.elephant, (self.W, self.H))
    self.elephant_reserve = pygame.transform.scale(self.elephant_reserve, (self.menu_width, self.menu_width))
    self.rock             = pygame.transform.scale(self.rock, (self.W, self.H))
    self.pieces           = {PLAYER0: self.rhino, PLAYER1: self.elephant, ROCK: self.rock}
    self.arrow            = pygame.transform.scale(self.arrow, (self.W, self.H))
    self.arrow_over       = pygame.transform.scale(self.arrow_over, (self.W, self.H))
    self.black_aura       = pygame.transform.scale(self.black_aura, (self.W, self.H))
    self.over_aura        = pygame.transform.scale(self.over_aura, (self.W, self.H))
    self.selected_aura    = pygame.transform.scale(self.selected_aura, (self.W, self.H))
    self.cur_player_aura  = pygame.transform.scale(self.cur_player_aura, (self.menu_width, self.menu_width))
    self.score_lbl        = pygame.transform.scale(self.score_lbl, (self.W, self.H))
    self.button_push_g    = pygame.transform.scale(self.button_push_g, (self.button_width, self.button_height))
    self.button_rotate_g  = pygame.transform.scale(self.button_rotate_g, (self.button_width, self.button_height))
    self.button_move_g    = pygame.transform.scale(self.button_move_g, (self.button_width, self.button_height))
    self.button_finish_g  = pygame.transform.scale(self.button_finish_g, (self.button_width, self.button_height))
    self.button_undo_g    = pygame.transform.scale(self.button_undo_g, (self.button_width, self.button_height))
    self.button_push_r    = pygame.transform.scale(self.button_push_r, (self.button_width, self.button_height))
    self.button_rotate_r  = pygame.transform.scale(self.button_rotate_r, (self.button_width, self.button_height))
    self.button_move_r    = pygame.transform.scale(self.button_move_r, (self.button_width, self.button_height))
    self.button_finish_r  = pygame.transform.scale(self.button_finish_r, (self.button_width, self.button_height))
    self.button_undo_r    = pygame.transform.scale(self.button_undo_r, (self.button_width, self.button_height))
    
    self.board_size = (self.W * self.nb_cols, self.H * self.nb_rows)
    rect = self.tile.get_rect()
    # compute window dimensions
    self.window_height = 7 * self.H
    self.window_width = 7 * self.W + self.menu_width + 2 * MARGIN
    self.menu_x0 = 7 * self.W + MARGIN
    self.menu_y0 = self.H
    # initialize buttons
    self.move_button   = MoveButton(self, self.button_move_g, self.button_move_r, self.menu_x0, self.menu_y0, self.button_width, self.button_height)
    self.rotate_button = RotateButton(self, self.button_rotate_g, self.button_rotate_r, self.menu_x0, self.menu_y0 + 1 * (self.button_height + 10), self.button_width, self.button_height)
    self.push_button   = PushButton(self, self.button_push_g, self.button_push_r, self.menu_x0, self.menu_y0 + 2 * (self.button_height + 10), self.button_width, self.button_height)
    self.finish_button = FinishButton(self, self.button_finish_g, self.button_finish_r, self.menu_x0, self.menu_y0 + 3 * (self.button_height + 10), self.button_width, self.button_height)
    self.undo_button   = UndoButton(self, self.button_undo_g, self.button_undo_r, self.menu_x0, self.menu_y0 + 4 * (self.button_height + 10), self.button_width, self.button_height)
    self.buttons = [ self.move_button, self.rotate_button, self.push_button, self.finish_button, self.undo_button ]

  def undo(self):
    self.selected_cell = None
    self.moved = False
    self.placed = False
    self.temporary_state = None

  def finish_human_play(self):
    self.history.append(self.state.copy())
    self.selected_cell = None
    self.moved = False
    self.placed = False
    if self.temporary_state != None:
      self.state = self.temporary_state
      self.temporary_state = None
    self.state.go_to_next_player()
    print('humand action: ' + str(self.last_action))

  def handle_human(self):
    #print('handle human')
    events = pygame.event.get()
    for event in events:
      if event.type == pygame.QUIT:
        # quit the game
        pygame.quit()
        sys.exit()
      elif event.type == pygame.MOUSEBUTTONDOWN:
        clicked_cell = self.get_cell(event.pos)
        if self.selected_cell == None and clicked_cell != None and self.is_selectable(clicked_cell[0], clicked_cell[1]):
          self.selected_cell = clicked_cell
          self.temporary_state = self.state.copy()
          # if the cell is empty we need to add a new piece
          if self.temporary_state.board[self.selected_cell[0]][self.selected_cell[1]] == EMPTY:
            i = self.selected_cell[0]
            j = self.selected_cell[1]
            action = ('place', self.selected_cell, 1)
            if i == 0:
              action = ('place', self.selected_cell, DOWN)
            elif i == self.nb_rows - 1:
              action = ('place', self.selected_cell, UP)
            elif j == 0:
              action = ('place', self.selected_cell, 3)
            self.temporary_state.apply_action(action, False)
            self.last_action = action
            self.placed = True
        # check for place-push
        if self.selected_cell == None and clicked_cell in PUSH_PLACE:
          position = PUSH_PLACE[clicked_cell][0]
          face = PUSH_PLACE[clicked_cell][1]
          if self.state.can_enter_push(position, face)[0]:
            action = ('place-push', position, face)
            self.last_action = action
            self.state.apply_action(action, False)
            siam.finish_human_play()
        # handle button clicks
        for button in self.buttons:
          if button.is_active() and button.contains_pos(event.pos):
            button.action()
      elif event.type == pygame.MOUSEMOTION:
        self.over_cell = self.get_cell(event.pos)
        self.over_button = self.get_button(event.pos)
      else:
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_f] != 0 and self.finish_button.is_active():
          # finish
          self.finish_button.action()
        if pressed[pygame.K_r] != 0 and self.rotate_button.is_active():
          # rotate
          self.rotate_button.action()
        if pressed[pygame.K_m] != 0 and self.move_button.is_active():
          # move
          self.move_button.action()
        if pressed[pygame.K_p] != 0 and self.push_button.is_active():
          # push
          self.push_button.action()
        if pressed[pygame.K_u] != 0 and self.undo_button.is_active():
          # undo
          self.undo_button.action()

  def get_cell(self, pos):
    i = (pos[1] - MARGIN) // self.H - 1
    j = (pos[0] - MARGIN) // self.W - 1
    if -1 <= i and i <= self.state.nb_rows and -1 <= j and j <= self.state.nb_cols:
      return (i, j)
    return None

  def handle_ai(self):
    if not self.ai_thinking:
      print('request action')
      self.action = get_action_threaded(self.state.copy(), self.last_action, self.agents[self.state.cur_player], self.time_left[self.state.cur_player])
      self.start = time.time()
      self.ai_thinking = True
    elif self.action != [None]:
      self.end = time.time()
      self.time_left[self.state.cur_player] -= self.end - self.start
      self.ai_thinking = False
      self.start = 0
      self.end = 0
      if self.time_left[self.state.cur_player] > 0:
        if not self.state.is_action_valid(self.action[0]):
          print('invalid action from ai {0}: {1}'.format(self.state.cur_player, self.action[0]))
          self.state.winner = 1 - self.state.cur_player
        else:
          self.history.append(self.state.copy())
          self.last_action = self.action[0]
          self.state.apply_action(self.action[0])
          self.action = [None]
          time.sleep(wait)

  def draw_screen(self):
    if self.temporary_state == None:
      self.draw_screen_aux(self.state)
    else:
      self.draw_screen_aux(self.temporary_state)

  def draw_screen_aux(self, state):
    cur_player = state.cur_player
    # fill the screen black
    self.screen.fill((0,0,0))
    # draw buttons
    for button in self.buttons:
      self.screen.blit(button.get_image(), button.position()) 
    # draw the tiles
    for i in range(self.nb_rows):
      for j in range(self.nb_cols):
        self.screen.blit(self.tile, ((j + 1) * self.H, (i + 1) * self.W))
        if state.board[i][j] != EMPTY:
          self.draw_piece(state, i, j)
    # draw reserve
    self.screen.blit(self.rhino_reserve, (self.menu_x0, self.buttons[-1].position()[1] + self.buttons[-1].height + 10))
    self.screen.blit(self.elephant_reserve, (self.menu_x0, self.buttons[-1].position()[1] + self.buttons[-1].height + self.H + 20))
    if not state.game_over():
      if state.cur_player == 0:
        self.screen.blit(self.cur_player_aura, (self.menu_x0, self.buttons[-1].position()[1] + self.buttons[-1].height + 10))
      else:
       self.screen.blit(self.cur_player_aura, (self.menu_x0, self.buttons[-1].position()[1] + self.buttons[-1].height + self.H + 20))
    label = self.score_points_font.render('x' + str(state.reserve[0]), 1, (255,255,255))
    self.screen.blit(label, (self.menu_x0 + self.W / 2, self.buttons[-1].position()[1] + self.buttons[-1].height + 10 + self.H / 2))
    label = self.score_points_font.render('x' + str(state.reserve[1]), 1, (255,255,255))
    self.screen.blit(label, (self.menu_x0 + self.W / 2, self.buttons[-1].position()[1] + self.buttons[-1].height + self.H + 20 + self.H / 2))
    # draw over cell
    if self.selected_cell == None and self.over_cell != None and state.in_bounds_pos(self.over_cell):
      i = self.over_cell[0]
      j = self.over_cell[1]
      bij = state.board[i][j]
      if bij == cur_player:
        self.screen.blit(self.over_aura, ((j + 1) * self.H , (i + 1) * self.W))
      # draw possible placement
      if self.can_place_piece(i, j):
        self.screen.blit(self.over_aura, ((j + 1) * self.H, (i + 1) * self.W))
    # draw selected
    if self.selected_cell != None:
      i = self.selected_cell[0]
      j = self.selected_cell[1]
      self.screen.blit(self.selected_aura, ((j + 1) * self.H, (i + 1) * self.W))
    # draw side arrows
    for pos in BORDER:
      for face in FACE:
        if state.can_enter_push(pos, face)[0]:
          i = pos[0] + DIR[OPPOSITE[face]][0]
          j = pos[1] + DIR[OPPOSITE[face]][1]
          if self.selected_cell == None and self.over_cell != None and (i, j) == self.over_cell:
            self.screen.blit(pygame.transform.rotate(self.arrow_over, 90 * face), ((j + 1) * self.H, (i + 1) * self.W))
          else:
            self.screen.blit(pygame.transform.rotate(self.arrow, 90 * face), ((j + 1) * self.H, (i + 1) * self.W))
    
    pygame.display.flip()
    
  def in_bounds(self, pos):
    return 0 <= pos[0] and pos[0] < self.nb_rows and 0 <= pos[1] and pos[1] < self.nb_cols

  def get_button(self, pos):
    for k in range(3):
      if self.buttons[i].contains_pos(pos):
        return k
    return None

  def is_selectable(self, i, j):
    return self.in_bounds((i, j)) and (self.state.board[i][j] == self.state.cur_player or self.can_place_piece(i, j))

  def can_place_piece(self, i, j):
    if self.state.turn < 2 and j == 2:
      return False
    return self.state.board[i][j] == EMPTY and (i == 0 or i == self.nb_rows - 1 or j == 0 or j == self.nb_cols - 1) and self.state.reserve[self.state.cur_player] > 0

  def draw_piece(self, state, i, j):
    if state.board_value(i, j) == ROCK:
      self.screen.blit(pygame.transform.rotate(self.pieces[state.board[i][j]], 90 * UP), ((j + 1) * self.H, (i + 1) * self.W))
    else:
      self.screen.blit(pygame.transform.rotate(self.pieces[state.board[i][j]], 90 * state.face[i][j]), ((j + 1) * self.H, (i + 1) * self.W))
    if not state.board[i][j] == ROCK and state.can_push((i, j), state.face[i][j])[0]:
      self.screen.blit(pygame.transform.rotate(self.arrow, 90 * state.face[i][j]), ((j + 1) * self.H, (i + 1) * self.W))
    if (i, j) != self.selected_cell:
      self.screen.blit(self.black_aura, ((j + 1) * self.H, (i + 1) * self.W))
    
  def wait_for_window_close(self):
    Tk().wm_withdraw() #to hide the main window
    messagebox.showinfo('Ok', 'Player {0} ({1}) wins the game!'.format(self.state.winner + 1, ['Rhinos', 'Elephans'][self.state.winner]))
    while True:
      # the game is over, we only case about the close event
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          # quit the game
          pygame.quit()
          sys.exit()


if __name__ == "__main__":
  # process the arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('-q', help='exit at the end', action='store_true')
  parser.add_argument('-t', help='total number of seconds credited to each player')
  parser.add_argument('-ai0', help='path to the ai that will play as player 0')
  parser.add_argument('-ai1', help='path to the ai that will play as player 1')
  parser.add_argument('-w', help='time to wait after ai action')
  parser.add_argument('-scale', help='image scale to fit on the screen')
  args = parser.parse_args()
  # set the time to play
  total_time = int(args.t) if args.t != None else 180
  wait = float(args.w) if args.w != None else 0
  quit = args.q
  player_type = [ 'human', 'human' ]
  player_type[0] = args.ai0 if args.ai0 != None else 'human'
  player_type[1] = args.ai1 if args.ai1 != None else 'human'
  agents = [ None for _ in range(2) ]
  # load the agents
  for i in range(2):
    if player_type[i] != 'human':
      j = player_type[i].rfind('/')
      # extract the dir from the agent
      dir = player_type[i][:j]
      # add the dir to the system path
      sys.path.append(dir)
      # extract the agent filename
      file = player_type[i][j+1:]
      # create the agent nstance
      agents[i] = getattr(__import__(file), 'MyAgent')()
      agents[i].set_id(i)
  scale = float(args.scale) if args.scale != None else 0.5
  # initialize and run the game
  siam = Siam(total_time, wait, quit, player_type, agents, scale, True)
  siam.run()