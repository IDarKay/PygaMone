from typing import List
import pygame
import game
import pokemon.player_pokemon as player_pokemon

OBJECT: str = "OBJECT"
HEAL: str = "HEAL"
POKE_BALLS: str = "POKE_BALLS"
BATTLE_ITEMS: str = "BATTLE_ITEMS"
BERRIES: str = "BERRIES"
CT: str = "CT"
TREASURES: str = "TREASURES"
RARE: str = "RARE"

CATEGORY: List[str] = [HEAL, POKE_BALLS, BATTLE_ITEMS, BERRIES, OBJECT, CT, TREASURES]


class Item(object):

    def __init__(self, identifier: str, image_name: str, category: str):
        self.identifier = identifier
        self.image = pygame.image.load(f'assets/textures/item/{image_name}.png')
        if self.image.get_size() != (24, 24):
            self.image = pygame.transform.scale(self.image, (24, 24))
        self.category = category

    def get_name(self) -> str:
        return game.get_game_instance().get_message(self.identifier + ".name")

    def get_lore(self) -> str:
        return game.get_game_instance().get_message(self.identifier + ".lore")

    def use(self, poke: 'player_pokemon.PlayerPokemon'):
        pass

    def can_use(self, poke: 'player_pokemon.PlayerPokemon') -> bool:
        return False

    def is_giveable(self, condition: int):
        return False

    def is_usable(self, condition: int):
        return False

    def __hash__(self):
        return self.identifier.__hash__()


