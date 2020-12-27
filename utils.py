from typing import Dict, List, Any, Tuple, Optional, Union, TypeVar, Callable, NoReturn
import time
import pygame
import game_error as err
import game
import pokemon.pokemon_type as pokemon_type
import pokemon.player_pokemon as player_pokemon
import main
import numpy as np

color_t = Union[tuple[int, int, int], tuple[int, int, int, int], str]

MENU_IMAGE = None
ARROW = None
RED_POKEBALL = None
GRAY_POKEBALL = None
POINT_POKEBALL = None


def force():
    global MENU_IMAGE, ARROW, RED_POKEBALL, GRAY_POKEBALL, POINT_POKEBALL
    MENU_IMAGE = pygame.image.load("assets/textures/hud/menu.png").convert_alpha()
    ARROW = get_part_i(MENU_IMAGE, (0, 64, 22, 91))
    RED_POKEBALL = get_part_i(MENU_IMAGE, (32, 91, 64, 123))
    GRAY_POKEBALL = get_part_i(MENU_IMAGE, (0, 91, 32, 123))
    POINT_POKEBALL = get_part_i(MENU_IMAGE, (64, 91, 96, 123))


def get_part_i(image: pygame.Surface, coord: Tuple[float, float, float, float],
               transform: Tuple[int, int] = (0, 0), flip: Tuple[bool, bool] = (False, False)) -> pygame.Surface:
    s = pygame.Surface((coord[2] - coord[0], coord[3] - coord[1]), pygame.SRCALPHA)
    s.blit(image, (0, 0), pygame.Rect(coord))
    if transform != (0, 0):
        copy_transform = [transform[0], transform[1]]
        if copy_transform[0] == -1:
            copy_transform[0] = coord[2] - coord[0]
        if copy_transform[1] == -1:
            copy_transform[1] = coord[3] - coord[1]
        transform = int(copy_transform[0]), int(copy_transform[1])
        s = pygame.transform.scale(s, transform)
    if flip != (False, False):
        s = pygame.transform.flip(s, flip[0], flip[1])
    return s


def draw_pokemon(display: pygame.Surface, poke: 'player_pokemon.PlayerPokemon',
                 coord: tuple[int, int], poke_y: int,
                 color: color_t = (255, 255, 255),
                 text_color: color_t = (0, 0, 0),
                 need_arrow: bool = False
                 ):
    x, y = coord
    draw_rond_rectangle(display, x, y, 49, 212, color)
    if poke:
        heal, max_heal = poke.heal, poke.get_max_heal()
        draw_progress_bar(display, (x + 42, y + 21), (170, 5), (52, 56, 61), (45, 181, 4), heal / max_heal)
        display.blit(poke.get_front_image(0.5), (x - 20, y + 4 - poke_y))
        if poke.item:
            display.blit(poke.item.image, (x + 5, y + 25))
        display.blit(
            game.FONT_16.render(f'{heal}/{max_heal}', True, text_color),
            (x + 42, y + 30))
        display.blit(
            tx := game.FONT_16.render(f'Lvl {poke.lvl}', True, text_color),
            (x + 212 - tx.get_size()[0], y + 30))
        display.blit(
            game.FONT_20.render(poke.get_name(True), True, text_color),
            (x + 42, y + 2))
        display.blit(pygame.transform.scale(poke.poke_ball.image, (16, 16)), (x + 212, y + 5))

        im = poke.combat_status.get_all_image()
        if len(im) > 0:
            current = im[min(current_milli_time() % (len(im) * 2000) // 2000, len(im) - 1)]
            draw_rond_rectangle(display, x + 150, y + 8, 12, 50, current[1])
            display.blit(tx := game.FONT_12.render(current[0], True, (255, 255, 255)),
                         (x + 175 - tx.get_size()[0] // 2, y + 14 - tx.get_size()[1] // 2))

        if need_arrow:
            display.blit(ARROW, (x - 50, y + 2))


def current_milli_time() -> int:
    return int(round(time.time() * 1000))


def time_to_string(t: int) -> str:
    hours = t // (60 * 60)
    t -= hours * (60 * 60)
    minutes = t // 60
    t -= minutes * 60
    return str(hours) + ":" + ("0" if minutes < 9 else "") + str(minutes)


def draw_select_box(display: pygame.Surface, _x: float, _y: float,
                    text: List[Tuple[pygame.Surface, pygame.Surface]],
                    selected: int, width: int = 100,
                    over_color: color_t = (0, 0, 0),
                    bg_color: color_t = (255, 255, 255),
                    bg_border: color_t = (100, 100, 100)):

    max_width = max(text, key=lambda s: s[0].get_size()[0])[0].get_size()[0] + 20
    if width < max_width:
        width = max_width

    _h = 20 + 28 * len(text)

    pygame.draw.rect(display, bg_color, pygame.Rect(_x, _y, width, _h), border_radius=10)
    pygame.draw.rect(display, bg_border, pygame.Rect(_x - 1, _y - 1, width + 1, _h + 1), border_radius=10, width=1)
    _y += 10
    _x += 10
    for i in range(len(text)):
        if selected == i:
            draw_rond_rectangle(display, _x + 5, _y, 20, width - 30, over_color)
        _text = text[i][1 if selected == i else 0]
        display.blit(_text, (_x, _y))
        _y += 28


def draw_rond_rectangle(display: pygame.Surface, _x: float, _y: float,
                        height: float, width: float, color: color_t):
    height *= 0.5
    pygame.draw.circle(display, color, (_x, _y + height), height)
    pygame.draw.circle(display, color, (_x + width, _y + height), height)
    pygame.draw.rect(display, color, pygame.Rect(_x, _y, width, height * 2))


# R = TypeVar('R', pygame.Rect, pygame.RectType, tuple[int, int, int, int])

def draw_split_rectangle(display: pygame.Surface, rect: tuple[int, int, int, int], split_up: float, split_down: float,
                              color: color_t, color_2: color_t):
    pygame.draw.rect(display, color, rect)
    poly = (
        (rect[0] + rect[2] * split_up, rect[1]),
        (rect[0] + rect[2], rect[1]),
        (rect[0] + rect[2], rect[1] + rect[3] - 1),
        (rect[0] + rect[2] * split_down, rect[1] + rect[3] - 1),
    )
    pygame.draw.polygon(display, color_2, poly)


def draw_split_rond_rectangle(display: pygame.Surface, rect: tuple[int, int, int, int], split_up: float, split_down: float,
                              color: color_t, color_2: color_t):
    height = rect[3] * 0.5
    pygame.draw.circle(display, color, (rect[0], rect[1] + height), height)
    pygame.draw.circle(display, color_2, (rect[0] + rect[2], rect[1] + height), height)
    draw_split_rectangle(display, rect, split_up, split_down, color, color_2)


def get_args(data: Dict[str, Any], key: str, _id: Any, default=None, type_check=None, _type="pokmon") -> Any:
    value = None
    if default is not None:
        value = data[key] if key in data else None if default == "NONE" else default
    else:
        if key not in data:
            raise err.PokemonParseError("No {} value for a {} ({}) !".format(key, _type, _id))
        value = data[key]
    if type_check:
        if value and not isinstance(value, type_check):
            raise err.PokemonParseError(
                "Invalid var type for {} need be {} for {} ({})".format(key, type_check, _type, _id))
    return value


def draw_type(display: pygame.Surface, _x: float, _y: float, _type: 'pokemon_type.Type'):
    pygame.draw.rect(display, (0, 0, 0), pygame.Rect(_x, _y, 85, 16),
                     border_radius=2)
    display.blit(_type.image, (_x, _y))
    display.blit(game.FONT_16.render(_type.get_name().upper(), True, (255, 255, 255)), (_x + 26, _y + 1))


def draw_ability(display: pygame.Surface, coord: Tuple[int, int], p_ability: 'player_pokemon.PokemonAbility',
                 color_1: color_t = (255, 255, 255), color_2: color_t = (70, 68, 69),
                 text_color_1: color_t = (0, 0, 0), text_color_2: color_t = (255, 255, 255)):
    draw_split_rond_rectangle(display, (coord[0], coord[1], 320, 34), 0.85, 0.8, color_1, color_2)
    display.blit(game.FONT_20.render(p_ability.ability.get_name() if p_ability else "-------------", True, text_color_1),
                 (coord[0] + 5, coord[1] + 6))
    if p_ability:
        draw_type(display, coord[0] + 160, coord[1] + 8,  p_ability.ability.type)

    pp = "{}/{}".format(p_ability.pp, p_ability.max_pp) if p_ability else "--/--"
    move = game.FONT_SIZE_20[0] * (1.8 if not p_ability else (2.5 if p_ability.pp > 9 else 1.5))
    display.blit(game.FONT_20.render(pp, True, text_color_2),
                 (coord[0] + 304 - move, coord[1] + 6))
    pass


def draw_ability_2(display: pygame.Surface, coord: Tuple[int, int],
                   p_ability: 'player_pokemon.PokemonAbility', border: bool = False):
    type_color = p_ability.ability.type.image.get_at((0, 0)) if p_ability else (255, 255, 255)
    if border:
        draw_rond_rectangle(display, coord[0] - 3, coord[1] - 3, 46, 226, (0, 0, 0))
    draw_split_rond_rectangle(display, (coord[0], coord[1],  220, 40), 0.75, 0.67, type_color, (0, 0, 0))
    # draw_rond_rectangle(display, coord[0] + 180, coord[1], 40, 40, (0, 0, 0))
    if p_ability:
        display.blit(pygame.transform.scale(p_ability.ability.type.image, (44, 32)), (coord[0] - 10, coord[1] + 4), pygame.Rect(0, 0, 32, 32))

    display.blit(tx := game.FONT_20.render(p_ability.ability.get_name() if p_ability else "-------------", True, (0, 0, 0)),
                 (coord[0] + 23, coord[1] + 20 - tx.get_size()[1] // 2))
    pp = "{}/{}".format(p_ability.pp, p_ability.max_pp) if p_ability else "--/--"

    display.blit(tx := game.FONT_20.render(pp, True, (255, 255, 255) if p_ability is None or p_ability.pp > 0 else (166, 26, 2)),
                 (coord[0] + 193 - tx.get_size()[0] // 2, coord[1] + 20 - tx.get_size()[1] // 2))


def draw_progress_bar(display: pygame.Surface, coord: Tuple[float, float], size: Tuple[float, float],
                      bg_color: color_t, color: color_t, progress: float):

    pygame.draw.rect(display, bg_color, pygame.Rect(coord[0], coord[1], size[0], size[1]))
    pygame.draw.rect(display, color, pygame.Rect(coord[0], coord[1], size[0] * progress, size[1]))


def min_max(min_v: int, value: int, max_v: int) -> int:
    return min_v if value < min_v else max_v if value > max_v else value


def hexa_color_to_rgb(hexa: str) -> Tuple[int, int, int]:
    if hexa[0] == '#':
        hexa = hexa[1:]
    return int('0x' + hexa[0:2], 16), int('0x' + hexa[2:4], 16), int('0x' + hexa[4:6], 16)


def change_image_color(surface: pygame.Surface, color: tuple[int, int, int]) -> pygame.Surface:
    size = surface.get_size()
    for x in range(size[0]):
        for y in range(size[1]):
            px = surface.get_at((x, y))
            if px[3] != 0:
                surface.set_at((x, y), color)
    return surface


def color_image(surface: pygame.Surface, color: color_t) -> pygame.Surface:
    if isinstance(color, str):
        color = hexa_color_to_rgb(color)
    alpha = (100 if len(color) == 3 else color[3]) / 255
    size = surface.get_size()
    for x in range(size[0]):
        for y in range(size[1]):
            px = surface.get_at((x, y))
            if px[3] != 0:
                al = (1 - alpha)
                f_px = (
                    int(color[0] * alpha + px[0] * al),
                    int(color[1] * alpha + px[1] * al),
                    int(color[2] * alpha + px[2] * al)
                )
                surface.set_at((x, y), f_px)
    return surface


def get_first_color(surface: pygame.Surface) -> Tuple[int, int]:

    size = surface.get_size()

    def _y_():
        for y_ in range(size[1] - 1, -1, -1):
            for x_ in range(size[0] - 1, -1, -1):
                if surface.get_at((x_, y_))[3] != 0:
                    return y_
        return 0

    def _x_():
        for x_ in range(size[0] - 1, -1, -1):
            for y_ in range(size[1] - 1, -1, -1):
                if surface.get_at((x_, y_))[3] != 0:
                    return x_
        return 0

    x = _x_()
    y = _y_()
    return x, y


GAMEPAD_KEYS = [
    'A', 'B', 'X', 'Y', 'L1', 'R1', '-', '+', 'R', 'L', '?', '\u2191', '\u2193', '`\u2190', '\u2191'
]


def remove_holes(surface, background=(0, 0, 0)):
    """
    Removes holes caused by aliasing.

    The function locates pixels of color 'background' that are surrounded by pixels of different colors and set them to
    the average of their neighbours. Won't fix pixels with 2 or less adjacent pixels.

    Args:
        surface (pygame.Surface): the pygame.Surface to anti-aliasing.
        background (3 element list or tuple): the color of the holes.

    Returns:
        anti-aliased pygame.Surface.
    """
    width, height = surface.get_size()
    array = pygame.surfarray.array3d(surface)
    contains_background = (array == background).all(axis=2)

    neighbours = (0, 1), (0, -1), (1, 0), (-1, 0)

    for row in range(1, height-1):
        for col in range(1, width-1):
            if contains_background[row, col]:
                average = np.zeros(shape=(1, 3), dtype=np.uint16)
                elements = 0
                for y, x in neighbours:
                    if not contains_background[row+y, col+x]:
                        elements += 1
                        average += array[row+y, col+x]
                if elements > 2:  # Only apply average if more than 2 neighbours is not of background color.
                    array[row, col] = average // elements

    return pygame.surfarray.make_surface(array)


def draw_arrow(display: pygame.Surface, up: bool, x: int, y: int, color: color_t, size=1):
    l = 10 * size
    h = 5 * size
    x -= l // 2
    p = (x, y), (x + l, y), (x + l // 2, (y - h) if up else (y + h))
    pygame.draw.polygon(display, color, p)


def get_center(surface: pygame.Surface, rec: tuple[int, int, int, int], center_x=True, center_y=True) -> tuple[int, int]:
    size = surface.get_size()
    x = rec[0] + rec[2] // 2 - size[0] // 2 if center_x else rec[0]
    y = rec[1] + rec[3] // 2 - size[1] // 2 if center_y else rec[1]
    return x, y


def draw_button_info(surface: pygame.Surface, **keys):
    pygame.draw.polygon(surface, "#000000", ((0, 570), (1060, 570), (1060, 600), (0, 600)))
    x = 1040
    h = 30
    c_y = 600 - h / 2
    y = int(c_y - game.FONT_SIZE_20[1] / 2)
    is_board = game.get_game_instance().last_input_type == game.INPUT_TYPE_KEYBOARD == 0
    for name, key in keys.items():
        key_char = (pygame.key.name(key[0]) if is_board else GAMEPAD_KEYS[key[2]]).upper()
        txt = game.FONT_20.render(name, True, (255, 255, 255))
        x -= txt.get_size()[0]
        surface.blit(txt, (x, y))
        mt_char = len(key_char) > 1
        font = game.FONT_20 if mt_char else game.FONT_24
        key = font.render(key_char, True, (0, 0, 0))
        size = key.get_size()
        if mt_char:
            w = size[0]
            x -= w + 15
            draw_rond_rectangle(surface, x, 600 - h + 4, h - 8, w, (255, 255, 255))
            surface.blit(key, (x, y))
            x -= 20
        else:
            x -= h // 2 + 2
            pygame.draw.circle(surface, (255, 255, 255), (x, c_y), h // 2 - 2)
            surface.blit(key, (x - size[0] // 2, c_y - size[1] // 2))
            x -= h // 2 + 2


def draw_table(display: pygame.Surface, /, y: int, x: int, h: int, c: int, l: int, half: int, size: int,
               left_getter: Callable[[int], str], right_getter: Callable[[int, int, int], Optional[str]],
               color_1: color_t = "#dcdcdc", color_2: color_t = "#ffffff",
               split_color_1: Optional[color_t] = "#d2d2d2", split_color_2: Optional[color_t] = "#f3f3f3",
               text_color_1: color_t = (0, 0, 0), text_color_2: color_t = (0, 0, 0),
               font: Optional[pygame.font.Font] = None
               ) -> int:
    """
    draw a table
    @param display: the surface where draw
    @param y: the Y start pf the table
    @param x: the start x
    @param h: the height of each case
    @param c: the height of the split
    @param l: the length of the table
    @param size: number of row of the table
    @param half: where cut the table in 2
    @param left_getter: text getter for the left collum parm: i : the row number
    @param right_getter: text getter for the right collum parm: i : the row number, x = current x, y = current y
            return the sting to draw or None for nothing
    @param color_1: the color of the left side
    @param color_2: the color of the right side
    @param split_color_1: the color of the left side of the split None to don"t draw
    @param split_color_2: the color of the right side of the split None to don"t draw
    @param text_color_1: the color of the left text
    @param text_color_2:  the color of the right text
    @param font: use font to draw text

    @return: Nothing
    """
    if font is None:
        font = game.FONT_24
    for i in range(size):
        pygame.draw.rect(display, color_1, (x, y, half, h))
        pygame.draw.rect(display, color_2, (x + half, y, l - half, h))
        left_back = left_getter(i)
        if left_back:
            display.blit(r_t := font.render(left_back, True, text_color_1),
                         (x + (half - r_t.get_size()[0]) // 2, y + (h - r_t.get_size()[1]) // 2))
        right_back = right_getter(i, x + half + 10, y)
        if right_back:
            display.blit(r_t := font.render(right_back, True, text_color_2),
                         (x + half + 10, y + (h - r_t.get_size()[1]) // 2))
        y += h
        if i != 6:
            if split_color_1:
                pygame.draw.rect(display, split_color_1, (x, y, half, c))
            if split_color_2:
                pygame.draw.rect(display, split_color_2, (x + half, y, l - half, c))
            y += c
    return y