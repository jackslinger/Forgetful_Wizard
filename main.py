import libtcodpy as libtcod
from dungeon import *

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

game_state = "playing"
player_action = None

def handle_keys(board):
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
		if libtcod.console_is_key_pressed(libtcod.KEY_UP) or key.vk == libtcod.KEY_KP8:
			board.move_or_attack(player,0,-1)
			return "moved"
		elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN) or key.vk == libtcod.KEY_KP2:
			board.move_or_attack(player,0,1)
			return "moved"
		elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT) or key.vk == libtcod.KEY_KP4:
			board.move_or_attack(player,-1,0)
			return "moved"
		elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT) or key.vk == libtcod.KEY_KP6:
			board.move_or_attack(player,1,0)
			return "moved"


libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

board = Board(SCREEN_WIDTH, SCREEN_HEIGHT)
board.generate()

while not libtcod.console_is_window_closed():
	board.draw(con)

	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
	libtcod.console_flush()

	player_action = handle_keys(board)
	if player_action == "exit":
		break
	elif player_action != None:
		for piece in board.pieces:
			if piece.ai:
				piece.ai.take_turn()
