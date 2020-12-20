from typing import TypeVar, Dict, NoReturn
import pokemon.abilitys as abilitys

ABILITYS: Dict[str, 'abilitys.AbstractAbility'] = {}

T = TypeVar('T', )


def register(it: T) -> T:

    if it.id_ in ABILITYS:
        raise ValueError("duplicate key in items registry {}".format(it.id_))

    ABILITYS[it.id_] = it
    return it


# EMBER: 'abilitys.EmberAbility' =
# TACKLE: 'abilitys.TackleAbility' =


def load() -> NoReturn:
    register(abilitys.EmberAbility())
    register(abilitys.TackleAbility())
    register(abilitys.AcidAbility())
