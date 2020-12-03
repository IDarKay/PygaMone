from item.pokeball import *
import item.item as item

ITEMS = {}

def register(item):

    if item._id in ITEMS:
        raise ValueError("duplicate key in items registry {}".format(item._id))

    ITEMS[item._id] = item
    return item


POKE_BALL = register(Pokeball("poke_ball", get_pokeball(2, 0, 52, 50), 1))
GREAT_BALL = register(Pokeball("great_ball", get_pokeball(64, 0, 114, 50), 1))
ULTRA_BALL = register(Pokeball("ultra_ball", get_pokeball(126, 0, 176, 50), 1))
MASTER_BALL = register(MasterBall())
del POKE_BALL_IMAGE




def load():
    print(ITEMS)
