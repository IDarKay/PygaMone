import pygame
import item.item as item
import random
import pokemon.player_pokemon as player_pokemon
import hud.bag as bag
from math import sqrt

# POKE_BALL_IMAGE: pygame.Surface = pygame.image.load("assets/textures/item/pokeball.png")


class Pokeball(item.GiveableItem):

    def __init__(self, _id: str, image_name: str, bonus: float):
        super().__init__("item.pokeball." + _id, image_name, item.POKE_BALLS)
        self.small_image: pygame.Surface = pygame.transform.scale(self.image, (16, 16))
        self.__bonus: float = bonus

    def try_catch(self, p_poke: 'player_pokemon.PlayerPokemon') -> int:
        '''

        :return: 0 = no poke move 1 - 3 poke_nb move 4 = catch
        '''
        # bonus_s = 1
        bonus_s = max(p_poke.combat_status.it, key=lambda st: st.status.get_catch_edit(), default=1)

        a = (((3 * p_poke.get_max_heal() - 2 * p_poke.heal) * p_poke.poke.catch_rate * self.__bonus) / (3 * p_poke.get_max_heal())) * bonus_s
        if a < 0:
            a = 1
        elif a > 255:
            a = 255
        print(a)
        b = 1048560 / sqrt(sqrt(16711680 / a))
        print(b)
        print((b/65535)**4)
        i = 0
        while i < 4 and random.randint(0, 65535) <= b:
            i += 1
        return i

    def need_use_target(self):
        return False

    def is_usable(self, condition: int):
        return condition == bag.CONDITION_BATTLE


class MasterBall(Pokeball):

    def __init__(self):
        super().__init__("master_ball", 'master-ball', 1)

    def try_catch(self, p_poke) -> int:
        # master always catch
        return 4
