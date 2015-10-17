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
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.sprite = Sprite(char, color)

    def draw(self, console):
        self.sprite.draw(console, self.x, self.y)
        #Delegate the task of drawing to the sprite

    def clear(self, console):
        #erase the character that represents this object
        libtcod.console_put_char(console, self.x, self.y, ' ', libtcod.BKGND_NONE)

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

    def generate(self):
        self.carve_room(38, 23, 5, 5)

class Board(object):
    """The Board represents one whole floor of the dungeon with a map, and objects.
    It also contains the logic for moving around and fighting."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = Map(width, height)
        self.map.generate()
        self.player = Piece(self.width/2, self.height/2, '@', libtcod.white)
        self.pieces = [self.player]

    def draw(self, console):
        #Draw the map, then draw the objects
        self.map.draw(console)
        for piece in self.pieces:
            piece.draw(console)

    def move(self, piece, dx, dy):
        #Move by the given amount
        new_x = piece.x + dx
        new_y = piece.y + dy

        if not self.map.tiles[new_x][new_y].blocks_passage:
            piece.x = new_x
            piece.y = new_y
