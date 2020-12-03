import game_error as err
from typing import Dict, List
import json
import displayer
import game
import pokemon.pokemon_type as pok_t
from utils import get_args

NB_POKEMON = 3
POKEMONS = [None for i in range(NB_POKEMON + 1)]

CURVE = {
    "FAST": lambda n: 0.8 * (n ** 3),
    "MEDIUM_FAST": lambda n: n ** 3,
    "MEDIUM_SLOW": lambda n: 1.2 * (n ** 3) - 15 * (n ** 2) + 100 * n - 140,
    "SLOW": lambda n: 1.25 * (n ** 3),
}

CURVE_VALUE = {N: [int(CURVE[N](x)) for x in range(101)] for N, V in CURVE.items()}

HEAL = "hp"

STATS = [HEAL, "attack", "defense", "speed", "sp_attack", "sp_defense"]

class Pokemon(object):

    def __init__(self, _id: int, data: Dict):
        self._id: int = _id
        self.parent: int = get_args(data, "parent", _id, default=0, type_check=int)
        if not (0 <= self.parent <= NB_POKEMON) or self.parent == _id:
            raise err.PokemonParseError("Pokemon ({}) have invalid parent !".format(_id))
        self.types = [pok_t.TYPES[t] for t in get_args(data, "type", _id)]
        self.xp_points: int = get_args(data, "xp_point", _id, type_check=int)
        self.color: str = get_args(data, "color", _id, type_check=str)
        self.evolution = get_args(data, "evolution", _id, default=[])
        self.display: displayer.Displayer = displayer.parse(get_args(data, "display", _id),
                                                            "pokemon/" + to_3_digit(_id))
        self.curve_name = get_args(data, "curve", _id, type_check=str)
        self.curve = CURVE[self.curve_name]
        self.base_stats = get_args(data, "base_stats", _id)
        self.ability = get_args(data, "ability", _id, default={})

    def get_all_possible_ability(self, lvl: int) -> List[str]:
        back = []
        for key, value in self.ability.items():
            if value >= lvl:
                back.append(key)
        if self.parent != 0:
            return back + get_pokemon(self.parent).get_all_possible_ability(lvl)
        return back

    def get_possible_ability_at_lvl(self, lvl: int) -> List[str]:
        back = []
        for key, value in self.ability.items():
            if value == lvl:
                back.append(key)
        if self.parent != 0:
            return back + get_pokemon(self.parent).get_possible_ability_at_lvl(lvl)
        return back

    def get_xp(self, lvl: int) -> int:
        return CURVE_VALUE[self.curve_name][lvl]

    def get_lvl(self, xp) -> int:
        if self.curve_name:
            lvl = 0
            values = CURVE_VALUE[self.curve_name]
            while xp > values[lvl]:
                lvl += 1
            return lvl - 1
        else:
            return int(get_pokemon(self.parent).get_lvl(xp))

    def get_name(self, upper_first=False):
        name = game.get_game_instance().get_poke_message(str(self._id))["name"]
        if upper_first:
            name = name[0].capitalize() + name[1:]
        return name

    def get_evolution(self):
        if self.parent != 0:
            return self.evolution + get_pokemon(self.parent).get_evolution()
        return self.evolution

    def get_evolution_at(self, lvl: int) -> int:
        for ev in self.get_evolution():
            if ev["lvl"] == lvl:
                return ev["pokemon"]
        return 0

    @staticmethod
    def load_pokemons():
        global POKEMONS
        for i in range(1, NB_POKEMON + 1):
            print("data/pokemon/{}.json".format(to_3_digit(i)))
            with open("data/pokemon/{}.json".format(to_3_digit(i)), "r", encoding='utf-8') as file:
                data = json.load(file)
                POKEMONS[i] = Pokemon(i, data)


def get_pokemon(_id: int) -> Pokemon:
    return POKEMONS[_id]


def to_3_digit(num: int) -> str:
    if num < 10:
        return "00" + str(num)
    if num < 100:
        return "0" + str(num)
    return str(num)



