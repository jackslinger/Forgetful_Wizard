import libtcodpy as libtcod
from itertools import cycle
from game_engine import *
import game_piece
import random
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

class Room:
    """The representation of a room for use in dungeon genration"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center_x = x + width / 2
        self.center_y = y + height / 2

    def distance_to(self, other):
        return abs(self.center_x - other.center_x) + abs(self.center_y - other.center_y)

class Map:
    """The Map represents the floor and walls of the dungeon."""
    def __init__(self, board, width, height):
        self.width = width
        self.height = height
        self.board = board
        self.tiles = [[self.board.factory.createPiece('empty', x, y) for y in range(self.height)] for x in range(self.width)]

    def draw(self, console):
        #The Map draws all of the tiles.
        libtcod.console_set_default_foreground(console, libtcod.white)

        for y in range(self.height):
            row = ''
            for x in range(self.width):
                char = self.tiles[x][y].sprite.char
                color = self.tiles[x][y].sprite.color
                rgb = (color.r, color.g, color.b)
                row += ('%c%c%c%c%c%c%c%c%c%c' % ((libtcod.COLCTRL_FORE_RGB, ) + rgb + (libtcod.COLCTRL_BACK_RGB, ) + (1,1,1) + (char, libtcod.COLCTRL_STOP)))
            libtcod.console_print(console, 0, y, row)

    def carve_room(self, start_x, start_y, width, height):
        end_x = start_x + width - 1
        end_y = start_y + height - 1
        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                if x == start_x or y == start_y or x == end_x or y == end_y:
                    self.tiles[x][y] = self.board.factory.createPiece('wall', x, y)
                else:
                    self.tiles[x][y] = self.board.factory.createPiece('floor', x, y)

    def carve_corridor_rooms(self, left_room, right_room, horizontal):
        if horizontal:
            left_max_x = left_room.x + left_room.width
            right_max_x = right_room.x + right_room.width
            min_x = max(left_room.x, right_room.x)
            max_x = min(left_max_x, right_max_x)
            x = random.randint(min_x + 1, max_x - 2)
            for y in range(left_room.y + left_room.height - 1, left_room.y - 1, -1):
                if not self.tiles[x][y].blocks_passage:
                    start_y = y
                    break
            for y in range(right_room.y, right_room.y + right_room.height - 1):
                if not self.tiles[x][y].blocks_passage:
                    end_y = y
                    break
            self.carve_corridor(x, start_y, x, end_y)
        else:
            left_max_y = left_room.y + left_room.height
            right_max_y = right_room.y + right_room.height
            min_y = max(left_room.y, right_room.y)
            max_y = min(left_max_y, right_max_y)
            y = random.randint(min_y + 1, max_y - 2)
            for x in range(left_room.x + left_room.width - 1, left_room.x - 1, -1):
                if not self.tiles[x][y].blocks_passage:
                    start_x = x
                    break
            for x in range(right_room.x, right_room.x + right_room.width - 1):
                if not self.tiles[x][y].blocks_passage:
                    end_x = x
                    break
            self.carve_corridor(start_x, y, end_x, y)

    def carve_corridor(self, start_x, start_y, end_x, end_y):
        if end_x < start_x:
            temp = start_x
            start_x = end_x
            end_x = temp
        if end_y < start_y:
            temp = start_y
            start_y = end_y
            end_y = temp

        for x in range(start_x, end_x + 1):
            self.tiles[x][end_y] = self.board.factory.createPiece('floor', x, end_y)
            if self.tiles[x][end_y + 1].sprite.char == ' ':
                self.tiles[x][end_y + 1] = self.board.factory.createPiece('wall', x, end_y + 1)
            if self.tiles[x][end_y - 1].sprite.char == ' ':
                self.tiles[x][end_y - 1] = self.board.factory.createPiece('wall', x, end_y - 1)

        for y in range(start_y, end_y + 1):
            self.tiles[end_x][y] = self.board.factory.createPiece('floor', end_x, y)
            if self.tiles[end_x + 1][y].sprite.char == ' ':
                self.tiles[end_x + 1][y] = self.board.factory.createPiece('wall', end_x + 1, y)
            if self.tiles[end_x - 1][y].sprite.char == ' ':
                self.tiles[end_x - 1][y] = self.board.factory.createPiece('wall', end_x - 1, y)

    def generate(self):
        self.tiles = [[self.board.factory.createPiece('empty', x, y) for y in range(self.height)] for x in range(self.width)]
        
        bsp_root = libtcod.bsp_new_with_size(0, 0, self.width, self.height)
        libtcod.bsp_split_recursive(bsp_root, None, 8, minHSize=11, minVSize=11, maxHRatio=1.0, maxVRatio=1.0)

        rooms = []
        self.process_node(bsp_root, rooms)

        for room in rooms:
            self.carve_room(room.x, room.y, room.width, room.height)

        full_graph = csr_matrix([[room1.distance_to(room2) for room1 in rooms] for room2 in rooms])
        minimum_spanning_graph = minimum_spanning_tree(full_graph)
        indexes = minimum_spanning_graph.nonzero()

        for i in range(len(indexes[0])):
            room1 = rooms[indexes[0][i]]
            room2 = rooms[indexes[1][i]]
            self.carve_corridor(room1.center_x, room1.center_y, room2.center_x, room1.center_y)
            self.carve_corridor(room2.center_x, room1.center_y, room2.center_x, room2.center_y)

        return rooms

    def process_node(self, node, rooms):
        if libtcod.bsp_is_leaf(node):
            width = random.randint(7, node.w)
            height = random.randint(7, node.h)
            x = random.randint(node.x, node.x+node.w-width)
            y = random.randint(node.y, node.y+node.h-height)
            rooms.append(Room(x, y, width, height))
        else:
            self.process_node(libtcod.bsp_left(node), rooms)
            self.process_node(libtcod.bsp_right(node), rooms)

class Board(object):
    """The Board represents one whole floor of the dungeon with a map, and a list of moving peices.
    It also contains the logic for moving around and fighting."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.factory = game_piece.PieceFactory(self)
        self.map = Map(self, width, height)
        self.player = self.factory.createPiece('player')

    def draw(self, console):
        self.map.draw(console)

        for piece in self.pieces:
            piece.draw(console)

    def generate(self):
        rooms = self.map.generate()

        for i in range(len(rooms)):
            if i == 0:
                self.player.x = rooms[i].center_x
                self.player.y = rooms[i].center_y
                self.pieces = [self.player]
                self.game.add_actor(self.player)
            elif i == 1:
                x = rooms[i].center_x
                y = rooms[i].center_y
                self.map.tiles[x][y] = self.factory.createPiece('down_stairs', x, y)
            else:
                orc = self.factory.createPiece('orc', rooms[i].center_x, rooms[i].center_y)
                self.pieces.append(orc)
                self.game.add_actor(orc)

    def move_to_back(self, piece):
        #Move a piece to the start of the list so they are drawn first
        self.pieces.remove(piece)
        self.pieces.insert(0, piece)

    def pieces_at(self, x, y):
        found_pieces = []
        found_pieces.append(self.map.tiles[x][y])

        for piece in self.pieces:
            if piece.x == x and piece.y == y:
                found_pieces.append(piece)

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
