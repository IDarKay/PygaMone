import math

import pygame
from pygame import Surface

import displayer
import sound_manager
import sounds
import utils
from pokemon.battle.animation import Animation
import pokemon.battle.battle as battle
import pokemon.player_pokemon as player_pokemon
import pokemon.pokemon as pokemon
import hud.hud as hud
import game

PATH = 'assets/textures/pokemon/{}.png'.format


class EvolutionAnimation(Animation):

    def __init__(self, bat: 'battle.Battle', poke: 'player_pokemon.PlayerPokemon', new_id: int):
        self.new_id = new_id
        self._bat = bat
        self._init = False
        self.action = False
        self._start = 0
        self.poke = poke
        self.base_poke = self.poke.poke
        self.new_base_poke = pokemon.get_pokemon(new_id)
        self.question_answer = None
        self.bg = None
        self.need_end = False

    def tick(self, display: Surface) -> bool:
        if not self._init:
            self._init = True

            ask = game.game_instance.get_message("yes"), \
                  game.game_instance.get_message("no")
            game.game_instance.player.open_dialogue(
                hud.QuestionDialog('battle.evolution_ask', self.callback, ask, speed=20, need_morph_text=True, style=2,
                               text_var=[self.poke.get_name(True)]))
        if self.question_answer is not None:
            # no
            if self.question_answer == 1:
                return True
            # yes
            else:
                ps_t = utils.current_milli_time() - self._start
                # if ps_t < 10_000:
                display.blit(self.bg, (0, 0))
                if ps_t < 8_000:
                    x = ps_t / (8000 / 10)
                    f = lambda x: math.cos(x * 10) + 0.2 * x -1
                    img = displayer.get_poke(PATH(str(self.new_base_poke.id_ if f(x) >= 0 else self.base_poke.id_)), 3)
                    display.blit(img, (530 - img.get_size()[0] // 2, 300 - img.get_size()[1] // 2))
                else:
                    img = displayer.get_poke(PATH(str(self.new_base_poke.id_)), 3)
                    display.blit(img, (530 - img.get_size()[0] // 2, 300 - img.get_size()[1] // 2))
                    if not self.action:
                        sound_manager.start_in_first_empty_taunt(sounds.EVOLUTION)
                        self.action = True
                        game.game_instance.player.open_dialogue(
                            hud.Dialog("battle.evolution", speed=100, need_morph_text=True,
                                       callback=self.end_callback,
                                       text_var=[self.poke.get_name(True), self.new_base_poke.get_name(True)]))
                        self.poke.set_id(self.new_id)

                    elif self.need_end:
                        game.game_instance.player.close_dialogue()
                        del self.bg
                        sounds.EVOLUTION.un_load()
                        return True
            return False

    # def on_key_action(self) -> bool:
    #     return True

    def end_callback(self):
        self.need_end = True
        return False

    def callback(self, value, index):
        self._start = utils.current_milli_time()
        self.question_answer = index
        sounds.EVOLUTION.load()
        self.bg = pygame.image.load('assets/textures/battle/bg/evolution.png')
