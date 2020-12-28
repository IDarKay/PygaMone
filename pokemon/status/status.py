from typing import TypeVar, Dict, NoReturn, Optional
import pokemon.status.pokemon_status as pst

STATUS: Dict[str, 'pst.Status'] = {}

T = TypeVar('T', )


def register(it: T) -> T:

    if it.id_ in STATUS:
        raise ValueError("duplicate key in items registry {}".format(it.id_))

    STATUS[it.id_] = it
    return it


BURN: Optional['pst.BurnStatus'] = None
FLINCH: Optional['pst.FlinchingStatus'] = None


def load() -> NoReturn:
    global BURN, FLINCH
    BURN = register(pst.BurnStatus("burn"))
    FLINCH = register(pst.FlinchingStatus("flinch"))
    print(STATUS)
