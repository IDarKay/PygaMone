from typing import Callable, Optional
from uuid import UUID

import utils
from pokemon import abilitys


class Move(object):

    def __init__(self, move: 'abilitys.AbstractAbility', launcher: UUID, targets: dict[UUID, int]):
        self.__move: 'abilitys.AbstractAbility' = utils.check_not_null(move)
        self.__launcher: UUID = utils.check_not_null(launcher)
        self.__targets: dict[UUID, int] = utils.check_not_null(targets)

    def get_move(self) -> 'abilitys.AbstractAbility':
        return self.__move

    def get_launcher(self) -> UUID:
        return self.__launcher

    def get_targets(self) -> dict[UUID, int]:
        return self.__targets

    def have_target(self, uuid: UUID) -> bool:
        return uuid in self.__targets

    def get_damage_on(self, uuid: UUID) -> int:
        return self.__targets.get(uuid, 0)

    def __str__(self):
        return f'move: {self.__move.id_}, launcher: {self.__launcher}, targets: {([f"{k} => {v}" for k, v in self.__targets.items()])}'


class Turn(object):

    def __init__(self):
        self.move: list[Move] = []

    def add_move(self, move: Move):
        self.move.append(utils.check_not_null(move))

    def get_damage_on(self, uuid: UUID, filter_: Optional[Callable[[Move], bool]]) -> int:
        return sum(map(lambda mo: mo.get_damage_on(uuid) if filter_ is None or filter_(mo) else False, self.move))

    def __str__(self):
        return str(list(map(str, self.move)))


class BattleHistory(object):

    def __init__(self):
        self.turn: list[Turn] = []

    def add_move(self, turn: int, move: Move):
        if len(self.turn) > turn:
            tr = self.turn[turn]
            if tr is None:
                tr = Turn()
                self.turn[turn] = tr
        else:
            tr = Turn()
            self.turn.insert(turn, tr)
        tr.add_move(move)

    def get_damage_on(self, turn: int, uuid: UUID, filter_: Optional[Callable[[Move], bool]]=None) -> int:
        if len(self.turn) > turn:
            tr = self.turn[turn]
            if tr is None:
                return 0
            return tr.get_damage_on(uuid, filter_)
        return 0

    def __str__(self):
        return str(list(map(str, self.turn)))
