from typing import Optional
import pygame_gif

__all__: list['Gif'] = []

class Gif(object):

    def __init__(self, path: str):
        __all__.append(self)
        self.path = path
        self.gif: Optional['pygame_gif.PygameGif'] = None

    def get(self):
        if self.gif is None:
            self.load()
        return self.gif

    def load(self):
        if not self.gif:
            self.gif = pygame_gif.PygameGif(self.path)

    def un_load(self):
        del self.gif
        self.gif = None

    def __str__(self):
        print("Sound : {}".format(self.path))


EMBER = Gif('./assets/textures/ability/ember.gif')
SMALL_EMBER = Gif('./assets/textures/ability/small_ember.gif')
CONTACT = Gif('./assets/textures/ability/contact.gif')
BIDE = Gif('./assets/textures/ability/bide.gif')


def unload_all():
    for g in __all__:
        g.un_load()
