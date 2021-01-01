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
FREEZE: Optional['pst.FreezeStatus'] = None
PARALYSIS: Optional['pst.ParalysisStatus'] = None
FLINCH: Optional['pst.FlinchingStatus'] = None


def load() -> NoReturn:
    global BURN, FLINCH, FREEZE, PARALYSIS
    BURN = register(pst.BurnStatus("burn"))
    FREEZE = register(pst.FreezeStatus("freeze"))
    PARALYSIS = register(pst.ParalysisStatus("paralysis"))
    FLINCH = register(pst.FlinchingStatus("flinch"))
    print(STATUS)
