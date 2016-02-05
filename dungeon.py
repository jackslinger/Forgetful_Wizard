import libtcodpy as libtcod
import math
import textwrap

class Game():
    """Stores the current game state. Maybe should be a singleton"""
    def __init__(self, message_system):
        self.game_state = "playing"
        self.message_system = message_system

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

class Sprite(object):
    """A Sprite represents a colored char that can draw it's self at a given position"""
    def __init__(self, char, color):
        super(Sprite, self).__init__()
        self.char = char
        self.color = color

    def draw(self, console, x, y):
        #set the color and then draw the character that represents this object at its position
        libtcod.console_set_default_foreground(console, self.color)
        libtcod.console_put_char(console, x, y, self.char, libtcod.BKGND_NONE)

class Piece:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    #it is placed on a particular board object
    def __init__(self, board, x, y, char, color, name, blocks_passage=False, fighter=None, ai=None):
        self.board = board
        self.x = x
        self.y = y
        self.sprite = Sprite(char, color)
        self.name = name
        self.blocks_passage = blocks_passage

        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self

        self.ai = ai
        if self.ai:
            self.ai.owner = self

    def draw(self, console):
        self.sprite.draw(console, self.x, self.y)
        #Delegate the task of drawing to the sprite

    def clear(self, console):
        #erase the character that represents this object
        libtcod.console_put_char(console, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def distance_to(self, piece):
        dx = piece.x - self.x
        dy = piece.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def move_towards(self, piece):
        dx = piece.x - self.x
        dy = piece.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.board.move_or_attack(self, dx, dy)


def monster_death(monster):
    print "The " + monster.name + " dies!"
    monster.blocks_passage = False
    monster.sprite = Sprite('%', libtcod.red)
    monster.ai = None
    monster.fighter = None
    monster.name = monster.name + " corpse"
    monster.board.move_to_back(monster)

def player_death(player):
    print "The Hero dies! Game Over!"
    player.blocks_passage = False
    player.sprite = Sprite('@', libtcod.red)
    player.fighter = None
    player.name = "Hero's corpse"
    player.board.move_to_back(player)
    player.board.game.game_state = "game_over"

class Fighter:
    #This class contains all the data and methods needed for a piece to fight.
    def __init__(self, hp, power, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.power = power
        self.death_function = death_function

    def takeDamage(self, amount):
        if self.hp > amount:
            self.hp -= amount
        else:
            if self.death_function:
                self.death_function(self.owner)

class BasicMonster:
    """The AI for a basic monster"""
    def take_turn(self):
        if self.owner.distance_to(self.owner.board.player) < 5:
            self.owner.move_towards(self.owner.board.player)

class Tile:
    """A Tile represents a part of the map, it can block light and or passage"""
    def __init__(self, char, color, blocks_passage, blocks_light):
        self.sprite = Sprite(char, color)
        self.blocks_light = blocks_light
        self.blocks_passage = blocks_passage

    def draw(self, console, x, y):
        #Delegate the task of drawing to the sprite
        self.sprite.draw(console, x, y)

class Map:
    """The Map represents the floor and walls of the dungeon."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[Tile(' ', libtcod.white, True, True)
            for y in range(self.height)]
                for x in range(self.width)]

    def draw(self, console):
        #The Map draws all of the tiles.
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[x][y].draw(console, x, y)

    def carve_room(self, start_x, start_y, width, height):
        end_x = start_x + width - 1
        end_y = start_y + height - 1
        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                if x == start_x or y == start_y or x == end_x or y == end_y:
                    self.tiles[x][y] = Tile('#', libtcod.white, True, True)
                else:
                    self.tiles[x][y] = Tile('.', libtcod.white, False, False)

    def carve_corridor(self, start_x, start_y, end_x, end_y):
        if end_x < start_x:
            temp = start_x
            start_x = end_x
            end_x = temp
        if end_y < start_y:
            temp = start_y
            start_y = end_y
            end_y = temp

        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                self.tiles[x][y] = Tile(',', libtcod.white, False, False)

    def generate(self):
        self.carve_room(38, 23, 5, 5)
        self.carve_room(3, 4, 30, 26)
        self.carve_room(35, 10, 20, 10)

        #Corridoors
        self.carve_corridor(32, 15, 35, 15)
        self.carve_corridor(32, 25, 38, 25)

class Board(object):
    """The Board represents one whole floor of the dungeon with a map, and objects.
    It also contains the logic for moving around and fighting."""
    def __init__(self, width, height, game):
        self.width = width
        self.height = height
        self.game = game
        self.map = Map(width, height)
        player_fighter = Fighter(hp=5, power=1, death_function=player_death)
        self.player = Piece(self, self.width/2, (self.height/2)+4, '@', libtcod.white, "Hero", blocks_passage=True, fighter=player_fighter)
        self.pieces = [self.player]

    def draw(self, console):
        #Draw the map
        self.map.draw(console)

        #Draw the pieces
        for piece in self.pieces:
            piece.draw(console)

    def generate(self):
        self.map.generate()
        orc_fighter = Fighter(hp=1, power=1, death_function=monster_death)
        orc_ai = BasicMonster()
        self.pieces.append(Piece(self, 5, 5, 'o', libtcod.green, "Orc", True, orc_fighter, orc_ai))
        troll_fighter = Fighter(hp=2, power=1, death_function=monster_death)
        troll_ai = BasicMonster()
        self.pieces.append(Piece(self, 35, (self.height/2)+4, 'T', libtcod.green, "Troll", True, troll_fighter, troll_ai))

    def move_to_back(self, piece):
        #Move a piece to the start of the list so they are drawn first
        self.pieces.remove(piece)
        self.pieces.insert(0, piece)

    def is_blocked(self, x, y):
        #Is the tile at this location blocking
        if self.map.tiles[x][y].blocks_passage:
            return True

        #Are any blocking pieces in this location
        blocking_piece = None
        for piece in self.pieces:
            if piece.blocks_passage and piece.x == x and piece.y == y:
                #Set the blocking_piece, and break out of the loop
                blocking_piece = piece
                return blocking_piece

        #If it's not blocked by a tile or piece then it's not blocked
        return False

    def move_or_attack(self, piece, dx, dy):
        #Get the co-ordinates of the destination
        new_x = piece.x + dx
        new_y = piece.y + dy

        #Check if the destination is blocked by a piece
        blocking_piece = self.is_blocked(new_x, new_y)

        #If blocked by something
        if blocking_piece:
            #If blocked by a piece
            if isinstance(blocking_piece, Piece):
                #Attack the piece if possible
                if (blocking_piece.fighter and piece.fighter):
                    text = "The " + piece.name + " attacks the " + blocking_piece.name + "!"
                    self.game.message_system.add_message(text)
                    blocking_piece.fighter.takeDamage(piece.fighter.power)
                    return True
                else:
                    #Moving has failed, should not take up a turn
                    tet = "The " + piece.name + " bumps into the " + blocking_piece.name
                    self.game.message_system.add_message(text)
                    return False
            else:
                #Moving into a wall or other obstruction should not take a turn
                text = "The " + piece.name + " bumps into the wall."
                self.game.message_system.add_message(text)
                return False
        else:
            #Move to the destination
            piece.x = new_x
            piece.y = new_y
            return True

class Spell(object):
    """represents a spell made up of a caster, target and effect"""
    def __init__(self, caster, target_function, effect_function, board):
        self.caster = caster
        self.target_function = target_function
        self.effect_function = effect_function
        self.board = board

    def cast(self):
        target = self.target_function(self.caster, self.board)
        self.effect_function(target)


def zap_target(caster, board):
    x = caster.x
    y = caster.y

    closest_monster = caster
    min_distance = 0
    for piece in board.pieces:
        if piece.fighter:
            distance = caster.distance_to(piece)
            if distance < min_distance or min_distance == 0:
                min_distance = distance
                closest_monster = piece

    return closest_monster

def hurt(target):
    print "Hurting the " + target.name
    if target.fighter:
        target.fighter.takeDamage(1)
