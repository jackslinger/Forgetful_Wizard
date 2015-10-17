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

    def move(self, dx, dy):
        #move by the given amount
        self.x += dx
        self.y += dy

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
    """The Map represents one floor of the dungeon and owns all of the objects
    on that floor. It draws it's self and delegates drawing to objects"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[Tile('.', libtcod.white, False, False)
            for y in range(self.height)]
                for x in range(self.width)]
        self.pieces = []

    def draw(self, console):
        #The Map first draws all of the tiles, then any items, then the player and monsters
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[x][y].draw(console, x, y)

        for piece in self.pieces:
            piece.draw(console)

    def addPiece(self, piece):
        self.pieces.append(piece)
