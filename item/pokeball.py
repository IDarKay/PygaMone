import pygame
import item.item as item
import random
import pokemon.player_pokemon as player_pokemon
import hud.bag as bag

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
        # todo: do status condition
        bonus_s = 1

        a = (((3 * p_poke.get_max_heal() - 2 * p_poke.heal) * p_poke.poke.catch_rate * self.__bonus) / (3 * p_poke.get_max_heal())) * bonus_s
        if a < 0:
            a = 1
        elif a > 255:
            a = 255
        b = 1048560 / (((16711680 / a) ** 0.5) ** 0.5)

        i = 0
        while i < 4 or random.randint(0, 65535) < b:
            i += 1
        return i

    def is_usable(self, condition: int):
        return condition == bag.CONDITION_BATTLE


class MasterBall(Pokeball):

    def __init__(self):
        super().__init__("master_ball", 'master-ball', 1)

    def try_catch(self, p_poke) -> int:
        # master always catch
        return 4
