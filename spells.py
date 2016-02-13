import dungeon

class Spell(object):
    """represents a spell made up of a caster, target and effect"""
    def __init__(self, caster, target_function, effect_function, board):
        self.caster = caster
        self.target_function = target_function
        self.effect_function = effect_function
        self.board = board

    def cast(self, **kwargs):
        target = self.target_function(self.caster, kwargs)
        self.effect_function(target)


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
            return caster

    return closest_monster

def self_target(caster, kwargs):
    return caster

def hurt(target):
    print "Hurting the " + target.name
    if target.fighter:
        target.fighter.takeDamage(1)
