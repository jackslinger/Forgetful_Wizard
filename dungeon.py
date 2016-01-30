import libtcodpy as libtcod

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
    def __init__(self, x, y, char, color, name, blocks_passage=False, fighter=None, ai=None):
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

def monster_death(monster):
    print "The " + monster.name + " dies!"
    monster.blocks_passage = False
    monster.sprite = Sprite('%', libtcod.red)
    monster.ai = None
    monster.fighter = None
    monster.name = monster.name + " corpse"

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
        print "The " + self.owner.name + " growls!"

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
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = Map(width, height)
        player_fighter = Fighter(hp=5, power=1)
        self.player = Piece(self.width/2, self.height/2, '@', libtcod.white, "Hero", blocks_passage=True, fighter=player_fighter)
        self.pieces = [self.player]

    def draw(self, console):
        #Draw the map, then draw the objects
        self.map.draw(console)
        for piece in self.pieces:
            piece.draw(console)

    def generate(self):
        self.map.generate()
        orc_fighter = Fighter(hp=1, power=1, death_function=monster_death)
        orc_ai = BasicMonster()
        self.pieces.append(Piece(5, 5, 'o', libtcod.green, "Orc", True, orc_fighter, orc_ai))
        troll_fighter = Fighter(hp=2, power=1, death_function=monster_death)
        troll_ai = BasicMonster()
        self.pieces.append(Piece(35, self.height/2, 'T', libtcod.green, "Troll", True, troll_fighter, troll_ai))


    def move_or_attack(self, piece, dx, dy):
        #Get the co-ordinates of the destination
        new_x = piece.x + dx
        new_y = piece.y + dy

        #Check if the destination is blocked by a piece
        blocking_piece = None
        for other in self.pieces:
            if other.blocks_passage and other.x == new_x and other.y == new_y:
                #Set the blocking piece, if more than one the last one will be picked
                blocking_piece = other

        #If blocked by a piece
        if (blocking_piece != None):
            #Attack the piece if possible
            if (blocking_piece.fighter and piece.fighter):
                print "The " + piece.name + " attacks the " + blocking_piece.name + "!"
                blocking_piece.fighter.takeDamage(piece.fighter.power)
            else:
                #Moving has failed, should not take up a turn
                print "The " + piece.name + " bumps into the " + blocking_piece.name
        elif not (self.map.tiles[new_x][new_y].blocks_passage):
            #Move to the destination
            piece.x = new_x
            piece.y = new_y
