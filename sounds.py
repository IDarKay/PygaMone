from typing import Optional
import pygame

__all__ : list['Sound'] = []

class Sound(object):

    def __init__(self, path: str):
        __all__.append(self)
        self.path = path
        self.sound: Optional[pygame.mixer.Sound]= None

    def get(self):
        if self.sound is None:
            self.load()
        return self.sound

    def load(self):
        if not self.sound:
            self.sound = pygame.mixer.Sound(self.path)

    def un_load(self):
        del self.sound
        self.sound = None

    def __str__(self):
        print("Sound : {}".format(self.path))


BATTLE_DPP_TRAINER = Sound('assets/sound/music/battle_DPP_trainer.mp3')
LEVEL_UP = Sound('assets/sound/level_up.mp3')
HEAL = Sound('assets/sound/heal.mp3')
PLINK = Sound('assets/sound/plink.mp3')
BLOCK = Sound('assets/sound/block.mp3')
SAVE = Sound('assets/sound/save.mp3')
HIT_NORMAL_DAMAGE = Sound('assets/sound/battle/NormalDamage.mp3')
HIT_NOT_VERY_EFFECTIVE = Sound('assets/sound/battle/NotVeryEffective.mp3')
HIT_SUPER_EFFECTIVE = Sound('assets/sound/battle/SuperEffective.mp3')

# __all__ = [
#     BATTLE_DPP_TRAINER,
#     LEVEL_UP,
#     HEAL,
#     PLINK,
#     BLOCK,
#     SAVE,
#     HIT_NORMAL_DAMAGE,
#     HIT_NOT_VERY_EFFECTIVE,
#     HIT_SUPER_EFFECTIVE
# ]