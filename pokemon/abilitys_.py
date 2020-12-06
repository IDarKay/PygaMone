from typing import TypeVar, Dict, NoReturn
import pokemon.ability as ability

ABILITYS: Dict[str, 'ability.AbstractAbility'] = {}

T = TypeVar('T', )


def register(it: T) -> T:

    if it.id_ in ABILITYS:
        raise ValueError("duplicate key in items registry {}".format(it.id_))

    ABILITYS[it.id_] = it
    return it


EMBER: 'ability.EmberAbility' = register(ability.EmberAbility())
TACKLE: 'ability.TackleAbility' = register(ability.TackleAbility())


def load() -> NoReturn:
    print(ABILITYS)
