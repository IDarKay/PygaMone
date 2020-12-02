from typing import Dict
import pokemon.pokemon


class Type(object):

    def __init__(self, name: str, edit: Dict):
        self.name = name
        self.edit = edit

    def get_attack_edit(self, poke):
        v = 1
        for __type in poke.types:
            if __type in self.edit:
                v *= self.edit[__type]
        return v


N_NORMAL = "NORMAL"
N_POISON = "POISON"
N_PSYCHIC = "PSYCHIC"
N_GRASS = "GRASS"
N_GROUND = "GROUND"
N_ICE = "ICE"
N_FIRE = "FIRE"
N_ROCK = "ROCK"
N_DRAGON = "DRAGON"
N_WATER = "WATER"
N_BUG = "BUG"
# N_DARK = "DARK"
N_FIGHTING = "FIGHTING"
N_GHOST = "GHOST"
# N_STEEL = "STEEL"
N_FLYING = "FLYING"
N_ELECTRIC = "ELECTRIC"
# N_FAIRY = "FAIRY"

NORMAL = Type(N_NORMAL, {N_ROCK: 0.5, N_GHOST: 0})
FIRE = Type(N_FIRE, {N_FIRE: 0.5, N_WATER: 0.5, N_GRASS: 2, N_ICE: 2, N_BUG: 2, N_ROCK: 0.5, N_DRAGON: 0.5})
WATER = Type(N_WATER, {N_FIRE: 2, N_WATER: 0.5, N_GRASS: 0.5, N_GROUND: 2, N_ROCK: 2, N_DRAGON: 0.5})
GRASS = Type(N_GRASS, {N_FIRE: 0.5, N_WATER: 2, N_GRASS: 0.5, N_POISON: 0.5, N_GROUND: 2, N_FLYING: 0.5, N_BUG: 0.5, N_ROCK: 2, N_DRAGON: 0.5})
ELECTRIC = Type(N_ELECTRIC, {N_WATER: 2, N_GRASS: 0.5, N_ELECTRIC: 0.5, N_GROUND: 0, N_FLYING: 2, N_DRAGON: 0.5})
ICE = Type(N_ICE, {N_WATER: 0.5, N_GRASS: 2, N_ICE: 0.5, N_GROUND: 2, N_FLYING: 2, N_DRAGON: 2})
FIGHTING = Type(N_FIGHTING, {N_NORMAL: 2, N_ICE: 2, N_POISON: 0.5, N_FLYING: 0.5, N_PSYCHIC: 0.5, N_BUG: 0.5, N_ROCK: 2, N_GHOST: 0})
POISON = Type(N_POISON, {N_GRASS: 2, N_POISON: 0.5, N_GROUND: 0.5, N_BUG: 2, N_ROCK: 0.5, N_GHOST: 0.5})
GROUND = Type(N_GROUND, {N_FIRE: 2, N_GRASS: 0.5, N_ELECTRIC: 2, N_POISON: 2, N_FLYING: 0, N_BUG: 0.5, N_ROCK: 2})
FLYING = Type(N_FLYING, {N_GRASS: 2, N_ELECTRIC: 0.5, N_FIGHTING: 2, N_BUG: 2, N_ROCK: 0.5})
PSYCHIC = Type(N_PSYCHIC, {N_FIGHTING: 2, N_POISON: 2, N_PSYCHIC: 0.5})
BUG = Type(N_BUG, {N_FIRE: 0.5, N_GRASS: 2, N_FIGHTING: 0.5, N_POISON: 2, N_FLYING: 0.5, N_PSYCHIC: 2, N_GHOST: 0.5})
ROCK = Type(N_ROCK, {N_FIRE: 2, N_ICE: 2, N_FIGHTING: 0.5, N_GROUND: 0.5, N_FLYING: 2, N_BUG: 2})
GHOST = Type(N_GHOST, {N_NORMAL: 0, N_PSYCHIC: 0, N_GHOST: 2})
DRAGON = Type(N_DRAGON, {N_DRAGON: 2})


TYPES = {
    N_NORMAL: NORMAL,
    N_POISON: POISON,
    N_PSYCHIC: PSYCHIC,
    N_GRASS: GRASS,
    N_GROUND: GROUND,
    N_ICE: ICE,
    N_FIRE: FIRE,
    N_ROCK: ROCK,
    N_DRAGON: DRAGON,
    N_WATER: WATER,
    N_BUG: BUG,
    # N_DARK: DARK,
    N_FIGHTING: FIGHTING,
    N_GHOST: GHOST,
    # N_STEEL: STEEL,
    N_FLYING: FLYING,
    N_ELECTRIC: ELECTRIC,
    # N_FAIRY: FAIRY,
}