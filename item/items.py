from typing import TypeVar, Dict, NoReturn
import item.pokeball as pokeball
import item.potion as potion
import item.item as item
import item.revive as revive

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
MASTER_BALL: 'pokeball.MasterBall' = register(pokeball.MasterBall())

POTION: 'potion.Potion' = register(potion.Potion("potion", "potion", 20))
SUPER_POTION: 'potion.Potion' = register(potion.Potion("super_potion", "super-potion", 50))
HYPER_POTION: 'potion.Potion' = register(potion.Potion("hyper_potion", "hyper-potion", 200))
MAX_POTION: 'potion.MaxPotion' = register(potion.MaxPotion())

REVIVE: 'revive.Revive' = register(revive.Revive("revive", "revive", 0.5))
MAX_REVIVE: 'revive.Revive' = register(revive.Revive("max_revive", "max-revive", 1))

# del pokeball.POKE_BALL_IMAGE


def load() -> NoReturn:
    print(ITEMS)
