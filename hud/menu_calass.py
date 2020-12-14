from typing import NoReturn
from abc import abstractmethod
import character.player as char_play
import pygame

class Menu(object):

    def __init__(self, player: 'char_play.Player'):
        self.player = player

    def on_key_x(self, value: float, press: bool) -> NoReturn:
        pass

    def on_key_y(self, value: float, press: bool) -> NoReturn:
        pass

    def on_key_action(self) -> NoReturn:
        pass

    def on_key_bike(self) -> NoReturn:
        pass

    def on_key_escape(self) -> NoReturn:
        pass

    @abstractmethod
    def render(self, display: pygame.Surface):
        pass
