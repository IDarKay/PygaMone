from typing import List
import pygame
import game

OBJECT: str = "OBJECT"
HEAL: str = "HEAL"
POKE_BALLS: str = "POKE_BALLS"
BATTLE_ITEMS: str = "BATTLE_ITEMS"
BERRIES: str = "BERRIES"
CT: str = "CT"
TREASURES: str = "TREASURES"
RARE: str = "RARE"

CATEGORY: List[str] = [OBJECT]


class Item(object):

    def __init__(self, identifier: str, image: pygame.Surface, category: str):
        self.identifier = identifier
        self.image = image
        self.category = category

    def get_name(self) -> str:
        return game.get_game_instance().get_message(self.identifier + ".name")

    def get_lore(self) -> str:
        return game.get_game_instance().get_message(self.identifier + ".lore")


