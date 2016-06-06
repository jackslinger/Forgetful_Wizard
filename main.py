import libtcodpy as libtcod
from dungeon import *
import spells

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 60

MAP_WIDTH = 80
MAP_HEIGHT = 41

PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT - 1

player_action = None

class ServiceLocator(object):
	"""Provides access to game services that are needed everywhere e.g. message_system"""
	def __init__(self):
		print "Put code here"

def menu(header, options, width):
	if len(options) > 26:
		raise ValueError("Can't have a menu with more than 26 options.")

	#Calculate the word wrapped height of the header and the total window height
	header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
	height = len(options) + header_height

	#Create a new window for the menu
	window = libtcod.console_new(width, height)

	#Print the header with auto wrap
	libtcod.console_set_default_foreground(window, libtcod.white)
	libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

	#Print all the options
	y = header_height
	letter_index = ord('a')
	for option_text in options:
		text = "(" + chr(letter_index) + ") " + option_text
		libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
		y += 1
		letter_index += 1

	#Blit to the middle of the main console
	x = SCREEN_WIDTH/2 - width/2
	y = SCREEN_HEIGHT/2 - height/2
	libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

def handle_keys(board, current_spell):
	game_state = board.game.game_state
	player = board.player

	# key = libtcod.console_check_for_keypress()

	key = libtcod.Key()
	mouse = libtcod.Mouse()
	libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt+Enter: toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	elif key.vk == libtcod.KEY_ESCAPE:
		return "exit"  #exit game

	if not key.pressed:
		return

	if (game_state == "playing"):
		if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8 or key.c == ord('k'):
			player.ai.set_action(MoveAction(player, player.x, player.y - 1))
		elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2 or key.c == ord('j'):
			player.ai.set_action(MoveAction(player, player.x, player.y + 1))
		elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4 or key.c == ord('h'):
			player.ai.set_action(MoveAction(player, player.x - 1, player.y))
		elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6 or key.c == ord('l'):
			player.ai.set_action(MoveAction(player, player.x + 1, player.y))
		elif key.c == ord('y') or key.vk == libtcod.KEY_KP7:
			player.ai.set_action(MoveAction(player, player.x - 1, player.y - 1))
		elif key.c == ord('u') or key.vk == libtcod.KEY_KP9:
			player.ai.set_action(MoveAction(player, player.x + 1, player.y - 1))
		elif key.c == ord('b') or key.vk == libtcod.KEY_KP1:
			player.ai.set_action(MoveAction(player, player.x - 1, player.y + 1))
		elif key.c == ord('n') or key.vk == libtcod.KEY_KP3:
			player.ai.set_action(MoveAction(player, player.x + 1, player.y + 1))
		elif key.c == ord('.') or key.vk == libtcod.KEY_KP5:
			#Wait in one place
			player.ai.set_action(WaitAction(player))
		elif key.c == ord('z'):
			zap = spells.Spell(board.player, spells.burst_target, spells.freeze, max_range=5)
			zap.cast()
		elif key.c == ord('x'):
			current_spell.cast()
			current_spell.target_function = spells.random_target()
			current_spell.effect_function = spells.random_effect()


libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)

libtcod.sys_set_fps(LIMIT_FPS)

con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)

panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
libtcod.console_set_default_background(panel, libtcod.black)

message_system = Message(PANEL_HEIGHT, SCREEN_WIDTH)
message_system.add_message("Welcome to Forgetfull Wizard!")

board = Board(MAP_WIDTH, MAP_HEIGHT)

game = Game(message_system, board)

board.generate()

status_panel = libtcod.console_new(SCREEN_WIDTH, 1)
libtcod.console_set_default_background(status_panel, libtcod.black)

current_spell = spells.random_spell(board.player)
status_bar = StatusBar(board.player, current_spell)

while not libtcod.console_is_window_closed():
	player_action = handle_keys(board, current_spell)
	if player_action == "exit":
		break

	render = game.process_turn()

	board.draw(con)
	message_system.draw(panel)
	status_bar.draw(status_panel)

	libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)
	libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)
	libtcod.console_blit(status_panel, 0, 0, SCREEN_WIDTH, 1, 0, 0, PANEL_Y-1)
	libtcod.console_flush()
