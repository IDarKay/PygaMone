import pygame
import gif_manger
import pygame_gif
import utils
import pokemon.battle.battle as battle


class BurnAnimation(battle.Animation):

    def __init__(self, cord: tuple[int, int]):
        self.cord = cord
        self.no_init = True
        gif = gif_manger.SMALL_EMBER.get()
        self.g_i: list['pygame_gif.GifInstance'] = []
        for i in range(-60, 70, 60):
            self.g_i.append(gif.display((self.cord[0] + i, self.cord[1] - 60)))

    def tick(self, display: pygame.Surface) -> bool:
        if self.no_init:
            self.no_init = False
            self.start = utils.current_milli_time()
        pst = utils.current_milli_time() - self.start
        if pst < 1500:
            for g in self.g_i:
                g.render(display)
            return False
        if pst < 2000:
            return False
        return True
