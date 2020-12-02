from typing import Tuple
import pokemon.pokemon as pokemon
from typing import Dict
from random import randint

class PlayerPokemon(object):

    def __init__(self, _id: int, xp, ivs, heal):
        self._id = _id
        self.xp = xp
        self.poke = pokemon.get_pokemon(self._id)
        self.lvl = self.get_lvl()
        self.ivs = ivs
        self.heal = heal
        self.stats = {}
        self.calculate_stats()

        # heal check
        if self.heal == 1 or self.heal > self.get_max_heal():
            self.heal = self.get_max_heal()

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

    def get_name(self, upper_first=False):
        return self.poke.get_name(upper_first)

    def add_xp(self, amount: int) -> bool:
        if amount < 0:
            raise ValueError("negative xp amount")
        if self.lvl == 100:
            return False
        self.xp += amount
        n = self.get_lvl()
        if self.lvl != n:
            self.lvl = n
            return True
        return False

    def serialisation(self):
        return {
            "_id": self._id,
            "xp": self.xp,
            "ivs": ivs_to_int(self.ivs),
            "heal": self.heal
        }


    @staticmethod
    def create_pokemon(_id: int, lvl: int):
        xp = pokemon.get_pokemon(_id).get_lvl(lvl)
        ivs = random_ivs()
        return PlayerPokemon(_id, xp, ivs, -1)
        pass

    @staticmethod
    def from_json(data):
        return PlayerPokemon(data["_id"], data["xp"],
                             ivs_from_int(data["ivs"]), data["heal"])


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