from typing import Dict, List, Any, Tuple
import time
import pygame
import game_error as err
import game
import pokemon.pokemon_type as pokemon_type
import pokemon.player_pokemon as player_pokemon


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
                    over_color=(0, 0, 0), bg_color=(255, 255, 255), bg_border=(100, 100, 100)):

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
                        height: float, width: float, color: Tuple[int, int, int]):
    height *= 0.5
    pygame.draw.circle(display, color, (_x, _y + height), height)
    pygame.draw.circle(display, color, (_x + width, _y + height), height)
    pygame.draw.rect(display, color, pygame.Rect(_x, _y, width, height * 2))


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
    display.blit(game.FONT_16.render(_type.get_name(), True, (255, 255, 255)), (_x + 26, _y))


def draw_ability(display: pygame.Surface, coord: Tuple[float, float], p_ability: 'player_pokemon.PokemonAbility'):
    draw_rond_rectangle(display, coord[0], coord[1], 34, game.SCREEN_SIZE[0] * 0.2, (255, 255, 255))
    draw_rond_rectangle(display, coord[0] + game.SCREEN_SIZE[0] * 0.18, coord[1], 34, 40, (70, 68, 69))
    display.blit(game.FONT_20.render(p_ability.ability.get_name() if p_ability else "-------------", True, (0, 0, 0)),
                 (coord[0] + 5, coord[1] + 6))
    if p_ability:
        draw_type(display, coord[0] + game.SCREEN_SIZE[0] * 0.11, coord[1] + 8,  p_ability.ability.type)

    pp = "{}/{}".format(p_ability.pp, p_ability.max_pp) if p_ability else "--/--"
    move = game.FONT_SIZE_20[0] * (1.8 if not p_ability else (2.5 if p_ability.pp > 9 else 1.5))
    display.blit(game.FONT_20.render(pp, True, (255, 255, 255)),
                 (coord[0] + game.SCREEN_SIZE[0] * 0.19 - move, coord[1] + 6))
    pass


def draw_progress_bar(display: pygame.Surface, coord: Tuple[float, float], size: Tuple[float, float],
                      bg_color: Tuple[int, int, int], color: Tuple[int, int, int], progress: float):

    pygame.draw.rect(display, bg_color, pygame.Rect(coord[0], coord[1], size[0], size[1]))
    pygame.draw.rect(display, color, pygame.Rect(coord[0], coord[1], size[0] * progress, size[1]))


def min_max(min_v: int, value:int , max_v: int) -> int:
    return min_v if value < min_v else max_v if value > max_v else value


def get_part_i(image: pygame.Surface, coord: Tuple[float, float, float, float],
               transform: Tuple[int, int] = (0, 0)) -> pygame.Surface:
    s = pygame.Surface((coord[2] - coord[0], coord[3] - coord[1]), pygame.SRCALPHA)
    s.blit(image, (0, 0), pygame.Rect(coord))
    if transform != (0, 0):
        copy_transform = [transform[0], transform[1]]
        if copy_transform[0] == -1:
            copy_transform[0] = coord[2] - coord[0]
        if copy_transform[1] == -1:
            copy_transform[1] = coord[3] - coord[1]
        transform = int(copy_transform[0]), int(copy_transform[1])
        return pygame.transform.scale(s, transform)
    return s