import libtcodpy as libtcod
import math
import game_engine

class Sprite(object):
    """A Sprite represents a colored char that can draw it's self at a given position"""
    def __init__(self, char, color):
        super(Sprite, self).__init__()
        self.char = char
        self.color = color

    def draw(self, console, x, y):
        libtcod.console_set_default_foreground(console, self.color)
        libtcod.console_put_char(console, x, y, self.char, libtcod.BKGND_NONE)

class Piece:
    """this is a generic object: the player, a monster, an item, the stairs...
    it's represented by a character on screen
    it's placed on a particular board object
    it can optionaly have fighter, ai and status components"""
    def __init__(self, board, x, y, char, color, name, blocks_passage=False, blocks_light=False, fighter=None, ai=None, status=None):
        self.board = board
        self.x = x
        self.y = y
        self.sprite = Sprite(char, color)
        self.name = name
        self.blocks_passage = blocks_passage
        self.blocks_light = blocks_light

        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

        self.status = status
        if self.status:
            self.status.owner = self

    def draw(self, console):
        self.sprite.draw(console, self.x, self.y)

    def clear(self, console):
        libtcod.console_put_char(console, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def distance_to(self, piece):
        dx = piece.x - self.x
        dy = piece.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

class PieceFactory:
    """The PieceFactory takes a string describing the piece it should make, wall, orc etc and then
    returns a Piece with those paramaters."""
    def __init__(self, board):
        self.board = board

    def createPiece(self, identifier, x=0, y=0):
        if identifier == 'wall':
            return Piece(self.board, x, y, '#', libtcod.white, 'Wall', blocks_passage=True, blocks_light=True, status=Status())
        elif identifier == 'floor':
            return Piece(self.board, x, y, '.', libtcod.white, 'Floor', blocks_passage=False, blocks_light=False, status=Status())
        elif identifier == 'down_stairs':
            return Piece(self.board, x, y, '>', libtcod.white, 'Down Stairs', blocks_passage=False, blocks_light=False, status=Status())
        elif identifier == 'empty':
            return Piece(self.board, x, y, ' ', libtcod.white, '', blocks_passage=False, blocks_light=False)
        elif identifier == 'player':
            fighter = Fighter(hp=5, power=1, death_function=player_death)
            return Piece(self.board, x, y, '@', libtcod.white, "Hero", blocks_passage=True, blocks_light=False, fighter=fighter, ai=PlayerAI(), status=Status())
        elif identifier == 'orc':
            fighter = Fighter(hp=1, power=1, death_function=monster_death)
            return Piece(self.board, x, y, 'o', libtcod.green, "Orc", blocks_passage=True, blocks_light=False, fighter=fighter, ai=BasicMonster(), status=Status())
        else:
            return None

def monster_death(monster):
    death_message = "The " + monster.name + " dies!"
    monster.board.game.message_system.add_message(death_message)
    monster.blocks_passage = False
    monster.sprite = Sprite('%', libtcod.red)
    monster.ai = None
    monster.fighter = None
    monster.board.game.remove_actor(monster)
    monster.name = monster.name + " corpse"
    monster.board.move_to_back(monster)

def player_death(player):
    death_message = "The Hero dies! Game Over!"
    player.board.game.message_system.add_message(death_message)
    player.blocks_passage = False
    player.sprite = Sprite('@', libtcod.red)
    player.fighter = None
    player.name = "Hero's corpse"
    player.board.move_to_back(player)
    player.board.game.game_state = "game_over"

def wall_destruction(piece):
    piece.blocks_passage = False
    piece.blocks_light = False
    piece.sprite = Sprite('.', libtcod.white)
    piece.fighter = None
    piece.ai = None

class Fighter:
    """This class contains all the data and methods needed for a piece to fight."""
    def __init__(self, hp, power, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.power = power
        self.death_function = death_function

    def take_damage(self, amount):
        if self.hp > amount:
            self.hp -= amount
        else:
            if self.death_function:
                self.death_function(self.owner)

class Status:
    """This class contains status flags such as on_fire or frozen."""
    def __init__(self):
        self.frozen = False

class PlayerAI:
    """The AI representing the player, stores a buffer with the players"""
    def __init__(self):
        self.action = None

    def take_turn(self):
        temp = self.action
        self.action = None
        return temp

    def set_action(self, action):
        self.action = action

class BasicMonster:
    """The AI for a basic monster"""
    def take_turn(self):
        player = self.owner.board.player
        dx = player.x - self.owner.x
        dy = player.y - self.owner.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        x = self.owner.x + int(round(dx / distance))
        y = self.owner.y + int(round(dy / distance))

        move_action = game_engine.MoveAction(self.owner, x, y)
        wait_action = game_engine.WaitAction(self.owner)

        if distance < 5:
            if move_action.isValid()[0]:
                return move_action
            else:
                return wait_action
        else:
            return wait_action

class StatusAffectedMonster:
    """AI code that takes status effects into account"""
    def take_turn(self):
        if self.owner.status and not self.owner.status.frozen:
            if self.owner.distance_to(self.owner.board.player) < 5:
                self.owner.move_towards(self.owner.board.player)
