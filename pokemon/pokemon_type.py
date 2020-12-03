from typing import Dict
import pygame
import game

IMAGES: pygame.Surface = pygame.image.load("assets/textures/hud/type.png")


class Type(object):

    def __init__(self, image_y: int, name: str, edit: Dict):
        self.name = name
        self.edit = edit
        self.image = pygame.Surface((22, 16))
        self.image.blit(IMAGES, (0, 0), pygame.Rect(0, 16 * image_y, 22, 16 * (image_y + 1)))

    def get_name(self) -> str:
        return game.get_game_instance().get_message("type.{}".format(self.name.lower()))

    def get_attack_edit(self, poke) -> float:
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

NORMAL: Type = Type(2, N_NORMAL, {N_ROCK: 0.5, N_GHOST: 0})
FIRE: Type = Type(7, N_FIRE, {N_FIRE: 0.5, N_WATER: 0.5, N_GRASS: 2, N_ICE: 2, N_BUG: 2, N_ROCK: 0.5, N_DRAGON: 0.5})
WATER: Type = Type(10, N_WATER, {N_FIRE: 2, N_WATER: 0.5, N_GRASS: 0.5, N_GROUND: 2, N_ROCK: 2, N_DRAGON: 0.5})
GRASS: Type = Type(1, N_GRASS, {N_FIRE: 0.5, N_WATER: 2, N_GRASS: 0.5, N_POISON: 0.5, N_GROUND: 2, N_FLYING: 0.5, N_BUG: 0.5, N_ROCK: 2, N_DRAGON: 0.5})
ELECTRIC: Type = Type(14, N_ELECTRIC, {N_WATER: 2, N_GRASS: 0.5, N_ELECTRIC: 0.5, N_GROUND: 0, N_FLYING: 2, N_DRAGON: 0.5})
ICE: Type = Type(6, N_ICE, {N_WATER: 0.5, N_GRASS: 2, N_ICE: 0.5, N_GROUND: 2, N_FLYING: 2, N_DRAGON: 2})
FIGHTING: Type = Type(11, N_FIGHTING, {N_NORMAL: 2, N_ICE: 2, N_POISON: 0.5, N_FLYING: 0.5, N_PSYCHIC: 0.5, N_BUG: 0.5, N_ROCK: 2, N_GHOST: 0})
POISON: Type = Type(3, N_POISON, {N_GRASS: 2, N_POISON: 0.5, N_GROUND: 0.5, N_BUG: 2, N_ROCK: 0.5, N_GHOST: 0.5})
GROUND: Type = Type(5, N_GROUND, {N_FIRE: 2, N_GRASS: 0.5, N_ELECTRIC: 2, N_POISON: 2, N_FLYING: 0, N_BUG: 0.5, N_ROCK: 2})
FLYING: Type = Type(13, N_FLYING, {N_GRASS: 2, N_ELECTRIC: 0.5, N_FIGHTING: 2, N_BUG: 2, N_ROCK: 0.5})
PSYCHIC: Type = Type(4, N_PSYCHIC, {N_FIGHTING: 2, N_POISON: 2, N_PSYCHIC: 0.5})
BUG: Type = Type(0, N_BUG, {N_FIRE: 0.5, N_GRASS: 2, N_FIGHTING: 0.5, N_POISON: 2, N_FLYING: 0.5, N_PSYCHIC: 2, N_GHOST: 0.5})
ROCK: Type = Type(8, N_ROCK, {N_FIRE: 2, N_ICE: 2, N_FIGHTING: 0.5, N_GROUND: 0.5, N_FLYING: 2, N_BUG: 2})
GHOST: Type = Type(12, N_GHOST, {N_NORMAL: 0, N_PSYCHIC: 0, N_GHOST: 2})
DRAGON: Type = Type(9, N_DRAGON, {N_DRAGON: 2})


TYPES: Dict[str, Type] = {
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