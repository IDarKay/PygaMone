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


POKE_BALL: 'pokeball.Pokeball' = register(pokeball.Pokeball("poke_ball", "poke-ball", 1))
GREAT_BALL: 'pokeball.Pokeball' = register(pokeball.Pokeball("great_ball", "great-ball", 1))
ULTRA_BALL: 'pokeball.Pokeball' = register(pokeball.Pokeball("ultra_ball", "ultra-ball", 1))
ULTRA_BALL2: 'pokeball.Pokeball' = register(pokeball.Pokeball("ultra_ball2", "ultra-ball", 1))
ULTRA_BALL3: 'pokeball.Pokeball' = register(pokeball.Pokeball("ultra_ball3", "ultra-ball", 1))
ULTRA_BALL4: 'pokeball.Pokeball' = register(pokeball.Pokeball("ultra_ball4", "ultra-ball", 1))
ULTRA_BALL5: 'pokeball.Pokeball' = register(pokeball.Pokeball("ultra_ball5", "ultra-ball", 1))
MASTER_BALL: 'pokeball.Pokeball' = register(pokeball.MasterBall())
# del pokeball.POKE_BALL_IMAGE


def load() -> NoReturn:
    print(ITEMS)
