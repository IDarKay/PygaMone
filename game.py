from typing import Optional
import pygame
import level
import collision
import character.player as player
import json
import hud.menu as _menu
import time
import pokemon.pokemon as pokemon
import pokemon.ability as ability
import hud.hud as hud
import pokemon.abilitys_ as abilitys_
import item.items as items
import main
import sys
import pokemon.battle.wild_start as wild_start

screen = None

CASE_SIZE = 32

# SCREEN_SIZE = (1920, 1080)
SURFACE_SIZE = (1060, 600)

DIRECTION = ["top", "left", "down", "right"]

game_instance: Optional['Game'] = None

FONT_16: pygame.font.Font = None
FONT_20: pygame.font.Font = None
FONT_24: pygame.font.Font = None
FONT_SIZE_16 = (0, 0)
FONT_SIZE_20 = (0, 0)
FONT_SIZE_24 = (0, 0)

came_scroll = (0, 0)

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


IMAGE_CACHE = Cache()
DISPLAYER_CACHE = Cache()
POKE_CACHE = Cache()


class Game(object):

    def __init__(self, screen_s: pygame.Surface):
        self.screen = screen_s

        # asset load
        global FONT_16, FONT_SIZE_16, FONT_20, FONT_SIZE_20, FONT_24, FONT_SIZE_24
        FONT_16 = pygame.font.Font("assets/font/MyFont-Regular.otf", 16)
        FONT_20 = pygame.font.Font("assets/font/MyFont-Regular.otf", 20)
        FONT_24 = pygame.font.Font("assets/font/MyFont-Regular.otf", 24)
        FONT_SIZE_16 = FONT_16.size('X')
        FONT_SIZE_20 = FONT_16.size('X')
        FONT_SIZE_24 = FONT_16.size('X')
        self.lang = {}
        self.poke_lang = {}
        self.save_name = ""
        self._save = {}
        self.load_save("save")
        self.load_lang("en")
        self.load_poke_lang("en")
        items.load()
        abilitys_.load()
        pokemon.Pokemon.load_pokemons()
        hud.load_hud_item()
        # ============

        global game_instance
        game_instance = self

        self.display: 'pygame.Surface' = pygame.Surface(SURFACE_SIZE, pygame.HWSURFACE | pygame.SRCALPHA)
        self.player: 'player.Player' = player.Player(self)

        self.floor_cache = Cache()
        self.layer_cache = Cache()
        self.trigger_cache = Cache()

        self.level = None
        load_coord = self.get_save_value("last_level_coord", [100, 100])
        self.load_level(self.get_save_value("last_level", "level_1"), load_coord[0], load_coord[1])

        self.clock = pygame.time.Clock()
        self.collision = collision.Collision()
        self.debug = False
        self.ignore_collision = False

        running = True
        self.direct_battle: list[bool, bool] = ["--direct_battle" in sys.argv, True]
        while running:
            running = self.tick()
            self.clock.tick(60)

    def load_lang(self, lang):
        with open("assets/lang/text/{}.json".format(lang), 'r', encoding='utf-8') as file:
            self.lang = json.load(file)

    def load_poke_lang(self, lang):
        with open("assets/lang/pokemon/{}.json".format(lang), 'r', encoding='utf-8') as file:
            self.poke_lang = json.load(file)

    def load_save(self, save):
        with open("data/save/{}.json".format(save), 'r', encoding='utf-8') as file:
            self._save = json.load(file)
        self.save_name = save
        if self.get_save_value("last_save", 0) == 0:
            self.save_data("last_save", int(time.time()))

    def save(self):
        save = self.get_save_value("last_save", 0)
        ct = int(time.time())
        tp = self.get_save_value("time_played", 0)
        self.save_data("time_played", tp + ct - save)
        self.save_data("last_save", ct)
        self.player.save(self._save)
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

    def get_message(self, key: str) -> str:
        if key in self.lang:
            return self.lang[key]
        else:
            return key

    def get_poke_message(self, key: str) -> str:
        if key in self.poke_lang:
            return self.poke_lang[key]
        else:
            return key

    def unload_level(self):
        self.player.freeze_time = -1
        self.layer_cache.clear()
        self.floor_cache.clear()
        self.trigger_cache.clear()
        global IMAGE_CACHE
        IMAGE_CACHE.clear()
        DISPLAYER_CACHE.clear()

    def load_level(self, name, x, y):
        self.player.freeze_time = 10
        self.level = level.Level(name)
        self.level.floor.load_asset(self.floor_cache)
        self.level.layer_1.load_asset(self.layer_cache)
        self.level.load_asset(self.trigger_cache)
        self.player.set_pos((x, y))
        if not self.level.can_cycling:
            self.player.is_cycling = False
        self.save_data("last_level", name)
        self.save_data("last_level_coord", [x, y])

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
                self.level.floor.render(start[0], start[1], end[0], end[1], self.floor_cache, self.display, self.collision,
                                      [])
                # self.player.tick(self.display)
                self.level.layer_1.render(start[0], start[1], end[0], end[1], self.layer_cache, self.display,
                                        self.collision, [(self.player.get_render_y(), self.player.render)])

                self.level.npc_render(self.display, self.collision)
                self.level.load_trigger(start[0], start[1], end[0], end[1], self.trigger_cache, self.collision)

                if self.debug:
                    self.render_collision()

                if self.debug:
                    p_pos = self.player.get_pos()
                    surf = FONT_16.render("x: {:+.4f}, y: {:+.4f}".format(p_pos[0], p_pos[1]), True, (255, 255, 255))

                    # back_ground = pygame.Surface(surf.get_rect().size)
                    # back_ground.fill((0, 0, 0))
                    # back_ground.set_alpha(200)
                    # self.display.blit(back_ground, (0, 0))
                    self.display.blit(surf, (0, 0))
            if self.player.current_battle:
                self.player.current_battle.tick(self.display)

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

        self.render()

        if self.player.freeze_time == 0:
            self.player.move(self.collision)
        elif self.player.freeze_time > 0:
            self.player.freeze_time -= 1

        if self.direct_battle[0] and self.direct_battle[1] and len(self.level.wild_pokemon) > 0:
            self.direct_battle[1] = False
            wild_start.start_wild("TALL_GRASS", self.player)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.player.on_key_y(-1, event.type == pygame.KEYUP)
                if event.key == pygame.K_s:
                    self.player.on_key_y(1, event.type == pygame.KEYUP)
                if event.key == pygame.K_d:
                    self.player.on_key_x(1, event.type == pygame.KEYUP)
                if event.key == pygame.K_a:
                    self.player.on_key_x(-1, event.type == pygame.KEYUP)
                if event.key == pygame.K_x and event.type == pygame.KEYDOWN:
                    self.player.on_key_sprint()
                if event.key == pygame.K_z and event.type == pygame.KEYDOWN:
                    self.player.cycling_press()
                if event.key == pygame.K_F3 and event.type == pygame.KEYDOWN:
                    self.debug = not self.debug
                if event.key == pygame.K_F4 and event.type == pygame.KEYDOWN:
                    self.ignore_collision = not self.ignore_collision
                if event.key == pygame.K_e and event.type == pygame.KEYDOWN:
                    if self.player.current_menu:
                        self.player.close_menu()
                    else:
                        self.player.open_menu(_menu.MainMenu(self.player))
                if event.key == pygame.K_F5 and event.type == pygame.KEYDOWN and self.player.freeze_time == 0:
                    x, y = self.player.get_pos()
                    path = self.level.path
                    self.unload_level()
                    self.load_level(path, x, y)
                if event.key == pygame.K_SPACE:
                    if event.type == pygame.KEYDOWN:
                        self.player.action_press()
                    elif event.type == pygame.KEYUP:
                        self.player.action_unpress()
                if event.key == pygame.K_ESCAPE:
                    if event.type == pygame.KEYDOWN:
                        self.player.escape_press()
        return True


def get_game_instance():
    """
    :rtype: Game
    """
    return game_instance

