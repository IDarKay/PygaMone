from typing import NoReturn
from hud.menu_calass import Menu
import pygame
import pokemon.pokemon as pokemon
import hud.menu as menu_
import game
import displayer
import utils
import option
import sound_manager
import sounds
import hud.hud as hud


class PokeDex(Menu):

    x = lambda y: (y - 1440) / (-120/53)

    poly_1 = ((636, 0), (742, 0), (477, 600), (371, 600))
    poly_2 = ((742, 0), (1060, 0), (1060, 600), (477, 600))
    poly_3 = ((x(15), 15), (1060, 15), (1060, 65), (x(65), 65))
    poly_4 = ((x(15), 15), (0, 15), (0, 65), (x(65), 65))

    PATH = 'assets/textures/pokemon/{}.png'.format

    def __init__(self, player, selected=0):
        super().__init__(player)
        self.selected = selected

        self.arrow = utils.ARROW
        self.nb_caught = sum(map(game.POKEDEX_CATCH.__eq__, game.get_game_instance().pokedex.values()))
        self.nb_saw = sum(map(game.POKEDEX_SEEN.__eq__, game.get_game_instance().pokedex.values()))
        self.black_pokeball = utils.change_image_color(utils.GRAY_POKEBALL.copy(), (0, 0, 0))
        self.white_pokeball = utils.change_image_color(utils.GRAY_POKEBALL.copy(), (255, 255, 255))
        self.light_orange_point = utils.change_image_color(utils.POINT_POKEBALL.copy(), (199, 90, 57))

        self.keys = {
            game.get_game_instance().get_message("back"): option.KEY_QUITE,
            game.get_game_instance().get_message("information"): option.KEY_ACTION
        }

    def __del__(self):
        print("dell pokedex")
        game.POKE_CACHE.clear()

    def on_key_x(self, value: float, press: bool) -> NoReturn:
        pass

    def on_key_y(self, value: float, press: bool) -> NoReturn:
        if press and value < 0 and self.selected > 0:
            self.selected -= 1
            sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
        elif press and value > 0 and self.selected < pokemon.NB_POKEMON - 1:
            self.selected += 1
            sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)

    def on_key_action(self) -> NoReturn:
        status = game.get_game_instance().get_pokedex_status(self.selected + 1)
        if status != game.POKEDEX_NEVER_SEEN:
            self.player.open_menu(PokeDexInfo(self.player, self.selected))
            sound_manager.start_in_first_empty_taunt(sounds.PLINK)

    def on_key_escape(self) -> NoReturn:
        self.player.open_menu(menu_.MainMenu(self.player))
        sound_manager.start_in_first_empty_taunt(sounds.BACK)

    def render(self, display: pygame.Surface) -> NoReturn:
        display.fill("#ecdcdf")
        pygame.draw.polygon(display, "#f4523b", PokeDex.poly_1)
        pygame.draw.polygon(display, "#fa7248", PokeDex.poly_2)
        pygame.draw.polygon(display, "#333333", PokeDex.poly_3)
        pygame.draw.polygon(display, "#cedae0", PokeDex.poly_4)

        utils.draw_button_info(display, **self.keys)

        nb = game.FONT_24.render(game.get_game_instance().get_message("number"), True, (255, 255, 255))
        nb_s = nb.get_size()

        # 839 = (1060 - x(40)) // 2 + x(40)
        display.blit(nb, (839 - (nb_s[0] // 2), 40 - (nb_s[1] // 2)))
        nb = game.FONT_24.render(game.get_game_instance().get_message("pokedex"), True, (0, 0, 0))
        display.blit(nb, (10, 40 - (nb_s[1] // 2)))
        x_1 = 20 + nb.get_size()[0]

        pygame.draw.rect(display, "#595959", (x_1, 22, 100, 34), border_radius=10)
        display.blit(f := game.FONT_20.render(str(self.nb_caught), True, (255, 255, 255)),
                     (x_1 + 50, 40 - (f.get_size()[1] // 2)))
        display.blit(utils.RED_POKEBALL, (x_1 + 10, 23))
        pygame.draw.rect(display, "#595959", (x_1 + 110, 22, 100, 34), border_radius=10)
        display.blit(f := game.FONT_20.render(str(self.nb_saw), True, (255, 255, 255)),
                     (x_1 + 160, 40 - (f.get_size()[1] // 2)))
        display.blit(utils.POINT_POKEBALL, (x_1 + 120, 23))

        range_ = self.get_range()

        y = 90

        for id_ in range(*range_):
            self.draw_pokemon(display, id_, y)
            if self.selected == id_:
                display.blit(self.arrow, (625, y + 10))
            y += 50

    def draw_pokemon(self, display: pygame.Surface, id_: int, y: int) -> NoReturn:
        r_id_ = id_ + 1
        status = game.get_game_instance().get_pokedex_status(r_id_)
        color = (100, 100, 100) if status == game.POKEDEX_NEVER_SEEN else (255, 255, 255) if self.selected == id_ else (0, 0, 0)
        poke = pokemon.get_pokemon(r_id_ if status != game.POKEDEX_NEVER_SEEN else 0)

        if status != game.POKEDEX_NEVER_SEEN and self.selected == id_:
            utils.draw_split_rond_rectangle(display, (650, y + 8, 355, 31), 0.5, 0.45, "#f0501e", "#000000")
            big_im = displayer.get_poke(PokeDex.PATH(str(poke.id_)), 3)
            s_x, s_y = big_im.get_size()
            display.blit(big_im, (250 - s_x // 2, 300 - s_y // 2))

        im = displayer.get_poke(PokeDex.PATH(str(poke.id_)), 0.5)
        delta_x, delta_y = utils.get_first_color(im)
        display.blit(im, (636, y + 30 - delta_y))
        display.blit(game.FONT_24.render(f"N° {pokemon.to_3_digit(r_id_)}", True, color), (680, y + 12))
        display.blit(game.FONT_24.render(poke.get_name(True) if poke.id_ != 0 else "???", True, color), (840, y + 12))
        if status != game.POKEDEX_NEVER_SEEN:
            display.blit(
                (self.white_pokeball if self.selected == id_ else self.black_pokeball) if status == game.POKEDEX_CATCH
                else (utils.POINT_POKEBALL if self.selected == id_ else self.light_orange_point),
                (980, y + 8)
            )

    def get_range(self) -> tuple[int, int]:
        end = pokemon.NB_POKEMON
        a, b = self.selected - 4, self.selected + 4
        while a < 0:
            a += 1
            b += 1
        while 0 < a > end - 9:
            a -= 1
            b -= 1
        b = min(b, end)
        return a, b + 1

class PokeDexInfo(Menu):

    def __init__(self, player, selected):
        super().__init__(player)
        self.selected = selected

        self.keys = {
            game.get_game_instance().get_message("back"): option.KEY_QUITE,
            game.get_game_instance().get_message("previous"): option.KEY_FORWARDS,
            game.get_game_instance().get_message("next"): option.KEY_BACK,
            game.get_game_instance().get_message("cry"): option.KEY_ACTION
        }
        self.white_pokeball = utils.change_image_color(utils.GRAY_POKEBALL.copy(), (255, 255, 255))
        self.play_sound()

    poly_1 = ((53, 0), (212, 0), (0, 420), (0, 120))
    poly_2 = ((212, 0), (1060, 0), (1060, 180), (848, 600), (0, 600), (0, 420))
    poly_3 = ((1060, 180), (1060, 480), (1007, 600), (848, 600))

    def __del__(self):
        sounds.unload_poke_sound()

    def render(self, display: pygame.Surface):
        display.fill("#ecdcdf")
        pygame.draw.polygon(display, "#f4523b", PokeDexInfo.poly_1)
        pygame.draw.polygon(display, "#fa7248", PokeDexInfo.poly_2)
        pygame.draw.polygon(display, "#f4523b", PokeDexInfo.poly_3)

        utils.draw_button_info(display, **self.keys)

        poke = pokemon.get_pokemon(self.selected + 1)

        # big
        big_im = displayer.get_poke(PokeDex.PATH(str(poke.id_)), 3)
        s_x, s_y = big_im.get_size()
        display.blit(big_im, (250 - s_x // 2, 300 - s_y // 2))

        utils.draw_split_rectangle(display, (477, 60, 530, 50), 0.4, 0.35, "#f0501e", "#000000")
        utils.draw_arrow(display, True, 742, 56, (255, 255, 255), size=2)
        utils.draw_arrow(display, False, 742, 114, (255, 255, 255), size=2)
        y = 62
        im = displayer.get_poke(PokeDex.PATH(str(poke.id_)), 0.7)
        delta_x, delta_y = utils.get_first_color(im)
        x = 480
        display.blit(im, (x, y + 30 - delta_y))
        status = game.get_game_instance().get_pokedex_status(self.selected + 1)
        display.blit(game.FONT_24.render(f"N° {pokemon.to_3_digit(self.selected + 1)}", True, (255, 255, 255)), (x + 50, y + 12))
        display.blit(game.FONT_24.render(poke.get_name(True) if poke.id_ != 0 else "???", True, (255, 255, 255)), (689, y + 12))
        if status != game.POKEDEX_NEVER_SEEN:
            display.blit(
                self.white_pokeball if status == game.POKEDEX_CATCH else utils.POINT_POKEBALL,
                (950, y + 8)
            )

        x, y = 530, 150
        l = 424
        h = 40
        s = 3
        pygame.draw.rect(display, "#dbdbd9", (x, y, l, h,))
        y += h + s
        tx = ("type", "size", "weight", "view")
        tx2 = (None, f'{poke.size} m', f'{poke.weight} Kg', str(game.get_game_instance().get_nb_view(self.selected + 1)))
        for i in range(4):
            pygame.draw.rect(display, "#dbdbd9", (x, y, l // 2, h))
            pygame.draw.rect(display, "#ffffff", (x + l // 2, y, l // 2, h,))
            display.blit(sur := game.FONT_24.render(game.get_game_instance().get_message(tx[i]), True, (0, 0, 0)),
                         utils.get_center(sur, (x, y, l // 2, h)))
            if i != 0:
                display.blit(sur := game.FONT_24.render(tx2[i], True, (0, 0, 0)),
                             utils.get_center(sur, (x + l // 2 + 5, y, l // 2, h), center_x=False))
            else:
                # _type = [game.FONT_16.render(_type.get_name(), True, (255, 255, 255)) for _type in poke.types]
                _x_ = x + l // 2 + 10
                for ii in range(len(poke.types)):
                    utils.draw_type(display, _x_, y + h // 2 - 8, poke.types[ii])
                    _x_ += 106
            y += h
            if i != 3:
                pygame.draw.rect(display, "#f2f2f2", (x, y, l, s))
            y += s
        pygame.draw.rect(display, "#ffffff", (x, y, l, h * 3))
        x += 5
        y += 10
        for p_l in hud.Dialog.split(poke.get_pokedex(), 40):
            display.blit(game.FONT_24.render(p_l, True, (0, 0, 0)), (x, y))
            y += game.FONT_SIZE_24[1] + 5

    def play_sound(self):
        try:
            s = sounds.POKE_SOUND[self.selected + 1]
            if s:
                sound_manager.TAUNT_CHANNEL3.play(s.get())
        except IndexError:
            pass

    def on_key_action(self) -> NoReturn:
        self.play_sound()

    def on_key_y(self, value: float, press: bool) -> NoReturn:
        if press and value < 0 and self.selected > 0:
            v = self.selected
            while v > 0:
                v -= 1
                if game.get_game_instance().get_pokedex_status(v + 1) != game.POKEDEX_NEVER_SEEN:
                    self.selected = v
                    sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
                    self.play_sound()
                    break

        elif press and value > 0 and self.selected < pokemon.NB_POKEMON - 1:
            v = self.selected
            while v < pokemon.NB_POKEMON - 1:
                v += 1
                if game.get_game_instance().get_pokedex_status(v + 1) != game.POKEDEX_NEVER_SEEN:
                    self.selected = v
                    sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
                    self.play_sound()
                    break

    def on_key_escape(self) -> NoReturn:
        self.player.open_menu(PokeDex(self.player, self.selected))
