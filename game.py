from typing import Optional, NoReturn
import pygame
import level
import collision
import character.player as player
import json
import time
import pokemon.pokemon as pokemon
import hud.hud as hud
import pokemon.abilitys_ as abilitys_
import item.items as items
import main
import sys
import pokemon.battle.wild_start as wild_start
import utils
import option
import pokemon.status.status as status_
import sounds

screen = None

CASE_SIZE = 32

# SCREEN_SIZE = (1920, 1080)
SURFACE_SIZE = (1060, 600)

DIRECTION = ["top", "left", "down", "right"]

game_instance: Optional['Game'] = None

FONT_12: pygame.font.Font = None
FONT_16: pygame.font.Font = None
FONT_20: pygame.font.Font = None
FONT_24: pygame.font.Font = None
FONT_SIZE_12 = (0, 0)
FONT_SIZE_16 = (0, 0)
FONT_SIZE_20 = (0, 0)
FONT_SIZE_24 = (0, 0)

came_scroll = (0, 0)

POKEDEX_NEVER_SEEN = 0
POKEDEX_SEEN = 1
POKEDEX_CATCH = 2

INPUT_TYPE_KEYBOARD = 0
INPUT_TYPE_GAMEPAD = 1


class Cache(object):

    def __init__(self):
        self.cache = {}

    def clear(self):
        self.cache.clear()

    def put(self, key, value):
        self.cache[key] = value

    def put_return(self, key, value):
        self.cache[key] = value
        return value

    def have(self, key):
        return key in self.cache

    def get_or_null(self, key):
        try:
            return self.cache[key]
        except KeyError:
            return None

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        else:
            raise KeyError("No value load for key {}".format(key))


class RenderTickCounter(object):

    def __init__(self, tps: float, time_millis: int):
        self.tick_time = 1000.0 / tps
        self.prevTimeMillis = time_millis
        self.lastFrameDuration = 0
        self.tickDelta = 0

    def begin_render_tick(self, time_millis: int) -> int:
        self.lastFrameDuration = (time_millis - self.prevTimeMillis) / self.tick_time
        self.prevTimeMillis = time_millis
        self.tickDelta += self.lastFrameDuration
        i = int(self.tickDelta)
        self.tickDelta -= float(i)
        return i


IMAGE_CACHE = Cache()
DISPLAYER_CACHE = Cache()
POKE_CACHE = Cache()
POKE_SOUND_CACHE = Cache()


class Game(object):

    def __init__(self, screen_s: pygame.Surface):
        self.screen = screen_s

        # asset load
        global FONT_12, FONT_SIZE_12, FONT_16, FONT_SIZE_16, FONT_20, FONT_SIZE_20, FONT_24, FONT_SIZE_24
        FONT_12 = pygame.font.Font("assets/font/Togalite-Regular.otf", 12)
        FONT_16 = pygame.font.Font("assets/font/Togalite-Medium.otf", 16)
        FONT_20 = pygame.font.Font("assets/font/Togalite-Medium.otf", 20)
        FONT_24 = pygame.font.Font("assets/font/Togalite-Medium.otf", 24)
        # FONT_24 = pygame.font.Font("assets/font/MyFont-Regular.otf", 24)
        FONT_SIZE_12 = FONT_12.size('X')
        FONT_SIZE_16 = FONT_16.size('X')
        FONT_SIZE_20 = FONT_20.size('X')
        FONT_SIZE_24 = FONT_24.size('X')
        self.lang_ios = "en"
        self.lang = {}
        self.poke_lang = {}
        self.ability_lang = {}
        self.save_name = ""
        self._save = {}
        self.load_save("save")
        # todo: lang selector
        self.load_lang(self.lang_ios)
        self.load_poke_lang(self.lang_ios)
        self.load_ability_lang(self.lang_ios)
        sounds.load_poke_sound()
        items.load()
        status_.load()
        abilitys_.load()
        pokemon.Pokemon.load_pokemons()
        hud.load_hud_item()
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        pokemon.init_translate(self)
        # ============
        self.__render_tick_counter = RenderTickCounter(20.00, 0)
        global game_instance
        game_instance = self

        self.display: 'pygame.Surface' = pygame.Surface(SURFACE_SIZE, pygame.HWSURFACE | pygame.SRCALPHA)
        self.player: 'player.Player' = player.Player(self)

        self.trigger_cache = Cache()

        self.level = None
        load_coord = self.get_save_value("last_level_coord", [100, 100])
        self.load_level(self.get_save_value("last_level", "level_1"), load_coord[0], load_coord[1])

        self.clock = pygame.time.Clock()
        self.collision = collision.Collision()
        self.debug = False
        self.ignore_collision = False
        self.time_matrix = [1] * 10
        running = True
        self.direct_battle: list[bool, bool] = ["--direct_battle" in sys.argv, True]
        self.last_input_type = INPUT_TYPE_KEYBOARD
        while self.tick():
            self.clock.tick(60)
        print("end")

    def load_lang(self, lang):
        with open("assets/lang/text/{}.json".format(lang), 'r', encoding='utf-8') as file:
            self.lang = json.load(file)

    def load_poke_lang(self, lang):
        with open("assets/lang/pokemon/{}.json".format(lang), 'r', encoding='utf-8') as file:
            self.poke_lang = json.load(file)

    def load_ability_lang(self, lang: str):
        with open("assets/lang/ability/{}.json".format(lang), 'r', encoding='utf-8') as file:
            self.ability_lang = json.load(file)

    def load_save(self, save):
        with open("data/save/{}.json".format(save), 'r', encoding='utf-8') as file:
            self._save = json.load(file)
        self.save_name = save
        if self.get_save_value("last_save", 0) == 0:
            self.save_data("last_save", int(time.time()))
        self.pokedex: dict[str, int] = self.get_save_value("pokedex", {})

    def save(self):
        save = self.get_save_value("last_save", 0)
        ct = int(time.time())
        tp = self.get_save_value("time_played", 0)
        self.save_data("time_played", tp + ct - save)
        self.save_data("last_save", ct)
        self.player.save(self._save)
        self.save_data("pokedex", self.pokedex)
        with open("data/save/{}.json".format(self.save_name), 'w', encoding='utf-8') as file:
            # copy to escape current modification
            json.dump(self._save.copy(), file)

    def get_save_value(self, key, default):
        if key in self._save:
            return self._save[key]
        else:
            return default

    def save_data(self, key, value):
        if value:
            self._save[key] = value
        elif key in self._save:
            del self._save[key]

    def get_money(self) -> int:
        return self.get_save_value("money", 0)

    def set_money(self, amount) -> int:
        self.save_data("money", amount)
        return amount

    def add_money(self, amount) -> int:
        return self.set_money(self.get_money() + amount)

    def remove_money(self, amount) -> int:
        return self.set_money(max(self.get_money() + amount, 0))

    def get_message(self, key: str) -> str:
        if key in self.lang:
            return self.lang[key]
        else:
            return key

    def get_poke_message(self, key: str) -> dict[str, str]:
        if key in self.poke_lang:
            return self.poke_lang[key]
        else:
            return {}

    def get_ability_message(self, key: str) -> dict[str, str]:
        if key in self.ability_lang:
            return self.ability_lang[key]
        else:
            return {}

    def unload_level(self):
        self.player.freeze_time = -1
        self.trigger_cache.clear()
        global IMAGE_CACHE
        IMAGE_CACHE.clear()
        DISPLAYER_CACHE.clear()

    def load_level(self, name, x, y):
        self.player.freeze_time = 10
        self.level = level.Level(name)
        self.level.floor.load_asset()
        self.level.layer_1.load_asset()
        self.level.load_asset(self.trigger_cache)
        self.player.set_pos((x, y))
        if not self.level.can_cycling:
            self.player.is_cycling = False
        self.save_data("last_level", name)
        self.save_data("last_level_coord", [x, y])
        if self.level.is_poke_center:
            self.save_data("last_poke_center_level", name)
            self.save_data("last_poke_center_level_coord", self.level.poke_center_heal_coord)
        self.level.load_sound()

    def render(self):

        self.collision.clear()
        self.display.fill((0, 0, 0))

        if self.player.have_open_menu():
            self.player.current_menu.render(self.display)
        else:
            if self.player.current_battle is None or self.player.current_battle.need_render():
                start = self.player.get_scroll_start()
                global came_scroll
                came_scroll = start
                end = self.player.get_scroll_end()
                self.level.floor.render(start[0], start[1], end[0], end[1], self.display, self.collision,
                                      [])
                # self.player.tick(self.display)
                self.level.layer_1.render(start[0], start[1], end[0], end[1], self.display,
                                        self.collision, [(self.player.get_render_y(), self.player.render)])

                self.level.npc_render(self.display, self.collision)
                self.level.load_trigger(start[0], start[1], end[0], end[1], self.trigger_cache, self.collision)

                if self.debug:
                    self.render_collision()



                    # back_ground = pygame.Surface(surf.get_rect().size)
                    # back_ground.fill((0, 0, 0))
                    # back_ground.set_alpha(200)
                    # self.display.blit(back_ground, (0, 0))

            if self.player.current_battle:
                back = self.player.current_battle.tick(self.display)
                if not isinstance(back, bool) or back:
                    self.player.current_battle.unload_assets()
                    self.player.current_battle = None
                    self.player.freeze_time = 2
                    if not isinstance(back, bool) and back is not None:
                        back()
                    self.level.load_sound()

        if self.debug:
            p_pos = self.player.get_pos()
            surf = FONT_16.render("x: {:+.4f}, y: {:+.4f}".format(p_pos[0], p_pos[1]), True, (255, 255, 255))
            surf2 = FONT_16.render(f"Last Render during {self.time_matrix[1]}ms", True, (255, 255, 255))
            surf3 = FONT_16.render(f"move TPS {(1000 / max(1, self.time_matrix[3])):+4.2f}", True, (255, 255, 255))
            surf4 = FONT_16.render(f"FPS: {(self.clock.get_fps()):+.1f} ", True, (255, 255, 255))
            self.display.blit(surf, (0, 0))
            self.display.blit(surf2, (0, 20))
            self.display.blit(surf3, (0, 40))
            self.display.blit(surf4, (0, 60))

        self.render_hud(self.display)
        self.screen.blit(pygame.transform.scale(self.display, main.SCREEN_SIZE), (0, 0))
        pygame.display.update()

    def render_hud(self, display):
        """

        :type display: pygame.Surface
        """
        if self.player.current_dialogue:
            self.player.current_dialogue.render(display)


    def render_collision(self):
        self.collision.debug_render(self.display)
        self.player.get_box().debug_render(self.display)

    def tick(self):

        if self.player.freeze_time == -1:
            self.collision.clear()
            self.display.fill((0, 0, 0))
            self.screen.blit(pygame.transform.scale(self.display, main.SCREEN_SIZE), (0, 0))
            pygame.display.update()
            return True

        self.time_matrix[0] = utils.current_milli_time()
        self.render()
        self.time_matrix[1] = utils.current_milli_time() - self.time_matrix[0]

        # k = self.__render_tick_counter.begin_render_tick(utils.current_milli_time())
        # for i in range(min(10, k)):
        if self.player.freeze_time == 0:
            self.time_matrix[2], self.time_matrix[3] = utils.current_milli_time(), utils.current_milli_time() - self.time_matrix[2]
            self.player.move(self.collision)
        elif self.player.freeze_time > 0:
            self.player.freeze_time -= 1
            self.player.speed_getter.get_delta(utils.current_milli_time(), 20)

        if self.direct_battle[0] and self.direct_battle[1] and len(self.level.wild_pokemon) > 0:
            self.direct_battle[1] = False
            wild_start.start_wild("TALL_GRASS", self.player)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

            if event.type == pygame.KEYUP or event.type == pygame.JOYBUTTONUP:
                if event.type == pygame.KEYUP:
                    k = event.key
                    self.last_input_type = INPUT_TYPE_KEYBOARD
                else:
                    k = event.button
                    self.last_input_type = INPUT_TYPE_GAMEPAD
                if k in option.KEY_FORWARDS:
                    self.player.on_key_y(-1, True)
                elif k in option.KEY_BACK:
                    self.player.on_key_y(1, True)
                elif k in option.KEY_RIGHT:
                    self.player.on_key_x(1, True)
                elif k in option.KEY_LEFT:
                    self.player.on_key_x(-1, True)
                elif k in option.KEY_ACTION:
                    self.player.action_unpress()
                elif k in option.KEY_SPRINT:
                    self.player.on_key_sprint(event.type == pygame.JOYBUTTONUP, False)

            elif event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                k = event.key if event.type == pygame.KEYDOWN else event.button
                if k in option.KEY_FORWARDS:
                    self.player.on_key_y(-1, False)
                elif k in option.KEY_BACK:
                    self.player.on_key_y(1, False)
                elif k in option.KEY_RIGHT:
                    self.player.on_key_x(1, False)
                elif k in option.KEY_LEFT:
                    self.player.on_key_x(-1, False)

                elif k in option.KEY_SPRINT:
                    self.player.on_key_sprint(event.type == pygame.JOYBUTTONDOWN, True)
                elif k in option.KEY_BIKE:
                    self.player.cycling_press()

                elif k in option.KEY_ACTION:
                    self.player.action_press()
                elif k in option.KEY_QUITE:
                    self.player.escape_press()
                elif k in option.KEY_MENU:
                    self.player.menu_press()

                # debug
                elif k == pygame.K_F3:
                    self.debug = not self.debug
                elif k == pygame.K_F4:
                    self.ignore_collision = not self.ignore_collision
                elif k == pygame.K_F5 and self.player.freeze_time == 0:
                    x, y = self.player.get_pos()
                    path = self.level.path
                    self.unload_level()
                    self.load_level(path, x, y)

            # elif event.type == pygame.JOYAXISMOTION:
            #     print("1", event.instance_id, event.axis, event.value)
            # elif event.type == pygame.JOYBALLMOTION:
            #     print("2", event.instance_id, event.ball, event.rel)
            elif event.type == pygame.JOYHATMOTION:
                v = event.value
                self.player.on_key_x(v[0], True, True)
                self.player.on_key_y(-v[1], True, True)


        return True

    def get_pokedex_e(self, id_: int) -> int:
        s_id = str(id_)
        return self.pokedex[s_id] if s_id in self.pokedex else POKEDEX_NEVER_SEEN

    def get_pokedex_status(self, id_: int) -> int:
        return self.get_pokedex_e(id_) & 0b11

    def get_nb_view(self, id_: int) -> int:
        return self.get_pokedex_e(id_) >> 2

    def add_pokedex_view(self, id_: int) -> NoReturn:
        if id_ < 1:
            return
        e = self.get_pokedex_e(id_)
        if e & 0b11 == POKEDEX_NEVER_SEEN:
            e &= ~0b11 | POKEDEX_SEEN
        c = e >> 2
        e &= 0b11
        e |= (c + 1) << 2
        self.pokedex[str(id_)] = e

    def set_pokedex_catch(self, id_: int) -> NoReturn:
        if id_ < 1:
            return
        self.pokedex[str(id_)] = self.get_pokedex_e(id_) & ~0b11 | POKEDEX_SEEN

    def get_pokedex_catch_status_values(self):
        return [(x & 0b11) for x in self.pokedex.values()]

def get_game_instance():
    """
    :rtype: Game
    """
    return game_instance

