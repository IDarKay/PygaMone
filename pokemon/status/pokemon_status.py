from abc import abstractmethod
import random
from typing import Optional, NoReturn
import pokemon.player_pokemon as player_pokemon
import pokemon.battle.battle as battle
import pokemon.abilitys as ability
import pokemon.status.status_animations as animation
import pokemon.status.status as status_
import game
from pokemon import pokemon_type


class Status(object):

    def __init__(self, id_: str, permanent: bool):
        self.id_ = id_
        self.permanent = permanent

    def get_image(self, si: 'StatusInstance') -> Optional[tuple[str, tuple[int, int, int]]]:
        return None

    def get_apply_text(self, ally: bool) -> Optional[str]:
        return None

    def get_damage_text(self, ally: bool) -> Optional[str]:
        return None

    def get_end_text(self, ally: bool) -> Optional[str]:
        return None

    def get_cancel_text(self, ally: bool) -> Optional[str]:
        return None

    def get_animation(self, si: 'StatusInstance', pos: tuple[int, int]) -> Optional['battle.Animation']:
        return None

    def get_catch_edit(self):
        return 1

    @abstractmethod
    def apply(self, si: 'StatusInstance', turn: int) -> bool:
        '''
        @return: True if cancel apply else false
        '''
        pass

    @abstractmethod
    def turn(self, si: 'StatusInstance', turn: int) -> tuple[bool, int]:
        '''
        @return: tuple : [end, recoil]
        '''
        pass

    @abstractmethod
    def attack(self, si: 'StatusInstance', turn: int, ab: 'ability.AbstractAbility') -> tuple[bool, bool, int]:
        '''
        @return: tuple : [end, cancel, recoil]
        '''
        pass

    def __eq__(self, other):
        return isinstance(other, Status) and self.id_ == other.id_


class BurnStatus(Status):

    def __init__(self, id_: str):
        super().__init__(id_, True)

    def get_image(self, si: 'StatusInstance') -> Optional[tuple[str, tuple[int, int, int]]]:
        return game.game_instance.get_message("status.burn.image"), (240, 128, 48)

    def get_apply_text(self, ally: bool) -> Optional[str]:
        return f"status.burn.{'ally' if ally else 'enemy'}.apply"

    def get_damage_text(self, ally: bool) -> Optional[str]:
        return f"status.burn.{'ally' if ally else 'enemy'}.damage"

    def get_end_text(self, ally: bool) -> Optional[str]:
        return f"status.burn.{'ally' if ally else 'enemy'}.end"

    def get_cancel_text(self, ally: bool) -> Optional[str]:
        return f"status.burn.{'ally' if ally else 'enemy'}.cancel"

    def attack(self, si: 'StatusInstance', turn: int, ab: 'ability.AbstractAbility') -> tuple[bool, bool, int]:
        return False, False, 0

    def turn(self, si: 'StatusInstance', turn: int) -> tuple[bool, int]:
        return False, si.poke.get_max_heal() // 8

    def apply(self, si: 'StatusInstance', turn: int) -> NoReturn:
        return pokemon_type.FIRE not in si.poke.poke.types

    def get_catch_edit(self):
        return 1.5

    def get_animation(self, si: 'StatusInstance', pos: tuple[int, int]) -> Optional['battle.Animation']:
        return animation.BurnAnimation(pos)


class SleepStatus(Status):

    def __init__(self, id_: str):
        super().__init__(id_, True)

    def get_image(self, si: 'StatusInstance') -> Optional[tuple[str, tuple[int, int, int]]]:
        return game.game_instance.get_message("status.sleep.image"), (152, 216, 216)

    def get_apply_text(self, ally: bool) -> Optional[str]:
        return f"status.sleep.{'ally' if ally else 'enemy'}.apply"

    def get_damage_text(self, ally: bool) -> Optional[str]:
        return ""

    def get_end_text(self, ally: bool) -> Optional[str]:
        return f"status.sleep.{'ally' if ally else 'enemy'}.end"

    def get_cancel_text(self, ally: bool) -> Optional[str]:
        return f"status.sleep.{'ally' if ally else 'enemy'}.cancel"

    def attack(self, si: 'StatusInstance', turn: int, ab: 'ability.AbstractAbility') -> tuple[bool, bool, int]:
        n = si.poke.ram_data["sleep"]
        n -= 1
        si.poke.ram_data["sleep"] = n
        if n <= 0:
            del si.poke.ram_data["sleep"]
        return n <= 0, n > 0, 0

    @staticmethod
    def __get_nb_hit() -> int:
        r = random.random()
        if r <= (1/3):
            return 2
        if r <= (2/3):
            return 3
        if r <= (5/6):
            return 4
        return 5

    def turn(self, si: 'StatusInstance', turn: int) -> tuple[bool, int]:
        return False, 0

    def apply(self, si: 'StatusInstance', turn: int) -> NoReturn:
        si.poke.ram_data["sleep"] = SleepStatus.__get_nb_hit()
        return True

    def get_catch_edit(self):
        return 2

    # def get_animation(self, si: 'StatusInstance', pos: tuple[int, int]) -> Optional['battle.Animation']:
    #     return animation.BurnAnimation(pos)


class FreezeStatus(Status):

    def __init__(self, id_: str):
        super().__init__(id_, True)

    def get_image(self, si: 'StatusInstance') -> Optional[tuple[str, tuple[int, int, int]]]:
        return game.game_instance.get_message("status.freeze.image"), (152, 216, 216)

    def get_apply_text(self, ally: bool) -> Optional[str]:
        return f"status.freeze.{'ally' if ally else 'enemy'}.apply"

    def get_damage_text(self, ally: bool) -> Optional[str]:
        return f"status.freeze.{'ally' if ally else 'enemy'}.damage"

    def get_end_text(self, ally: bool) -> Optional[str]:
        return f"status.freeze.{'ally' if ally else 'enemy'}.end"

    def get_cancel_text(self, ally: bool) -> Optional[str]:
        return f"status.freeze.{'ally' if ally else 'enemy'}.cancel"

    def attack(self, si: 'StatusInstance', turn: int, ab: 'ability.AbstractAbility') -> tuple[bool, bool, int]:
        end = random.random() < 0.1
        return end, not end, 0

    def turn(self, si: 'StatusInstance', turn: int) -> tuple[bool, int]:
        return False, 0

    def apply(self, si: 'StatusInstance', turn: int) -> NoReturn:
        return pokemon_type.ICE not in si.poke.poke.types

    def get_catch_edit(self):
        return 2

    # def get_animation(self, si: 'StatusInstance', pos: tuple[int, int]) -> Optional['battle.Animation']:
    #     return animation.BurnAnimation(pos)


class ParalysisStatus(Status):

    def __init__(self, id_: str):
        super().__init__(id_, True)

    def get_image(self, si: 'StatusInstance') -> Optional[tuple[str, tuple[int, int, int]]]:
        return game.game_instance.get_message("status.paralysis.image"), (248, 208, 48)

    def get_apply_text(self, ally: bool) -> Optional[str]:
        return f"status.paralysis.{'ally' if ally else 'enemy'}.apply"

    def get_damage_text(self, ally: bool) -> Optional[str]:
        return f"status.paralysis.{'ally' if ally else 'enemy'}.damage"

    def get_end_text(self, ally: bool) -> Optional[str]:
        return f"status.paralysis.{'ally' if ally else 'enemy'}.end"

    def get_cancel_text(self, ally: bool) -> Optional[str]:
        return f"status.paralysis.{'ally' if ally else 'enemy'}.cancel"

    def attack(self, si: 'StatusInstance', turn: int, ab: 'ability.AbstractAbility') -> tuple[bool, bool, int]:
        return False, random.random() <= 0.25, 0

    def turn(self, si: 'StatusInstance', turn: int) -> tuple[bool, int]:
        return False, 0

    def apply(self, si: 'StatusInstance', turn: int) -> NoReturn:
        return pokemon_type.ELECTRIC not in si.poke.poke.types

    def get_catch_edit(self):
        return 1.5

    # def get_animation(self, si: 'StatusInstance', pos: tuple[int, int]) -> Optional['battle.Animation']:
    #     return animation.BurnAnimation(pos)


class ConfuseStatus(Status):

    def __init__(self, id_: str):
        super().__init__(id_, True)

    def get_image(self, si: 'StatusInstance') -> Optional[tuple[str, tuple[int, int, int]]]:
        return game.game_instance.get_message("status.confuse.image"), (248, 208, 48)

    def get_apply_text(self, ally: bool) -> Optional[str]:
        return f"status.confuse.apply"

    def get_damage_text(self, ally: bool) -> Optional[str]:
        return f"status.confuse.damage"

    def get_end_text(self, ally: bool) -> Optional[str]:
        return f"status.confuse.end"

    def get_cancel_text(self, ally: bool) -> Optional[str]:
        return f"status.confuse.cancel"

    def attack(self, si: 'StatusInstance', turn: int, ab: 'ability.AbstractAbility') -> tuple[bool, bool, int]:
        n = si.poke.ram_data["confuse"]
        n -= 1
        si.poke.ram_data["confuse"] = n
        if n <= 0:
            del si.poke.ram_data["confuse"]
        cancel = (random.random() <= 0.5 and n > 0)
        return n <= 0, cancel, si.poke.get_max_heal() * 1/8 if cancel else 0

    def turn(self, si: 'StatusInstance', turn: int) -> tuple[bool, int]:
        return False, 0

    @staticmethod
    def __get_nb_hit() -> int:
        r = random.random()
        if r <= (1/3):
            return 2
        if r <= (2/3):
            return 3
        if r <= (5/6):
            return 4
        return 5

    def apply(self, si: 'StatusInstance', turn: int) -> NoReturn:
        si.poke.ram_data["confuse"] = ConfuseStatus.__get_nb_hit()
        return True

    # def get_animation(self, si: 'StatusInstance', pos: tuple[int, int]) -> Optional['battle.Animation']:
    #     return animation.BurnAnimation(pos)


class FlinchingStatus(Status):

    def __init__(self, id_: str):
        super().__init__(id_, False)

    def get_apply_text(self, ally: bool) -> Optional[str]:
        return f"status.flinch.apply"

    def get_damage_text(self, ally: bool) -> Optional[str]:
        return f"status.flinch.cancel"

    def get_end_text(self, ally: bool) -> Optional[str]:
        return f"status.flinch.cancel"

    def get_cancel_text(self, ally: bool) -> Optional[str]:
        return f"status.flinch.cancel"

    def attack(self, si: 'StatusInstance', turn: int, ab: 'ability.AbstractAbility') -> tuple[bool, bool, int]:
        return True, True, 0

    def turn(self, si: 'StatusInstance', turn: int) -> tuple[bool, int]:
        return False, 0

    def apply(self, si: 'StatusInstance', turn: int) -> NoReturn:
        return True


class ClampStatus(Status):

    def __init__(self, id_: str):
        super().__init__(id_, False)

    def get_apply_text(self, ally: bool) -> Optional[str]:
        return f"status.clamp.apply"

    def get_damage_text(self, ally: bool) -> Optional[str]:
        return f"status.clamp.damage"

    def get_end_text(self, ally: bool) -> Optional[str]:
        return f"status.clamp.cancel"

    def get_cancel_text(self, ally: bool) -> Optional[str]:
        return f"status.clamp.cancel"

    def attack(self, si: 'StatusInstance', turn: int, ab: 'ability.AbstractAbility') -> tuple[bool, bool, int]:
        return False, False, si.poke.get_max_heal() // 16

    def turn(self, si: 'StatusInstance', turn: int) -> tuple[bool, int]:
        n = si.poke.ram_data["clamped"]
        n -= 1
        si.poke.ram_data["clamped"] = n
        if n <= 0:
            del si.poke.ram_data["clamped"]
        return n <= 0, 0

    @staticmethod
    def __get_nb_hit() -> int:
        r = random.random()
        if r <= (1/3):
            return 2
        if r <= (2/3):
            return 3
        if r <= (5/6):
            return 4
        return 5

    def apply(self, si: 'StatusInstance', turn: int) -> NoReturn:
        si.poke.ram_data["clamped"] = ClampStatus.__get_nb_hit()
        return True


class StatusInstance(object):

    def __init__(self, status: 'Status', poke: 'player_pokemon.PlayerPokemon'):
        self.status = status
        self.poke = poke
        self.data = {}


class PokeStatus(object):

    def __init__(self, poke: 'player_pokemon.PlayerPokemon', status: list[str]):
        self.poke = poke
        self.it: list[StatusInstance] = []
        for s in status:
            if (st := status_.STATUS[s]).permanent:
                self.try_add(st, 0)

    def get_save(self) -> list[str]:
        return [it.status.id_ for it in self.it if it.status.permanent]

    def can_add(self, status: Status, turn: int) -> bool:
        si = StatusInstance(status, self.poke)
        if si.status.apply(si, turn):
            del si
            return True
        del si
        return False

    def remove(self, status: Status):
        for i in range(len(self.it)):
            if self.it[i].status == status:
                del self.it[i]
                return

    def try_add(self, status: Status, turn: int) -> tuple[bool, Optional[StatusInstance]]:
        si = StatusInstance(status, self.poke)
        if si.status.apply(si, turn):
            if not self.have_status(si.status):
                self.it.append(si)
            return True, si
        del si
        return False, None

    def get_all_image(self) -> list[tuple[str, tuple[int, int, int]]]:
        l = []
        for it in self.it:
            if at := it.status.get_image(it):
                l.append(at)
        return l

    def turn(self, turn) -> list[tuple[Status, bool, int]]:
        l = []
        for it in self.it:
            back = it.status.turn(it, turn)
            l.append((it.status, back[0], back[1]))
        for e in l:
            if e[1]:
                self.__remove(e[0])
        return l

    def attack(self, turn, ab: 'ability.AbstractAbility') -> list[tuple[Status, bool, bool, int]]:
        l = []
        for it in self.it:
            back = it.status.attack(it, turn, ab)
            l.append((it.status, back[0], back[1], back[2]))
        for e in l:
            if e[1]:
                self.__remove(e[0])
        return l

    def reset(self):
        i = 0
        while len(self.it) > i:
            if not self.it[i].status.permanent:
                del self.it[i]
            else:
                i += 1

    def __remove(self, status: Status):
        for i in range(len(self.it)):
            if self.it[i].status == status:
                del self.it[i]

    def have_status(self, status: Status) -> bool:
        for it in self.it:
            if it.status == status:
                return True
        return False
