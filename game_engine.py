import libtcodpy as libtcod
import game_piece
import textwrap

class Game():
    """Represents a game with a board and a message system. Is called from the UI
       to process the next turn."""
    def __init__(self, message_system, board):
        self.game_state = "playing"
        self.actors = []
        self.index = 0
        self.message_system = message_system
        self.board = board
        self.board.game = self

    def add_actor(self, actor):
        self.actors.append(actor)

    def remove_actor(self, actor):
        self.actors.remove(actor)

    def process_turn(self):
        if len(self.actors) > 0:
            actor = self.actors[self.index]

            if actor.ai:
                action = actor.ai.take_turn()

                if not action:
                    return

                while(True):
                    result, alternative = action.perform()
                    if not result:
                        return
                    if not alternative:
                        break
                    action = alternative

                self.index += 1
                self.index %= len(self.actors)

class Message:
    """Stores and prints a message buffer of a set size"""
    def __init__(self, buffer_max_size, width):
        self.buffer_max_size = buffer_max_size
        self.width = width
        self.buffer = []

    def draw(self, console):
        self.clear(console)

        libtcod.console_set_default_foreground(console, libtcod.white)
        y = 0
        for line in self.buffer:
            libtcod.console_print_ex(console, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
            y += 1

    def clear(self, console):
        libtcod.console_clear(console)

    def add_message(self, message):
        message_lines = textwrap.wrap(message, self.width)

        for line in message_lines:
            if len(self.buffer) == self.buffer_max_size:
                #Delete the first item to make room
                del self.buffer[0]

            #Add the line to the message buffer
            self.buffer.append(line)

class StatusBar:
    """Prints status information on a bar on the screen"""
    def __init__(self, player, current_spell):
        self.player = player
        self.current_spell = current_spell

    def draw(self, console):
        libtcod.console_clear(console)
        libtcod.console_set_default_foreground(console, libtcod.white)
        libtcod.console_print_ex(console, 3, 0, libtcod.BKGND_NONE, libtcod.LEFT, 'HP: ' + str(self.player.fighter.hp))
        if self.current_spell:
            libtcod.console_print_ex(console, 10, 0, libtcod.BKGND_NONE, libtcod.LEFT, self.current_spell.target_function.__name__)
            libtcod.console_print_ex(console, 30, 0, libtcod.BKGND_NONE, libtcod.LEFT, self.current_spell.effect_function.__name__)

class MoveAction(object):
    """The Move Action encodes the movement of a game_piece on the board
    including collision detection and offering attack as an alternative
    when bumping into monsters."""
    def __init__(self, piece, x, y):
        self.piece = piece
        self.x = x
        self.y = y

    def perform(self):
        #Check if the destination is blocked by a piece
        blocking_piece = self.piece.board.is_blocked(self.x, self.y)

        #If blocked by something
        if blocking_piece:
            #If blocked by a piece
            if isinstance(blocking_piece, game_piece.Piece) and self.piece.fighter and blocking_piece.fighter:
                return True, AttackAction(self.piece, blocking_piece)
            return False, None
        else:
            #Move to the destination
            self.piece.x = self.x
            self.piece.y = self.y

            return True, None

class WaitAction(object):
    """The Wait Action encodes a piece standing still"""
    def __init__(self, piece):
        self.piece = piece

    def perform(self):
        return True, None

class AttackAction(object):
    """The Attack Action encodes one piece on the board attacking anouther"""
    def __init__(self, attacker, defender):
        self.attacker = attacker
        self.defender = defender

    def perform(self):
        self.defender.fighter.take_damage(self.attacker.fighter.power)
        return True, None
