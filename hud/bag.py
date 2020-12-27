from typing import NoReturn, Callable, Optional
import pygame
import game
import option
import utils
from hud.menu_calass import Menu
import hud.menu as hud_menu
import hud.hud as hud
import pokemon.player_pokemon as player_pokemon
import item.item as item
import sounds
import sound_manager

SORT_NONE = 0
SORT_NAME = 1
SORT_AMOUNT = 2
SORT_AMOUNT_REVERSE = 3

CONDITION_NORMAL = 0
CONDITION_HEAL = 1
CONDITION_BATTLE = 2
CONDITION_GIVE = 3


class Bag(Menu):
    X = lambda y: (y - 1440) / (-120 / 53)

    poly_1 = ((424, 0), (530, 0), (265, 600), (159, 600))
    poly_2 = ((530, 0), (1060, 0), (1060, 600), (265, 600))

    def __init__(self, player,
                 white_list_category: tuple = (),
                 sort: int = SORT_NONE,
                 target: Optional['player_pokemon.PlayerPokemon'] = None,
                 condition: int = CONDITION_NORMAL,
                 use_callback: Optional[Callable[['item.Item', 'player_pokemon.PlayerPokemon'], NoReturn]] = None
                 ):
        super().__init__(player)
        self.use_callback = use_callback
        self.condition = condition
        self.target = target
        self.sort = sort

        if len(white_list_category) > 0:
            black_list_category = item.CATEGORY.copy()
            for e in white_list_category:
                black_list_category.remove(e)
        else:
            black_list_category = ()
        self.black_list_category = black_list_category
        self.open_time = utils.current_milli_time()
        self.keys = {
            game.get_game_instance().get_message("back"): option.KEY_QUITE,
            game.get_game_instance().get_message("sort"): option.KEY_BIKE,
            game.get_game_instance().get_message("select"): option.KEY_ACTION
        }
        self.action_selected = -1
        self.nb_action = 0
        self.category_select = 0
        self.item_selected = 0
        self.poke_select = -1
        self.categories_surface = []
        for a in range(2):
            line = []
            for i in range(len(item.CATEGORY)):
                if item.CATEGORY[i] not in black_list_category:
                    line.append(utils.get_part_i(utils.MENU_IMAGE, (i * 32, 128 + a * 32, i * 32 + 32, 160 + a * 32)))
            self.categories_surface.append(line)
        self.categories = item.CATEGORY.copy()
        for i in black_list_category:
            self.categories.remove(i)
        self.items: list[tuple[item.Item, int]] = []
        self.set_items()

        self.box_text = [(game.FONT_20.render(game.get_game_instance().get_message(t), True, (0, 0, 0)),
                          game.FONT_20.render(game.get_game_instance().get_message(t), True, (255, 255, 255)))
                         for t in ["give", "use", "back"]]

    def set_items(self):
        self.items = list(game.game_instance.inv.get_category(self.categories[self.category_select]).items())
        if self.sort == SORT_AMOUNT:
            self.items = sorted(self.items, key=lambda it: it[1])
        elif self.sort == SORT_AMOUNT_REVERSE:
            self.items = sorted(self.items, key=lambda it: it[1], reverse=True)
        elif self.sort == SORT_NAME:
            self.items = sorted(self.items, key=lambda it: it[0].get_name())

    def render(self, display: pygame.Surface):
        display.fill("#ecdcdf")
        pygame.draw.polygon(display, "#e7a300", Bag.poly_1)
        pygame.draw.polygon(display, "#f2b71f", Bag.poly_2)

        self.draw_team(display)
        self.draw_items(display)

        utils.draw_button_info(display, **self.keys)

    def draw_items(self, display: pygame.Surface):
        center = 795

        x, y = center - (20 * (len(self.categories))), 40
        for i in range(len(self.categories)):
            display.blit(self.categories_surface[self.category_select == i][i], (x, y))
            x += 40

        pygame.draw.polygon(display, "#e38c22",
                            ((center - 100, 80), (center + 100, 80),
                             (center + 100 - 26 * (265 / 600), 106), (center - 100 - 26 * (265 / 600), 106))
                            )
        cat_tx = game.FONT_20.render(
            game.game_instance.get_message(f'item.category.{self.categories[self.category_select]}'),
            True, (255, 255, 255))
        display.blit(cat_tx, (center - cat_tx.get_size()[0] // 2, 93 - cat_tx.get_size()[1] // 2))

        if len(self.items) > 0:
            x = center - 160
            y = 115
            select_y = -1
            for i in range(*self.get_range()):
                if self.item_selected == i:
                    select_y = y
                self.draw_item(display, (x, y), *self.items[i], is_selected=self.item_selected == i)
                y += 40
            y = 445
            try:
                select = self.items[self.item_selected][0]
                pygame.draw.polygon(display, "#e38c22",
                                    ((530, y), (1060, y), (1060, y + 26), (530 - 26 * (265 / 600), y + 26)))
                display.blit(cat_tx, (540, y + 13 - cat_tx.get_size()[1] // 2))
                y += 30
                for p_l in hud.Dialog.split(select.get_lore(), 55):
                    display.blit(game.FONT_16.render(p_l, True, (0, 0, 0)), (545, y))
                    y += game.FONT_SIZE_16[1] + 5
            except IndexError:
                self.item_selected = 0

            if self.action_selected != -1 and self.poke_select == -1:
                it = self.items[self.item_selected]
                opt = []
                if it[0].is_giveable(self.condition):
                    opt.append(self.box_text[0])
                if it[0].is_usable(self.condition):
                    opt.append(self.box_text[1])
                opt.append(self.box_text[2])
                utils.draw_select_box(display, 850, select_y, opt, self.action_selected, 100)

    @staticmethod
    def draw_item(display: pygame.Surface, coord: tuple[int, int], it: 'item.Item', amount: int, is_selected: bool):
        text_color = (255, 255, 255) if is_selected else (0, 0, 0)
        x, y = coord
        if is_selected:
            utils.draw_split_rond_rectangle(display, (x, y, 320, 30), 0.84, 0.8, color=(0, 0, 0), color_2="#e4700b")
        i_s = it.image.get_size()
        display.blit(it.image, (x - 5 - i_s[0] // 2, y + 15 - i_s[1] // 2))
        display.blit(
            tx := game.FONT_20.render(it.get_name(), True, text_color),
            (x + 5, y + 15 - tx.get_size()[1] // 2))
        display.blit(
            tx := game.FONT_20.render('X', True, text_color),
            (x + 270, y + 15 - tx.get_size()[1] // 2))
        display.blit(
            tx := game.FONT_20.render(str(amount), True, text_color),
            (x + 328 - tx.get_size()[0], y + 15 - tx.get_size()[1] // 2))

    def draw_team(self, display: pygame.Surface):
        _x = 106
        _y = 60
        _time = utils.current_milli_time() - self.open_time
        part_time = _time % 2000
        poke_y = 0
        if part_time < 900:
            poke_y = 0
        elif part_time < 950 or 1950 <= part_time:
            poke_y = 1
        elif part_time < 1000 or 1900 <= part_time:
            poke_y = 3
        elif part_time < 1900:
            poke_y = 5

        if self.target is None:
            for i in range(self.player.get_non_null_team_number()):
                if i != self.poke_select:
                    utils.draw_pokemon(display, self.player.team[i], (_x, _y), poke_y)
                else:
                    utils.draw_pokemon(display, self.player.team[i], (_x, _y), poke_y,
                                     color=(0, 0, 0), text_color=(255, 255, 255), need_arrow=True)
                _y += 80
        else:
            utils.draw_pokemon(display, self.target, (_x, _y), poke_y)

    def on_key_action(self) -> NoReturn:
        if self.action_selected == -1:
            nb_items = len(self.items)
            if nb_items > 0:
                # crash prof
                if self.item_selected >= nb_items:
                    self.item_selected = 0
                it = self.items[self.item_selected]
                if it:
                    if nb := it[0].is_giveable(self.condition) + it[0].is_usable(self.condition):
                        sound_manager.start_in_first_empty_taunt(sounds.PLINK)
                        self.action_selected = 0
                        self.nb_action = nb + 1
                    else:
                        sound_manager.start_in_first_empty_taunt(sounds.BLOCK)
        elif self.poke_select != -1:
            it = self.items[self.item_selected]
            poke = self.player.team[self.poke_select]
            if it[0] is None or it[1] <= 0 or poke is None:
                self.on_key_escape()
            g = it[0].is_giveable(self.condition)
            u = it[0].is_usable(self.condition)
            if self.action_selected == 0 and g:
                poke.set_item(it[0])
                sound_manager.start_in_first_empty_taunt(sounds.PLINK)
                self.action_selected = -1
                self.poke_select = -1
                self.set_items()
            elif (self.action_selected == 0 and not g and u) or self.action_selected == 1 and u:
                if not it[0].can_use(poke):
                    sound_manager.start_in_first_empty_taunt(sounds.BLOCK)
                    return
                if self.use_callback is None:
                    it[0].use(poke)
                else:
                    self.use_callback(it[0], poke)
                game.game_instance.inv.remove_items(it[0])
                sound_manager.start_in_first_empty_taunt(sounds.PLINK)
                self.action_selected = -1
                self.poke_select = -1
                self.set_items()
            else:
                self.poke_select = -1
        else:
            it = self.items[self.item_selected]
            if it[0] is None or it[1] <= 0:
                self.on_key_escape()
            g = it[0].is_giveable(self.condition)
            u = it[0].is_usable(self.condition)
            if self.action_selected == 0 and g:
                if self.target is not None:
                    self.target.set_item(it[0])
                    sound_manager.start_in_first_empty_taunt(sounds.PLINK)
                    self.action_selected = -1
                    self.set_items()
                else:
                    self.poke_select = 0
            elif (self.action_selected == 0 and not g and u) or self.action_selected == 1 and u:
                if self.target is not None:
                    if not it[0].can_use(self.target):
                        sound_manager.start_in_first_empty_taunt(sounds.BLOCK)
                        self.poke_select = -1
                        self.action_selected = -1
                        return
                    if self.use_callback is None:
                        it[0].use(self.target)
                    else:
                        self.use_callback(it[0], self.target)
                    game.game_instance.inv.remove_items(it[0])
                    sound_manager.start_in_first_empty_taunt(sounds.PLINK)
                    self.action_selected = -1
                    self.set_items()
                else:
                    self.poke_select = 0
            else:
                self.on_key_escape()

    def on_key_escape(self):
        sound_manager.start_in_first_empty_taunt(sounds.BACK)
        if self.poke_select != -1:
            self.poke_select = -1
        elif self.action_selected != -1:
            self.action_selected = -1
        else:
            self.player.open_menu(hud_menu.MainMenu(self.player))

    def on_key_y(self, value: float, press: bool) -> NoReturn:
        if press:
            if self.action_selected == -1:
                if value < 0 and self.item_selected > 0:
                    sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
                    self.item_selected -= 1
                elif value > 0 and self.item_selected < len(self.items) - 1:
                    sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
                    self.item_selected += 1
            elif self.poke_select != -1:
                if value < 0 and self.poke_select > 0:
                    self.poke_select -= 1
                elif value > 0 and self.poke_select < self.player.get_non_null_team_number() - 1:
                    self.poke_select += 1
            else:
                if value < 0 and self.action_selected > 0:
                    sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
                    self.action_selected -= 1
                elif value > 0 and self.action_selected < self.nb_action - 1:
                    sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
                    self.action_selected += 1

    def on_key_bike(self) -> NoReturn:
        self.sort = (self.sort + 1) % 4
        self.set_items()

    def on_key_x(self, value: float, press: bool) -> NoReturn:
        if press and self.action_selected == -1:
            if value < 0 and self.category_select > 0:
                self.category_select -= 1
                self.item_selected = 0
                sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
                self.set_items()
            elif value > 0 and self.category_select < len(self.categories) - 1:
                self.category_select += 1
                self.item_selected = 0
                sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
                self.set_items()

    def get_range(self) -> tuple[int, int]:
        end = len(self.items)
        a, b = self.item_selected - 4, self.item_selected + 4
        while a < 0:
            a += 1
            b += 1
        while 0 < a > end - 9:
            a -= 1
            b -= 1
        b = min(b + 1, end)
        return a, b