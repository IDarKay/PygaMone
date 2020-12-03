import pygame
import item.item as item
import random
import utils
import pokemon.player_pokemon as pk

POKE_BALL_IMAGE = pygame.image.load("assets/textures/item/pokeball.png")

class Pokeball(item.Item):

    def __init__(self, _id: str, image: pygame.Surface, bonus: float):
        super().__init__("item.pokeball." + _id, image, item.OBJECT)
        self.bonus = bonus

    def try_catch(self, p_poke) -> int:
        '''

        :return: 0 = no poke move 1 - 3 poke_nb move 4 = catch
        '''
        # todo: do status condition
        bonus_s = 1

        a = (((3 * p_poke.get_max_heal() - 2 * p_poke.heal) * p_poke.poke.catch_rate * self.bonus)  / (3 * p_poke.get_max_heal())) * bonus_s
        if a < 0: a = 1
        elif a > 255: a = 255
        b = 1048560 / (((16711680 / a) ** 0.5) ** 0.5)

        i = 0
        while i < 4 or random.randint(0, 65535) < b:
            i += 1
        return i


class MasterBall(Pokeball):

    def __init__(self):
        super().__init__("master_ball", get_pokeball(188, 0, 238, 50), 1)

    def try_catch(self, p_poke) -> int:
        # master always catch
        return 4

def get_pokeball(*coord: int) -> pygame.Surface:
    return utils.get_part(POKE_BALL_IMAGE, coord)