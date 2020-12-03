from typing import TypeVar, Dict, NoReturn
import item.pokeball as pokeball
import item.item as item

ITEMS: Dict[str, 'item.Item'] = {}

T = TypeVar('T', )


def register(it: T) -> T:

    if it.identifier in ITEMS:
        raise ValueError("duplicate key in items registry {}".format(it.identifier))

    ITEMS[it.identifier] = it
    return it


POKE_BALL: 'pokeball.Pokeball' = register(pokeball.Pokeball("poke_ball", pokeball.get_pokeball(2, 0, 52, 50), 1))
GREAT_BALL: 'pokeball.Pokeball' = register(pokeball.Pokeball("great_ball", pokeball.get_pokeball(64, 0, 114, 50), 1))
ULTRA_BALL: 'pokeball.Pokeball' = register(pokeball.Pokeball("ultra_ball", pokeball.get_pokeball(126, 0, 176, 50), 1))
MASTER_BALL: 'pokeball.Pokeball' = register(pokeball.MasterBall())
del pokeball.POKE_BALL_IMAGE


def load() -> NoReturn:
    print(ITEMS)
