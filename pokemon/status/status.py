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
SLEEP: Optional['pst.SleepStatus'] = None
CONFUSE: Optional['pst.ParalysisStatus'] = None
FLINCH: Optional['pst.FlinchingStatus'] = None
CLAMP: Optional['pst.ClampStatus'] = None


def load() -> NoReturn:
    globals()["BURN"] = register(pst.BurnStatus("burn"))
    globals()["FREEZE"] = register(pst.FreezeStatus("freeze"))
    globals()["PARALYSIS"] = register(pst.ParalysisStatus("paralysis"))
    globals()["FLINCH"] = register(pst.FlinchingStatus("flinch"))
    globals()["CLAMP"] = register(pst.ClampStatus("clamp"))
    globals()["CONFUSE"] = register(pst.ConfuseStatus("confuse"))
    globals()["SLEEP"] = register(pst.SleepStatus("sleep"))
    print(STATUS)
