from typing import Optional
import pygame

NB_POKEMON: int = 9
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

# todo: get file
PLINK_2 = Sound('assets/sound/plink.mp3')
BACK = Sound('assets/sound/plink.mp3')
LVL_UP = Sound('assets/sound/level_up.mp3')
EVOLUTION = Sound('assets/sound/evolution.mp3')
BALL_EXIT = Sound('assets/sound/battle/BallExit.wav')
BALL_SHAKE = Sound('assets/sound/battle/BallShake.wav')
BALL_THROW = Sound('assets/sound/battle/BallThrow.wav')
CATCH = Sound('assets/sound/battle/catch.mp3')

BLOCK = Sound('assets/sound/block.mp3')
SAVE = Sound('assets/sound/save.mp3')
HIT_NORMAL_DAMAGE = Sound('assets/sound/battle/NormalDamage.mp3')
HIT_NOT_VERY_EFFECTIVE = Sound('assets/sound/battle/NotVeryEffective.mp3')
HIT_SUPER_EFFECTIVE = Sound('assets/sound/battle/SuperEffective.mp3')

POKE_SOUND: list[Optional[Sound]] = [None] * (NB_POKEMON + 1)


def to_3_digit(num: int) -> str:
    if num < 10:
        return "00" + str(num)
    if num < 100:
        return "0" + str(num)
    return str(num)

def load_poke_sound():
    for id_ in range(1, NB_POKEMON + 1):
        sound = Sound(f'assets/sound/cry/{to_3_digit(id_)}Cry.wav')
        POKE_SOUND[id_] = sound


def unload_poke_sound():
    for ps in POKE_SOUND:
        if ps:
            ps.un_load()




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