import game_error as err
from typing import Dict, List, Optional, Callable, Any
import json
import displayer
import game
import pokemon.pokemon_type as pok_t
import utils

NB_POKEMON: int = 3
POKEMONS: List[Optional['Pokemon']] = [None for i in range(NB_POKEMON + 1)]

CURVE: Dict[str, Callable[[int], float]] = {
    "FAST": lambda n: 0.8 * (n ** 3),
    "MEDIUM_FAST": lambda n: n ** 3,
    "MEDIUM_SLOW": lambda n: 1.2 * (n ** 3) - 15 * (n ** 2) + 100 * n - 140,
    "SLOW": lambda n: 1.25 * (n ** 3),
}

CURVE_VALUE: Dict[str, List[int]] = {N: [int(CURVE[N](x)) for x in range(101)] for N, V in CURVE.items()}

HEAL: str = "hp"

STATS: List[str] = [HEAL, "attack", "defense", "speed", "sp_attack", "sp_defense"]


class Pokemon(object):

    def __init__(self, id_: int, data: Dict):
        self.id_: int = id_
        self.parent: int = utils.get_args(data, "parent", id_, default=0, type_check=int)
        if not (0 <= self.parent <= NB_POKEMON) or self.parent == id_:
            raise err.PokemonParseError("Pokemon ({}) have invalid parent !".format(id_))
        self.types: 'pok_t' = [pok_t.TYPES[t] for t in utils.get_args(data, "type", id_)]
        self.xp_points: int = utils.get_args(data, "xp_point", id_, type_check=int)
        self.color: str = utils.get_args(data, "color", id_, type_check=str)
        self.evolution: List[Dict[str, Any]] = utils.get_args(data, "evolution", id_, default=[])
        self.display: displayer.Displayer = displayer.parse(utils.get_args(data, "display", id_),
                                                            "pokemon/" + to_3_digit(id_))
        self.curve_name: str = utils.get_args(data, "curve", id_, type_check=str)
        self.curve: Callable[[int], float] = CURVE[self.curve_name]
        self.base_stats: Dict[str, int] = utils.get_args(data, "base_stats", id_)
        self.ability: Dict[str, int] = utils.get_args(data, "ability", id_, default={})
        self.catch_rate: float = utils.get_args(data, "catch_rate", id_)

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

    def get_name(self, upper_first=False) -> str:
        name = game.get_game_instance().get_poke_message(str(self.id_))["name"]
        if upper_first:
            name = name[0].capitalize() + name[1:]
        return name

    def get_evolution(self) -> List[Dict[str, int]]:
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



