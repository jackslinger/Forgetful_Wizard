import libtcodpy as libtcod
from itertools import cycle
from game_engine import *
import game_piece

class Map:
    """The Map represents the floor and walls of the dungeon."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [[game_piece.Piece(self, x, y, ' ', libtcod.white, "", blocks_passage=False, blocks_light=False)
            for y in range(self.height)]
                for x in range(self.width)]

    def draw(self, console):
        #The Map draws all of the tiles.
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[x][y].draw(console)

    def carve_room(self, start_x, start_y, width, height):
        end_x = start_x + width - 1
        end_y = start_y + height - 1
        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                if x == start_x or y == start_y or x == end_x or y == end_y:
                    self.tiles[x][y] = game_piece.Piece(self, x, y, '#', libtcod.white, "wall", blocks_passage=True, blocks_light=True, status=game_piece.Status())
                else:
                    self.tiles[x][y] = game_piece.Piece(self, x, y, '.', libtcod.white, "floor", blocks_passage=False, blocks_light=False, status=game_piece.Status())

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
                self.tiles[x][y] = game_piece.Piece(self, x, y, '.', libtcod.white, "floor", False, False)

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

    def draw(self, console):
        #Draw the map
        self.map.draw(console)

        #Draw the pieces
        for piece in self.pieces:
            piece.draw(console)

    def generate(self):
        self.map.generate()
        player_fighter = game_piece.Fighter(hp=5, power=1, death_function=game_piece.player_death)
        player_ai = game_piece.PlayerAI()
        self.player = game_piece.Piece(self, self.width/2, (self.height/2)+4, '@', libtcod.white, "Hero", blocks_passage=True, blocks_light=False, fighter=player_fighter,
                            ai=player_ai, status=game_piece.Status())
        self.pieces = [self.player]
        self.game.add_actor(self.player)
        orc_fighter = game_piece.Fighter(hp=1, power=1, death_function=game_piece.monster_death)
        orc_ai = game_piece.BasicMonster()
        orc_status = game_piece.Status()
        orc = game_piece.Piece(self, 5, 5, 'o', libtcod.green, "Orc", blocks_passage=True, blocks_light=False, fighter=orc_fighter, ai=orc_ai, status=orc_status)
        self.pieces.append(orc)
        self.game.add_actor(orc)
        troll_fighter = game_piece.Fighter(hp=2, power=1, death_function=game_piece.monster_death)
        troll_ai = game_piece.BasicMonster()
        troll = game_piece.Piece(self, 35, (self.height/2)+4, 'T', libtcod.green, "Troll", blocks_passage=True, blocks_light=False, fighter=troll_fighter, ai=troll_ai)
        self.pieces.append(troll)
        self.game.add_actor(troll)

    def move_to_back(self, piece):
        #Move a piece to the start of the list so they are drawn first
        self.pieces.remove(piece)
        self.pieces.insert(0, piece)

    def pieces_at(self, x, y):
        found_pieces = []

        #Add the map tile at the given location
        found_pieces.append(self.map.tiles[x][y])

        #Add any other pieces at the given location
        for piece in self.pieces:
            if piece.x == x and piece.y == y:
                found_pieces.append(piece)

        #Return all the pieces found
        return found_pieces

    def is_blocked(self, x, y):
        #Is the tile at this location blocking
        if self.map.tiles[x][y].blocks_passage:
            #Set the blocking_piece, and break out of the loop
            blocking_piece = self.map.tiles[x][y]
            return blocking_piece

        #Are any blocking pieces in this location
        blocking_piece = None
        for piece in self.pieces:
            if piece.blocks_passage and piece.x == x and piece.y == y:
                #Set the blocking_piece, and break out of the loop
                blocking_piece = piece
                return blocking_piece

        #If it's not blocked by a tile or piece then it's not blocked
        return False
