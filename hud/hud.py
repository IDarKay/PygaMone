from typing import NoReturn, Callable, Iterable
import character.character as character
from utils import *

DIALOGUE_MAX_CHAR_LINES: int = 0
LEFT_X: int = 0

load: bool = False
DIALOGUE_BOX: pygame.Surface = None
RIGHT_ARROW: pygame.Surface = None
DOWN_ARROW: pygame.Surface = None
SELECT_TOP: pygame.Surface = None
SELECT_DOWN: pygame.Surface = None
SELECT_MID: pygame.Surface = None


def load_hud_item():
    global load, DIALOGUE_BOX, RIGHT_ARROW, DOWN_ARROW, SELECT_TOP, SELECT_DOWN, SELECT_MID, DIALOGUE_MAX_CHAR_LINES
    global LEFT_X
    if not load:
        load = True
        HUD: pygame.Surface = pygame.image.load("assets/textures/hud/HUD.png")
        DIALOGUE_BOX = get_part_i(HUD, (0, 25, 280, 78), (game.SURFACE_SIZE[0] * 0.9, game.SURFACE_SIZE[1] * 0.2))
        RIGHT_ARROW = get_part_i(HUD, (0, 0, 6, 10), (12, 20))
        DOWN_ARROW = get_part_i(HUD, (6, 0, 16, 6), (20, 12))
        SELECT_TOP = get_part_i(HUD, (0, 10, 74, 15), (game.SURFACE_SIZE[0] * 0.2, game.SURFACE_SIZE[1] * 0.05))
        SELECT_DOWN = get_part_i(HUD, (0, 19, 74, 25), (game.SURFACE_SIZE[0] * 0.2, game.SURFACE_SIZE[1] * 0.05))
        SELECT_MID = get_part_i(HUD, (74, 10, 149, 25), (game.SURFACE_SIZE[0] * 0.2, game.SURFACE_SIZE[1] * 0.08))
        DIALOGUE_MAX_CHAR_LINES = int(game.SURFACE_SIZE[0] * 0.85) // game.FONT_SIZE_16[0]
        LEFT_X = int(game.SURFACE_SIZE[0] * 0.15)
        del HUD


class Dialog(object):

    def __init__(self, text: Any, speed: int = 50, speed_skip: bool = False, timed: int = 0,
                 need_morph_text: bool = False, none_skip: bool = False):
        """

        text => sting list with each lines or sting lang key with need_morph_text=True
        speed => nb of ms in each char show (-1 for instant)
        speed_skip => can skip lines with action click default False
        timed => none skip and auto closable after timed ms need only 2 text line or less and speed_skip = False
        :type timed: int
        :type speed_skip: bool
        :type speed: int
        """
        if speed_skip and timed != 0:
            raise ValueError("Can't create Dialogue box with speed_skip and timed !=0")
        if timed != 0 and len(text) > 2:
            raise ValueError("Can't create Dialogue with timed !=0 and len(text) > 2")
        if need_morph_text:
            t = game.game_instance.get_message(text)
            self._text: List[str] = Dialog.split(t)

        else:
            self._text: List[str] = text
        self._speed: int = speed
        self._start_render_line: int = -1
        self._current_line: int = 0
        self._show_line: int = 0
        self._timed: int = timed
        self._speed_skip: bool = speed_skip
        self._need_enter: bool = False
        self._mono_line: int = len(self._text) == 1
        self._display_arrow: int = timed == 0 and not none_skip
        self._open_time: int = current_milli_time()
        self._is_end_line: bool = False
        self.none_skip: bool = none_skip

    def render(self, display: pygame.Surface) -> NoReturn:
        display.blit(DIALOGUE_BOX, (int(game.SURFACE_SIZE[0] * 0.05), game.SURFACE_SIZE[1] * 0.75))
        t = current_milli_time()

        if 0 < self._timed < (t - self._start_render_line):
            game.game_instance.player.close_dialogue()
            return

        # print(self.current_line)
        if self._start_render_line == -1:
            self._start_render_line = t
        nb_char = (((t - self._start_render_line) // self._speed) + 1) if self._speed > 0 else (len(self._text[self._current_line]) + 1)
        if nb_char > len(self._text[self._current_line]) or self._is_end_line:
            if self._show_line == 0 and not self._mono_line:
                self._show_line = 1
                self._current_line += 1
                self._start_render_line = t
                nb_char = 1
            else:
                nb_char = len(self._text[self._current_line])
                if self._display_arrow:
                    display.blit(DOWN_ARROW, (game.SURFACE_SIZE[0] * 0.88, game.SURFACE_SIZE[1] * 0.88))
                self._need_enter = True
                self._is_end_line = True

        if self._show_line == 1:
            l = game.FONT_24.render(self._text[self._current_line - 1], True, (0, 0, 0))
            display.blit(l, (LEFT_X, int(game.SURFACE_SIZE[1] * 0.78)))

        l = self._text[self._current_line]
        current = game.FONT_24.render(l[0: nb_char], True, (0, 0, 0))
        display.blit(current, (LEFT_X, int(game.SURFACE_SIZE[1] * 0.78) + ((game.SURFACE_SIZE[1] * 0.2 / 3) * self._show_line)))

    def press_action(self) -> NoReturn:

        if not self.none_skip and (self._need_enter or self._speed_skip or (self._timed > 0 and current_milli_time() - self._open_time > self._open_time)):
            self._need_enter = False
            if self._mono_line or (self._current_line == (len(self._text) - 1)):
                if self._speed and not self._is_end_line:
                    self._is_end_line = True
                    return False
                else:
                    return True
            self._is_end_line = False
            if self._show_line == 0 and not self._mono_line:
                self._show_line = 1
            self._current_line += 1
            self._start_render_line = current_milli_time()
        return False

    def pres_y(self, up: bool) -> NoReturn:
        pass

    @staticmethod
    def split(text: str) -> List[str]:
        split_text = text.split()
        split_line = []
        line = ""

        for i in split_text:
            if (len(line) + len(i)) > DIALOGUE_MAX_CHAR_LINES > len(i) or i == '[l]':
                split_line.append(line)
                line = ""
            if i != '[l]':
                line += i + " "
        if len(line) != 0:
            split_line.append(line)
        return split_line


class QuestionDialog(Dialog):

    def __init__(self, text: Any, callback: Callable[[str, int], NoReturn], ask: Iterable[str], speed: int = 50,
                 speed_skip: bool = False, timed: int = 0, need_morph_text: bool = False):
        """
        ask => dic [Show:value]
        :type ask: dict[str:object]
        """
        super().__init__(text, speed, speed_skip, timed, need_morph_text)
        if len(ask) < 2:
            raise ValueError("len of ask need be > 2")

        self.__ask = ask
        self.__select = 0
        self.__callback = callback

    def render(self, display: pygame.Surface):
        super().render(display)
        if self._current_line == len(self._text) - 1 and self._need_enter:
            self._display_arrow = False
            nb_line = len(self.__ask)
            draw_x = int(game.SURFACE_SIZE[0] * 0.75)
            draw_y = int(game.SURFACE_SIZE[1] * 0.68)
            display.blit(SELECT_DOWN, (draw_x, draw_y))
            for i in range(nb_line):
                draw_y -= game.SURFACE_SIZE[1] * 0.08
                display.blit(SELECT_MID, (draw_x, draw_y))

            draw_y -= game.SURFACE_SIZE[1] * 0.05
            display.blit(SELECT_TOP, (draw_x, draw_y))

            draw_y += game.SURFACE_SIZE[1] * 0.06
            draw_x += 35
            c = 0
            for key in self.__ask:
                if c == self.__select:
                    display.blit(RIGHT_ARROW, (draw_x - 18, draw_y + 3))
                font = game.FONT_24.render(key, True, (0, 0, 0))
                display.blit(font, (draw_x, draw_y))
                draw_y += game.SURFACE_SIZE[1] * 0.08
                c += 1

    def pres_y(self, up: bool) -> NoReturn:
        if self._current_line == len(self._text) - 1 and self._need_enter:
            if up:
                self.__select = self.__select = max(self.__select - 1, 0)
            else:
                self.__select = min(self.__select + 1, len(self.__ask) - 1)

    def press_action(self) -> NoReturn:
        if self._current_line == len(self._text) - 1 and self._need_enter:
            return not self.__callback(self.__ask[self.__select], self.__select)
        else:
            return super().press_action()
