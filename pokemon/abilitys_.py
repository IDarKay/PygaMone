from typing import TypeVar, Dict, NoReturn
import pokemon.abilitys as abilitys
from inspect import isclass

ABILITYS: Dict[str, 'abilitys.AbstractAbility'] = {}

T = TypeVar('T', )


def register(it: T) -> T:

    if it.id_ in ABILITYS:
        raise ValueError("duplicate key in items registry {}".format(it.id_))

    ABILITYS[it.id_] = it
    return it


def load() -> NoReturn:
    for attribute_name in dir(abilitys):
        attribute = getattr(abilitys, attribute_name)
        if isclass(attribute) and issubclass(attribute, abilitys.AbstractAbility) and attribute != abilitys.AbstractAbility:
            register(attribute())
