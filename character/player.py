import pygame
import game
import time
import character.character as character

DIALOGUE_MAX_CHAR_LINES = 0
LEFT_X = 0





load = False
DIALOGUE_BOX = None
RIGHT_ARROW = None
DOWN_ARROW = None
SELECT_TOP = None
SELECT_DOWN = None
SELECT_MID = None


def load_hud_item():
    global load, DIALOGUE_BOX, RIGHT_ARROW, DOWN_ARROW, SELECT_TOP, SELECT_DOWN, SELECT_MID, DIALOGUE_MAX_CHAR_LINES
    global LEFT_X
    if not load:
        load = True
        HUD = pygame.image.load("assets/textures/hud/HUD.png")
        DIALOGUE_BOX = character.get_part(HUD, (0, 25, 280, 78), (game.SURFACE_SIZE[0] * 0.9, -1))
        RIGHT_ARROW = character.get_part(HUD, (0, 0, 6, 10))
        DOWN_ARROW = character.get_part(HUD, (6, 0, 16, 6))
        SELECT_TOP = character.get_part(HUD, (0, 10, 74, 15), (game.SURFACE_SIZE[0] * 0.2, -1))
        SELECT_DOWN = character.get_part(HUD, (0, 19, 74, 25), (game.SURFACE_SIZE[0] * 0.2, -1))
        SELECT_MID = character.get_part(HUD, (74, 10, 149, 25), (game.SURFACE_SIZE[0] * 0.2, -1))
        DIALOGUE_MAX_CHAR_LINES = int(game.SURFACE_SIZE[0] * 0.85) // game.FONT_SIZE[0]
        LEFT_X = int(game.SURFACE_SIZE[0] * 0.15)
        del HUD


class Dialog(object):

    def __init__(self, text, speed=50, speed_skip=False, timed=0, need_morph_text=False):
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
            self.text = Dialog.split(t)

        else:
            self.text = text
        self.speed = speed
        self.start_render_line = -1
        self.current_line = 0
        self.show_line = 0
        self.timed = timed
        self.speed_skip = speed_skip
        self.need_enter = False
        self.mono_line = len(self.text) == 1
        self.display_arrow = timed == 0
        self.open_time = current_milli_time()
        self.is_end_line = False

    def render(self, display):
        display.blit(DIALOGUE_BOX, (int(game.SURFACE_SIZE[0] * 0.05), game.SURFACE_SIZE[1] * 0.75))
        t = current_milli_time()

        if 0 < self.timed < (t - self.start_render_line):
            game.game_instance.player.close_dialogue()
            return

        # print(self.current_line)
        if self.start_render_line == -1:
            self.start_render_line = t
        nb_char = (((t - self.start_render_line) // self.speed) + 1) if self.speed > 0 else (len(self.text[self.current_line]) + 1)
        if nb_char > len(self.text[self.current_line]):
            if self.show_line == 0 and not self.mono_line:
                self.show_line = 1
                self.current_line += 1
                self.start_render_line = t
                nb_char = 1
                self.is_end_line = False
            else:
                nb_char = len(self.text[self.current_line])
                if self.display_arrow:
                    display.blit(DOWN_ARROW, (game.SURFACE_SIZE[0] * 0.88, game.SURFACE_SIZE[1] * 0.88))
                self.need_enter = True
                self.is_end_line = True
        else:
            self.is_end_line = False

        if self.show_line == 1:
            l = game.FONT.render(self.text[self.current_line - 1], True, (0, 0, 0))
            display.blit(l, (LEFT_X, int(game.SURFACE_SIZE[1] * 0.78)))

        l = self.text[self.current_line]
        current = game.FONT.render(l[0: nb_char], True, (0, 0, 0))
        display.blit(current, (LEFT_X, int(game.SURFACE_SIZE[1] * 0.78) + ((game.SURFACE_SIZE[1] * 0.2 / 3) * self.show_line)))

    def press_action(self):

        if self.need_enter or self.speed_skip or (self.timed > 0 and current_milli_time() - self.open_time > self.open_time):
            self.need_enter = False
            print(self.current_line, (len(self.text) - 1))
            if self.mono_line or (self.current_line == (len(self.text) - 1)):
                return True
            if self.show_line == 0 and not self.mono_line:
                self.show_line = 1
            self.current_line += 1
            self.start_render_line = current_milli_time()
        return False

    def pres_y(self, up):
        pass

    @staticmethod
    def split(text):
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

    def __init__(self, text, callback, ask, speed=50, speed_skip=False, timed=0, need_morph_text=False):
        """
        ask => dic [Show:value]
        :type ask: dict[str:object]
        """
        super().__init__(text, speed, speed_skip, timed, need_morph_text)
        if len(ask) < 2:
            raise ValueError("len of ask need be > 2")

        self.ask = ask
        self.select = 0
        self.callback = callback

    def render(self, display):
        # todo: fix bug
        super().render(display)
        if self.current_line == len(self.text) - 1 and self.need_enter:
            self.display_arrow = False
            nb_line = len(self.ask)
            draw_x = int(game.SURFACE_SIZE[0] * 0.75)
            draw_y = int(game.SURFACE_SIZE[1] * 0.70)
            display.blit(SELECT_DOWN, (draw_x, draw_y))
            for i in range(nb_line):
                draw_y -= 15
                display.blit(SELECT_MID, (draw_x, draw_y))

            draw_y -= 5
            display.blit(SELECT_TOP, (draw_x, draw_y))

            draw_y += 7
            draw_x += 12
            c = 0
            for key in self.ask:
                if c == self.select:
                    display.blit(RIGHT_ARROW, (draw_x - 8, draw_y))
                font = game.FONT.render(key, True, (0, 0, 0))
                display.blit(font, (draw_x, draw_y))
                draw_y += 14
                c += 1

    def pres_y(self, up):
        if self.current_line == len(self.text) - 1 and self.is_end_line:
            if up:
                self.select = self.select = max(self.select - 1, 0)
            else:
                self.select = min(self.select + 1, len(self.ask) - 1)

    def press_action(self):
        if self.current_line == len(self.text) - 1 and self.is_end_line:
            return not self.callback(self.ask[self.select], self.select)
        else:
            return super().press_action()



class Player(character.Character):

    def __init__(self):
        super().__init__((100, 100), (17, 25))

        self.image = [character.get_part(character.NPC_IMAGE, cord) for cord in [(0, 25, 17, 50), (17, 25, 34, 50), (0, 0, 17, 25), (17, 0, 34, 25)]]
        self.movement = [0, 0]
        self.speed = 1
        self.direction = 2
        self.current_dialogue = None
        self.freeze_time = 0
        self.is_action_press = False
        self.last_close_dialogue = current_milli_time()
        self.current_menu = None

    def have_open_menu(self):
        return self.current_menu

    def open_menu(self, menu):
        # check if can open
        if self.current_dialogue:
            return False
        self.freeze_time = -2
        self.current_menu = menu
        return True

    def close_menu(self):
        self.freeze_time = 2
        self.current_menu = None

    def open_dialogue(self, dialogue, check_last_open=0, over=False):
        """
        :type over: bool
        :type check_last_open: int
        :type dialogue: Dialog
        """
        print("open")
        if self.current_dialogue and not over:
            raise RuntimeError("try open dialog while other is open")

        if 0 < check_last_open and check_last_open > current_milli_time() - self.last_close_dialogue and not over:
            return

        self.freeze_time = -2
        self.current_dialogue = dialogue

    def action_press(self):
        self.is_action_press = True
        if self.current_dialogue:
            if self.current_dialogue.press_action():
                self.close_dialogue()
        if self.current_menu:
            self.current_menu.on_key_action()

    def close_dialogue(self):
        self.last_close_dialogue = current_milli_time()
        self.current_dialogue = None
        self.freeze_time = 2

    def action_unpress(self):
        self.is_action_press = False

    def get_scroll_start(self):
        return int(self.rect.x-(game.SURFACE_SIZE[0]/2) + 8.5), int(self.rect.y - (game.SURFACE_SIZE[1]/2) + 12.5)

    def get_scroll_end(self):
        return int(self.rect.x + (game.SURFACE_SIZE[0] / 2) + 8.5), int(self.rect.y + (game.SURFACE_SIZE[1] / 2) + 12.5)

    def get_image(self):
        return self.image[self.direction]

    def move(self, co):
        """

        :type co: collision.Collision
        """
        move = self.update_direction()
        if move:
            offset_y = (-1 if self.direction == 0 else 1 if self.direction == 2 else 0) * self.speed
            offset_x = (-1 if self.direction == 1 else 1 if self.direction == 3 else 0) * self.speed
        else:
            offset_x, offset_y = 0, 0
        box = self.get_box()

        col = co.get_collision(box, offset_x, offset_y)
        if self.freeze_time != 0:
            return
        if col and (not game.game_instance.ignore_collision):
            self.set_render_from_scroll(game.came_scroll, col)
        else:
            self.rect.x += offset_x
            self.rect.y += offset_y

    def update_direction(self):
        if self.movement[1] < 0:
            self.direction = 0
        elif self.movement[1] > 0:
            self.direction = 2
        elif self.movement[0] > 0:
            self.direction = 3
        elif self.movement[0] < 0:
            self.direction = 1
        else:
            return False
        return True

    def on_key_x(self, value, up):
        if up:
            self.movement[0] -= value
        else:
            self.movement[0] += value
        if self.current_menu:
            self.current_menu.on_key_x(value, not up)

    def on_key_y(self, value, up):
        if up:
            self.movement[1] -= value
        else:
            self.movement[1] += value
        if self.current_menu:
            self.current_menu.on_key_y(value, not up)
        if self.current_dialogue and not up:
            self.current_dialogue.pres_y(value < 0)

def current_milli_time():
    return int(round(time.time() * 1000))


