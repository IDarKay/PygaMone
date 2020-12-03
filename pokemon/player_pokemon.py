import pokemon.pokemon as pokemon
from typing import Dict, List, Tuple
from random import randint
import pokemon.ability as p_ability
import item.items as items

class PokemonAbility(object):

    def __init__(self, _id: str, pp: int, max_pp: int):
        self._id = _id
        self.ability = p_ability.ABILITYS[_id]
        self.pp = pp
        self.max_pp = max_pp


    def serialisation(self) -> Dict:
        return {
            "_id": self._id,
            "pp": self.pp,
            "max_pp": self.max_pp,
        }

    @staticmethod
    def new_ability(_id: str):
        """

        :rtype: PokemonAbility
        """
        ab = p_ability.ABILITYS[_id]
        return PokemonAbility(_id, ab.pp, ab.max_pp)

    @staticmethod
    def deserialisation(data):
        """

        :rtype: PokemonAbility
        """
        return PokemonAbility(
            data["_id"],
            data["pp"],
            data["max_pp"]
        )

class PlayerPokemon(object):

    def __init__(self, _id: int, xp, ivs, heal, ability: List[PokemonAbility], poke_ball):
        self._id = _id
        self.xp = xp
        self.poke = pokemon.get_pokemon(self._id)
        self.lvl = self.get_lvl()
        self.ivs = ivs
        self.heal = heal
        self.stats = {}
        self.calculate_stats()
        self.ability = ability
        self.poke_ball = poke_ball

        # heal check
        if self.heal == 1 or self.heal > self.get_max_heal():
            self.heal = self.get_max_heal()

    def get_ability(self, slot: int):
        if slot < 0 or slot > 4:
            raise ValueError("Slot need be in [0:4]")
        if len(self.ability) - 1 >= slot:
            return self.ability[slot]
        return None

    def get_max_heal(self):
        return self.stats[pokemon.HEAL]

    def calculate_stats(self):
        for st in pokemon.STATS:
            self.stats[st] = calculate_stats(self.lvl, self.poke.base_stats[st], self.ivs[st], st == pokemon.STATS[0])

    def get_lvl(self) -> int:
        return self.poke.get_lvl(self.xp)

    def current_xp_status(self):
        if self.lvl < 100:
            this_l = self.poke.get_xp(self.lvl)
            return self.xp - this_l, self.poke.get_xp(self.lvl + 1) - this_l
        else:
            return 0

    def add_attack(self, slot: int, ability_name: str):
        if slot < 0 or slot > 4:
            raise ValueError("Slot need be in [0:4]")
        self.ability[slot] = PokemonAbility.new_ability(ability_name)

    def get_name(self, upper_first=False):
        return self.poke.get_name(upper_first)

    def add_xp(self, amount: int) -> Tuple[bool, int, int]:
        if amount < 0:
            raise ValueError("negative xp amount")
        if self.lvl == 100:
            return False, 100, 100
        self.xp += amount
        n = self.get_lvl()
        if self.lvl != n:
            self.lvl = n
            return True, n, self.lvl
        return False, n, n

    def serialisation(self):
        return {
            "_id": self._id,
            "xp": self.xp,
            "ivs": ivs_to_int(self.ivs),
            "heal": self.heal,
            "ability": [a.serialisation() for a in self.ability],
            "pokeball": self.poke_ball._id
        }

    @staticmethod
    def create_pokemon(_id: int, lvl: int, poke_ball=items.POKE_BALL):
        poke = pokemon.get_pokemon(_id)
        xp = poke.get_lvl(lvl)
        ivs = random_ivs()
        ability = poke.get_all_possible_ability(lvl)
        _ability = []
        for i in range(min(len(ability), 4)):
            a = randint(0, len(ability) - 1)
            _ability[i] = PokemonAbility.new_ability(ability[a])
            del ability[a]
        return PlayerPokemon(_id, xp, ivs, -1, _ability, poke_ball)
        pass

    @staticmethod
    def from_json(data):
        return PlayerPokemon(data["_id"], data["xp"],
                             ivs_from_int(data["ivs"]), data["heal"],
                             [PokemonAbility.deserialisation(a) for a in data["ability"]],
                             items.ITEMS[data["pokeball"]]
                             )


# IVS =
# 0000-0000-0000-0000-0000-0000-0000-0000
#                     ATTA/DEF/SPEED/SPECIAL

def calculate_stats(level: int, base: int, iv: int, is_hp: bool):
    n = ((((base + iv) * 2) * level) / 100) + 10
    if is_hp:
        n += level
    return int(n)


def ivs_from_int(ivs: int) -> Dict:
    back = {
        pokemon.STATS[1]: (ivs & (0b1111 << 12)) >> 12,
        pokemon.STATS[2]: (ivs & (0b1111 << 8)) >> 8,
        pokemon.STATS[3]: (ivs & (0b1111 << 4)) >> 4,
        pokemon.STATS[4]: ivs & 0b1111,
        pokemon.STATS[5]: ivs & 0b1111,
        pokemon.STATS[0]: ((((ivs & (0b1111 << 12)) >> 12) & 0b1) << 3) +
                          ((((ivs & (0b1111 << 8)) >> 8) & 0b1) << 2) +
                          ((((ivs & (0b1111 << 4)) >> 4) & 0b1) << 1) +
                          ((ivs & 0b1111) & 0b1)
    }
    return back


def random_ivs():
    return ivs_from_int((randint(0, 15) << 12) + (randint(0, 15) << 8) + (randint(0, 15) << 4) + randint(0, 15))


def ivs_to_int(ivs_dic: dict) -> int:
    return (ivs_dic[pokemon.STATS[1]] << 12) + (ivs_dic[pokemon.STATS[2]] << 8) + (ivs_dic[pokemon.STATS[3]] << 4) + ivs_dic[pokemon.STATS[4]]