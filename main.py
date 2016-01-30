import libtcodpy as libtcod
from dungeon import *

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

player_action = None

def handle_keys(board):
	game_state = board.game.game_state
	player = board.player

	key = libtcod.Key()
	mouse = libtcod.Mouse()
	libtcod.sys_wait_for_event(libtcod.EVENT_KEY_PRESS,key,mouse,False)

	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt+Enter: toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	elif key.vk == libtcod.KEY_ESCAPE:
		return "exit"  #exit game

	if (game_state == "playing"):
		if libtcod.console_is_key_pressed(libtcod.KEY_UP) or key.vk == libtcod.KEY_KP8 or key.c == ord('k'):
			valid_move = board.move_or_attack(player,0,-1)
			if valid_move:
				return "moved"
			else:
				return "not_moved"
		elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN) or key.vk == libtcod.KEY_KP2 or key.c == ord('j'):
			valid_move = board.move_or_attack(player,0,1)
			if valid_move:
				return "moved"
			else:
				return "not_moved"
		elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT) or key.vk == libtcod.KEY_KP4 or key.c == ord('h'):
			valid_move = board.move_or_attack(player,-1,0)
			if valid_move:
				return "moved"
			else:
				return "not_moved"
		elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT) or key.vk == libtcod.KEY_KP6 or key.c == ord('l'):
			valid_move = board.move_or_attack(player,1,0)
			if valid_move:
				return "moved"
			else:
				return "not_moved"
		elif key.c == ord('y'):
			valid_move = board.move_or_attack(player,-1,-1)
			if valid_move:
				return "moved"
			else:
				return "not_moved"
		elif key.c == ord('u'):
			valid_move = board.move_or_attack(player,1,-1)
			if valid_move:
				return "moved"
			else:
				return "not_moved"
		elif key.c == ord('b'):
			valid_move = board.move_or_attack(player,-1,1)
			if valid_move:
				return "moved"
			else:
				return "not_moved"
		elif key.c == ord('n'):
			valid_move = board.move_or_attack(player,1,1)
			if valid_move:
				return "moved"
			else:
				return "not_moved"
		elif key.c == ord('.'):
			#Wait in one place
			return "waiting"


libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

game = Game()
board = Board(SCREEN_WIDTH, SCREEN_HEIGHT, game)
board.generate()

while not libtcod.console_is_window_closed():
	board.draw(con)

	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
	libtcod.console_flush()

	player_action = handle_keys(board)
	if player_action == "exit":
		break
	elif player_action == "moved" or player_action == "waiting":
		for piece in board.pieces:
			if piece.ai:
				piece.ai.take_turn()
