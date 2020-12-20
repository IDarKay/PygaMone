from typing import TypeVar, Dict, NoReturn
import pokemon.status.pokemon_status as pst

STATUS: Dict[str, 'pst.Status'] = {}

T = TypeVar('T', )


def register(it: T) -> T:

    if it.id_ in STATUS:
        raise ValueError("duplicate key in items registry {}".format(it.id_))

    STATUS[it.id_] = it
    return it


BURN: 'pst.BurnStatus' = register(pst.BurnStatus("burn"))


def load() -> NoReturn:
    # BURN: 'pst.BurnStatus'
    print(STATUS)
