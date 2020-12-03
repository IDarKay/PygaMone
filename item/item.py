import pygame
import game

OBJECT = "OBJECT"

CATEGORY = [OBJECT]

class Item(object):

    def __init__(self, _id: str, image: pygame.Surface, category: str):
        self._id = _id
        self.image = image
        self.category = category

    def get_name(self):
        return game.get_game_instance().get_message(self._id + ".name")

    def get_lore(self):
        return game.get_game_instance().get_message(self._id + ".lore")


