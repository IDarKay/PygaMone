from typing import List, Dict, NoReturn, Any, Tuple
import utils
import pokemon.pokemon_type as p_type
import pokemon.player_pokemon as p_poke
import pokemon.pokemon as pokemon
import game_error as err
import game
import pygame
import pygame_gif
import pokemon.battle.battle as battle_
import sound_manager
import random
import pokemon.status.status as status
import pokemon.status.pokemon_status as pokemon_status

PHYSICAL = "PHYSICAL"
SPECIAL = "SPECIAL"
STATUS = "STATUS"

TARGET_ALLY = 0
TARGET_ENEMY = 1
TARGET_BOTH = 2

RANGE_MONO = 0
RANGE_TWO = 1
RANGE_THREE = 3

RECOIL_DAMAGE = 0
RECOIL_SELF = 1
NO_RECOIL = 2

CATEGORYS: List[str] = [PHYSICAL, SPECIAL, STATUS]
ABILITY_SOUND_FOLDER = 'assets/sound/ability/'

class AbstractAbility(object):

    def __init__(self, id_, **data):
        self.id_ = id_
        self.__data = data
        self.type = p_type.TYPES[self.get_args("type", type_check=str)]
        self.category = self.get_args("category")
        if self.category not in CATEGORYS:
            raise err.AbilityParseError("Invalid category for {}".format(id_))
        self.pp = self.get_args("pp", type_check=int)
        self.max_pp = self.get_args("max_pp", type_check=int)
        self.power = self.get_args("power", type_check=int)
        self.accuracy = self.get_args("accuracy", type_check=int)
        self.contact = self.get_args("contact", default=False, type_check=bool)
        self.protect = self.get_args("protect", default=False, type_check=bool)
        self.magic_coat = self.get_args("magic_coat", default=False, type_check=bool)
        self.snatch = self.get_args("snatch", default=False, type_check=bool)
        self.mirror_move = self.get_args("mirror_move", default=False, type_check=bool)
        self.king_rock = self.get_args("king_rock", default=False, type_check=bool)
        self.high_critical = self.get_args("high_critical", default=False, type_check=bool)
        # self.target = self.get_args("target")
        self.target = self.get_args("target", default=TARGET_ENEMY, type_check=int)
        self.range = self.get_args("range", default=RANGE_MONO, type_check=int)
        self.recoil_type = self.get_args("recoil_type", default=NO_RECOIL, type_check=int)
        self.recoil = self.get_args("recoil", default=0, type_check=int)
        self.render_during = 0
        self.load = False
        self.need_sound = False
        del self.__data

    def get_target(self, case: int, nb_enemy: int, nb_ally: int, enemy: bool) -> list[list[bool, bool, bool], list[bool, bool, bool]]:
        table = [[False] * 3] * 2
        nb = nb_enemy if enemy else nb_ally
        ln = [False] * 3
        if self.range == RANGE_THREE:
            ln = [True] * 3
        elif self.range == RANGE_TWO:
            ln = [True, True] if nb != 3 else [True, True, False] if case == 0 else [False, True, True]
        else:
            ln[case] = True
        table[0 if enemy else 1] = ln
        return table

    def get_damage(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) -> tuple[list[tuple[int, float]], bool, int]:
        nb_target = len(targets)
        critical_T = launcher.get_stats(pokemon.SPEED) *\
                     (8 if launcher.get_stats(p_poke.C_S_CRITICAL) >= 1 and self.high_critical else
                      4 if self.high_critical else 2 if launcher.get_stats(p_poke.C_S_CRITICAL) >= 1 else 0.5)
        crit = random.randint(0, 255) <= critical_T
        Ta = (0.75 if nb_target > 1 else 1)
        STAB = (1.5 if self.type in launcher.poke.types else 1)
        rdm = (random.randint(85, 100) / 100)
        burn = (0.5 if launcher.combat_status.have_status(status.BURN) and self.category == PHYSICAL else 1)
        modifier = Ta * (1.5 if crit else 1) * rdm * STAB * burn
        power = self.power
        level = ((2 * launcher.lvl) / 5) + 2
        back = []
        for tr in targets:
            if tr:
                a = launcher.get_stats(pokemon.ATTACK) if self.category == PHYSICAL else tr.get_stats(pokemon.SP_ATTACK)

                # escape divide by 0
                d = max(1, tr.get_stats(pokemon.DEFENSE) if self.category == PHYSICAL else tr.get_stats(pokemon.SP_DEFENSE))

                # todo: weather
                # todo: badge
                # todo other
                type_edit = self.type.get_attack_edit(tr.poke)
                val = ((level * power * (a / d)) / 50) + 2
                md = modifier * type_edit
                back.append((int(val * md), type_edit))
            else:
                back.append((0, 0.0))

        recoil = 0 if self.recoil == NO_RECOIL else (back[0] * self.recoil) if self.recoil == RECOIL_DAMAGE else self.recoil

        return back, crit, recoil

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) -> tuple[
        Tuple[Dict[str, int], List['pokemon_status.Status']],
        List[Tuple[Dict[str, int], List['pokemon_status.Status']]]
    ]:
        return ({}, []), [({}, [])] * len(targets)

    def get_name(self) -> NoReturn:
        return game.get_game_instance().get_message("ability." + self.id_)

    def get_args(self, key: str, default=None, type_check=None) -> Any:
        return self.get_args_2(self.__data, key, self.id_, default, type_check, _type="ability")

    def get_args_2(self, data: Dict[str, Any], key: str, _id: Any, default=None, type_check=None, _type="pokmon") -> Any:
        value = None
        if default is not None:
            value = data[key] if key in data else None if default == "NONE" else default
        else:
            if key not in data:
                raise err.PokemonParseError("No {} value for a {} ({}) !".format(key, _type, _id))
            value = data[key]
        if type_check:
            if value and not isinstance(value, type_check):
                raise err.PokemonParseError(
                    "Invalid var type for {} need be {} for {} ({})".format(key, type_check, _type, _id))
        return value

    def load_assets(self) -> bool:
        if not self.load:
            self.load = True
            if self.need_sound:
                self.sound = pygame.mixer.Sound(ABILITY_SOUND_FOLDER + self.id_ + ".mp3")
            return True
        return False

    def unload_assets(self) -> bool:
        if self.load:
            self.load = False
            if self.need_sound:
                del self.sound
            return False
        return True

    def get_rac(self, target: List[Tuple[int, int, int]],
               launcher: Tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        return battle_.RenderAbilityCallback()

    def render(self, display: pygame.display, target: List[Tuple[int, int, int]],
               launcher: Tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        pass


class TackleAbility(AbstractAbility):
    def __init__(self):
        super().__init__(id_='tackle',
                         type="NORMAL",
                         category="PHYSICAL",
                         pp=34,
                         max_pp=56,
                         power=40,
                         accuracy=100,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=TARGET_ENEMY)

        self.render_during = 2000


class EmberAbility(AbstractAbility):

    def __init__(self):
        super().__init__(id_='ember',
                         type="FIRE",
                         category="SPECIAL",
                         pp=25,
                         max_pp=40,
                         power=40,
                         accuracy=100,
                         protect=True,
                         magic_coat=True,
                         mirror_move=True,
                         target=TARGET_ENEMY,
                         recoil_type=RECOIL_SELF,
                         recoil=10
                         )
        self.render_during = 2000
        self.need_sound = True

    def load_assets(self) -> bool:
        if super().load_assets():
            self.gif = pygame_gif.PygameGif('assets/textures/ability/ember.gif')
            return True
        return False

    def get_rac(self, target: List[Tuple[int, int, int]],
               launcher: Tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        if ps_t < 1800:
            v = ps_t % 180
            v = -6 if v < 60 else 0 if v < 120 else 6
            target_m = [(t[2], v, 0) for t in target]
            return battle_.RenderAbilityCallback(move_target=target_m)
        return battle_.RenderAbilityCallback()

    def unload_assets(self) -> bool:
        if super().load_assets():
            del self.gif
            del self.g_i
            return True
        return False

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) -> tuple[
        Tuple[Dict[str, int], List['pokemon_status.Status']],
        List[Tuple[Dict[str, int], List['pokemon_status.Status']]]
    ]:
        return ({}, []), [({"speed": 2}, [status.BURN] if random.random() < 1 else []) for i in range(len(targets))]


    def render(self, display: pygame.display, target: List[Tuple[int, int, int]],
               launcher: Tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            self.g_i = self.gif.display(target[0])
            sound_manager.start_in_first_empty_taunt(self.sound)
        for t in target:
            self.g_i.render(display, (t[0] - 40, t[1] - 120))


load: bool = False