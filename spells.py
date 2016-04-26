import libtcodpy as libtcod
import game_piece
import random

class Spell(object):
    """represents a spell made up of a caster, target or targets and effect"""
    def __init__(self, caster, target_function, effect_function, **kwargs):
        self.caster = caster
        self.target_function = target_function
        self.effect_function = effect_function
        self.kwargs = kwargs

    def cast(self):
        targets = self.target_function(self.caster, self.kwargs)
        for target in targets:
            self.effect_function(target, self.kwargs)

def random_spell(caster):
    target_functions = [zap_target, random_adjacent_target, burst_target, self_target]
    effect_functions = [hurt, freeze, growth]

    target = random.choice(target_functions)
    effect = random.choice(effect_functions)
    return Spell(caster, target, effect)

def zap_target(caster, kwargs):
    board = caster.board
    x = caster.x
    y = caster.y

    max_range = None
    if 'max_range' in kwargs:
        max_range = kwargs['max_range']

    closest_monster = caster
    min_distance = 0
    for piece in board.pieces:
        if piece.fighter:
            distance = caster.distance_to(piece)
            if distance < min_distance or min_distance == 0:
                min_distance = distance
                closest_monster = piece

    if max_range:
        if min_distance > max_range:
            return [caster]

    return [closest_monster]

def random_adjacent_target(caster, kwargs):
    board = caster.board

    targets = []
    for x in range(caster.x - 1, caster.x + 2):
        for y in range(caster.y - 1, caster.y + 2):
            if not (caster.x == x and caster.y == y):
                #Get all the pieces at a location
                found_pieces = board.pieces_at(x, y)
                for piece in found_pieces:
                    targets.append(piece)

    #Shuffle the list of posible targets and select the first one
    random.shuffle(targets)
    return [targets[0]]

def burst_target(caster, kwargs):
    board = caster.board

    targets = []
    for x in range(caster.x - 1, caster.x + 2):
        for y in range(caster.y - 1, caster.y + 2):
            if not (caster.x == x and caster.y == y):
                #Get all the pieces at a location
                found_pieces = board.pieces_at(x, y)
                for piece in found_pieces:
                    targets.append(piece)

    return targets

def self_target(caster, kwargs):
    return [caster]

def hurt(target, kwargs):
    damage = 1
    if 'damage' in kwargs:
        max_range = kwargs['damage']

    if target.fighter:
        target.fighter.take_damage(damage)

def freeze(target, kwargs):
    if target.status and not target.status.frozen:
        target.status.frozen = True
        target.name = "Frozen " + target.name
        target.sprite.color = libtcod.blue

def growth(target, kwargs):
    if not target.fighter and not target.ai:
        target.name = "Stunted Tree"
        target.sprite = game_piece.Sprite('#', libtcod.green)
        target.blocks_passage = True
        target.blocks_light = True
        fighter = game_piece.Fighter(hp=1, power=0, death_function=game_piece.wall_destruction)
        fighter.owner = target
        target.fighter = fighter
