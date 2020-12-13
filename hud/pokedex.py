from typing import NoReturn
from hud.menu_calass import Menu
import pygame
import pokemon.pokemon as pokemon
import hud.menu as menu_


class PokeDex(Menu):

    x = lambda y: (y - 1440) / (-120/53)

    poly_1 = ((636, 0), (742, 0), (477, 600), (371, 600))
    poly_2 = ((742, 0), (1060, 0), (1060, 600), (477, 600))
    poly_3 = ((x(15), 15), (1060, 15), (1060, 65), (x(65), 65))
    poly_4 = ((x(15), 15), (0, 15), (0, 65), (x(65), 65))
    poly_5 = ((0, 570), (1060, 570), (1060, 600), (0, 600))

    def __init__(self, player):
        super().__init__(player)
        self.selected = 0

    def on_key_x(self, value: float, press: bool) -> NoReturn:
        pass

    def on_key_y(self, value: float, press: bool) -> NoReturn:
        if press and value < 0 and self.selected > 0:
            self.selected -= 1
        elif press and value > 0 and self.selected < pokemon.NB_POKEMON - 1:
            self.selected += 1

    def on_key_action(self) -> NoReturn:
        pass

    def on_key_escape(self) -> NoReturn:
        self.player.open_menu(menu_.MainMenu(self.player))

    def render(self, display: pygame.Surface) -> NoReturn:
        display.fill((255, 255, 255))
        pygame.draw.polygon(display, "#f4523b", PokeDex.poly_1)
        pygame.draw.polygon(display, "#fa7248", PokeDex.poly_2)
        pygame.draw.polygon(display, "#333333", PokeDex.poly_3)
        pygame.draw.polygon(display, "#cedae0", PokeDex.poly_4)
        pygame.draw.polygon(display, "#000000", PokeDex.poly_5)

        range_ = self.get_range()

        y = 100

        for id_ in range(*range_):
            self.draw_pokemon(id_, y)
            y += 50


    # def draw_pokemon(self, id_, y):
    #     T color



    def get_range(self):
        end = pokemon.NB_POKEMON - 1
        a, b = self.selected - 3, self.selected + 3
        while a < 0:
            a -= 1
            b += 1
        while 0 < a > end - 7:
            a -= 1
            b -= 1
        b = min(b, end)
        return a, b + 1





