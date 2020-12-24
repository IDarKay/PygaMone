from typing import NoReturn, Any, Optional

import pygame

import pokemon.battle.battle as battle_
import pokemon.pokemon_type as p_type
import pokemon.player_pokemon as p_poke
import pokemon.pokemon as pokemon
import pokemon.status.status as status
import pokemon.status.pokemon_status as pokemon_status
import game_error as err
import game
import random

PHYSICAL = "PHYSICAL"
SPECIAL = "SPECIAL"
STATUS = "STATUS"

TARGET_SELF = 0
TARGET_ENEMY = 1
TARGET_BOTH = 2
TARGET_ALLY = 3

RANGE_MONO = 0
RANGE_TWO = 1
RANGE_THREE = 3

RECOIL_DAMAGE = 0
RECOIL_SELF = 1
NO_RECOIL = 2

CATEGORYS: list[str] = [PHYSICAL, SPECIAL, STATUS]
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
        self.target = self.get_args("target", default=TARGET_ENEMY, type_check=int)
        self.range = self.get_args("range", default=RANGE_MONO, type_check=int)
        self.recoil_type = self.get_args("recoil_type", default=NO_RECOIL, type_check=int)
        self.recoil = self.get_args("recoil", default=0, type_check=int)
        self.is_priority = self.get_args("is_priority", default=0, type_check=int)
        self.render_during = 0
        self.load = False
        self.need_sound = False

        self.last_damage = []
        self.last_launcher: Optional['p_poke.PlayerPokemon'] = None
        self.last_nb_hit = 1

        del self.__data

    def get_render_during(self):
        return self.render_during

    def get_nb_turn(self) -> int:
        return 1

    def get_nb_hit(self) -> int:
        return 1

    def get_category_name(self) -> str:
        return game.get_game_instance().get_message(f'ability.categories.{self.category}')

    def get_target(self, case: int, nb_enemy: int, nb_ally: int, enemy: bool) -> list[
        list[bool, bool, bool], list[bool, bool, bool]]:
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

    # noinspection PyPep8Naming
    def get_damage(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[list[tuple[int, float]], bool, int]:
        self.last_launcher = launcher
        if self.category == STATUS:
            self.last_damage = [0] * len(targets)
            return [(0, 1)] * len(targets), False, 0
        self.last_damage = []
        nb_target = len(targets)
        critical_t = launcher.get_stats(pokemon.SPEED) * \
                     (8 if launcher.get_stats(p_poke.C_S_CRITICAL) > 1 and self.high_critical else
                      4 if self.high_critical else 2 if launcher.get_stats(p_poke.C_S_CRITICAL) > 1 else 0.5)
        nb_hit = self.get_nb_hit()
        self.last_nb_hit = nb_hit
        crit = [random.randint(0, 255) <= critical_t for _ in range(nb_hit)]
        Ta = (0.75 if nb_target > 1 else 1)
        STAB = (1.5 if self.type in launcher.poke.types else 1)
        rdm = (random.randint(85, 100) / 100)
        burn = (0.5 if launcher.combat_status.have_status(status.BURN) and self.category == PHYSICAL else 1)
        modifier = [Ta * (1.5 if crit[i] else 1) * rdm * STAB * burn for i in range(nb_hit)]
        power = self.power
        level = ((2 * launcher.lvl) / 5) + 2
        back = []
        for tr in targets:
            if tr:
                a = launcher.get_stats(pokemon.ATTACK) if self.category == PHYSICAL else tr.get_stats(pokemon.SP_ATTACK)

                # escape divide by 0
                d = max(1, tr.get_stats(pokemon.DEFENSE) if self.category == PHYSICAL else tr.get_stats(
                    pokemon.SP_DEFENSE))

                # todo: weather
                # todo: badge
                # todo other
                type_edit = self.type.get_attack_edit(tr.poke)
                val = ((level * power * (a / d)) / 50) + 2
                # md = modifier * type_edit

                f_damage = int(sum(k * type_edit * val for k in modifier))

                self.last_damage.append(f_damage)
                back.append((f_damage, type_edit))
            else:
                self.last_damage.append(0)
                back.append((0, 0.0))

        recoil = (back[0][0] * self.recoil) if self.recoil == RECOIL_DAMAGE else self.recoil
        return back, max(crit), recoil

    def is_fail(self, poke: 'p_poke.PlayerPokemon'):
        if self.accuracy == -1:
            return False
        return not (random.random() < (self.accuracy * poke.get_stats(p_poke.C_S_ACCURACY, True) / 100))

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) -> tuple[
        tuple[dict[str, int], list['pokemon_status.Status']],
        list[tuple[dict[str, int], list['pokemon_status.Status']]]
    ]:
        return ({}, []), [({}, [])] * len(targets)

    def get_name(self) -> NoReturn:
        return game.get_game_instance().get_ability_message(self.id_)['name']

    def get_description(self) -> NoReturn:
        return game.get_game_instance().get_ability_message(self.id_)['description']

    def get_args(self, key: str, default=None, type_check=None) -> Any:
        return self.get_args_2(self.__data, key, self.id_, default, type_check, _type="ability")

    def get_args_2(self, data: dict[str, Any], key: str, _id: Any, default=None, type_check=None,
                   _type="pokemon") -> Any:
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

    def get_rac(self, target: list[tuple[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        return battle_.RenderAbilityCallback()

    def render(self, display: pygame.Surface, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        pass
