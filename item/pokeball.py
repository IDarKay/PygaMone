from typing import Tuple
import pygame
import item.item as item
import random
import pokemon.player_pokemon as player_pokemon

POKE_BALL_IMAGE: pygame.Surface = pygame.image.load("assets/textures/item/pokeball.png")


class Pokeball(item.Item):

    def __init__(self, _id: str, image: pygame.Surface, bonus: float):
        super().__init__("item.pokeball." + _id, image, item.OBJECT)
        self.small_image: pygame.Surface = pygame.transform.scale(image, (16, 16))
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


class MasterBall(Pokeball):

    def __init__(self):
        super().__init__("master_ball", get_pokeball(188, 0, 238, 50), 1)

    def try_catch(self, p_poke) -> int:
        # master always catch
        return 4


def get_pokeball(*coord: int) -> pygame.Surface:
    return get_part_i(POKE_BALL_IMAGE, coord)

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