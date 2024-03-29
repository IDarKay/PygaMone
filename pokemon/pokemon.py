from typing import Dict, List, Optional, Callable, Any
import json
import game
import pokemon.pokemon_type as pok_t
import utils
import os

from pokemon import abilitys_

NB_POKEMON: int = 151
POKEMONS: List[Optional['Pokemon']] = [None for i in range(NB_POKEMON + 1)]

CURVE: Dict[str, Callable[[int], float]] = {
    "FAST": lambda n: 0.8 * (n ** 3),
    "MEDIUM_FAST": lambda n: n ** 3,
    "MEDIUM_SLOW": lambda n: 1.2 * (n ** 3) - 15 * (n ** 2) + 100 * n - 140,
    "SLOW": lambda n: 1.25 * (n ** 3),
}

CURVE_VALUE: Dict[str, List[int]] = {N: [int(CURVE[N](x)) for x in range(101)] for N, V in CURVE.items()}

HEAL: str = "hp"
ATTACK: str = "attack"
DEFENSE: str = "defense"
SPEED: str = "speed"
SP_ATTACK: str = "sp_attack"
SP_DEFENSE: str = "sp_defense"

STATS: List[str] = [HEAL, ATTACK, DEFENSE, SPEED, SP_ATTACK, SP_DEFENSE]

TRANSLATE_STATS = {}


def init_translate(g: 'game.Game'):
    for s in STATS:
        TRANSLATE_STATS[s] = g.get_message("stats." + s)


class Pokemon(object):

    def __init__(self, id_: int, data: Dict):
        self.id_: int = id_
        self.types: List['pok_t.Type'] = [pok_t.TYPES[t] for t in utils.get_args(data, "type", id_)]
        self.xp_points: int = utils.get_args(data, "xp_point", id_, type_check=int)
        self.color: str = utils.get_args(data, "color", id_, type_check=str)
        self.evolution: List[Dict[str, Any]] = utils.get_args(data, "evolution", id_, default=[])
        self.female_rate: float = utils.get_args(data, "female_rate", id_)
        self.have_female_image = os.path.isfile(f'assets/textures/pokemon/female/{self.id_}.png')
        self.curve_name: str = utils.get_args(data, "curve", id_, type_check=str)
        self.curve: Callable[[int], float] = CURVE[self.curve_name]
        self.base_stats: Dict[str, int] = utils.get_args(data, "base_stats", id_)
        self.ability: Dict[str, int] = utils.get_args(data, "ability", id_, default={})
        self.ability = {k: v for k, v in self.ability.items() if k in abilitys_.ABILITYS}
        print(self.id_, self.ability)
        self.catch_rate: float = utils.get_args(data, "catch_rate", id_)
        self.size = utils.get_args(data, "size", id_, default=0)
        self.weight = utils.get_args(data, "weight", id_, default=0)

    def get_all_possible_ability(self, lvl: int) -> List[str]:
        back = []
        for key, value in self.ability.items():
            if value <= lvl:
                back.append(key)
        return back

    def get_ability_lvl(self, e):
        if e in self.ability:
            return self.ability[e]
        raise ValueError("{} not in ability".format(e))

    def get_4_last_ability(self, lvl: int) -> List[str]:
        l = self.get_all_possible_ability(lvl)
        sorted(l, key=self.get_ability_lvl, reverse=True)
        if len(l) > 4:
            l = l[0:4]

        return l

    def get_possible_ability_at_lvl(self, lvl: int) -> List[str]:
        back = []
        for key, value in self.ability.items():
            if value == lvl:
                back.append(key)
        return back

    def get_xp(self, lvl: int) -> int:
        return CURVE_VALUE[self.curve_name][lvl]

    def get_lvl(self, xp) -> int:
        lvl = 0
        values = CURVE_VALUE[self.curve_name]
        while xp >= values[lvl]:
            lvl += 1
        return lvl - 1

    def get_name(self, upper_first=False) -> str:
        name = game.get_game_instance().get_poke_message(str(self.id_)).get("name", "unset")
        if upper_first:
            name = name[0].capitalize() + name[1:]
        return name

    def get_japan_name(self) -> str:
        try:
            return game.get_game_instance().get_poke_message(str(self.id_)).get("japan", "unset")
        except KeyError:
            return ""

    def get_pokedex(self) -> str:
        return game.get_game_instance().get_poke_message(str(self.id_)).get("pokedex", "unset")

    def get_evolution(self) -> List[Dict[str, int]]:
        return self.evolution

    def get_evolution_at(self, lvl: int) -> int:
        for ev in self.get_evolution():
            if ev["lvl"] == lvl:
                return ev["pokemon"]
        return 0

    def get_evolution_under(self, lvl: int) -> list[int]:
        li = []
        for ev in self.get_evolution():
            if ev["lvl"] <= lvl:
                li.append(ev["pokemon"])
        return li

    @staticmethod
    def load_pokemons():
        global POKEMONS, NB_POKEMON
        for i in range(0, NB_POKEMON + 1):
            try:
                with open("data/pokemon/{}.json".format(to_3_digit(i)), "r", encoding='utf-8') as file:
                    data = json.load(file)
                    POKEMONS[i] = Pokemon(i, data)
            except FileNotFoundError:
                print(f'pokemon id : {i}, not found')
                break
        while POKEMONS[-1] is None:
            del POKEMONS[-1]
        NB_POKEMON = len(POKEMONS) - 1
        print(NB_POKEMON)


def get_pokemon(_id: int) -> Pokemon:
    return POKEMONS[_id]


def to_3_digit(num: int) -> str:
    if num < 10:
        return "00" + str(num)
    if num < 100:
        return "0" + str(num)
    return str(num)
