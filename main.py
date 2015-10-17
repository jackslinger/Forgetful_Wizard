import libtcodpy as libtcod
from dungeon import *

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

def handle_keys():
	global player

	#key = libtcod.console_check_for_keypress()  #real-time
	key = libtcod.console_wait_for_keypress(True)  #turn-based

	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt+Enter: toggle fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

	elif key.vk == libtcod.KEY_ESCAPE:
		return True  #exit game

	if libtcod.console_is_key_pressed(libtcod.KEY_UP):
		player.y -= 1

	elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
		player.y += 1

	elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
		player.x -= 1

	elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
		player.x += 1

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

map = Map(SCREEN_WIDTH, SCREEN_HEIGHT)

player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', libtcod.white)

while not libtcod.console_is_window_closed():
	map.draw(con)
	player.draw(con)

	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
	libtcod.console_flush()

	libtcod.console_put_char(con, player.x, player.y, ' ', libtcod.BKGND_NONE)

	exit = handle_keys()
	if exit:
		break
