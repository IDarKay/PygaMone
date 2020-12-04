from typing import NoReturn, Optional
import pygame


MUSIC_CHANNEL: Optional[pygame.mixer.Channel] = None
AMBIENT_CHANNEL: Optional[pygame.mixer.Channel] = None
TAUNT_CHANNEL: Optional[pygame.mixer.Channel] = None


def init() -> NoReturn:
    global MUSIC_CHANNEL, AMBIENT_CHANNEL, TAUNT_CHANNEL
    MUSIC_CHANNEL = pygame.mixer.Channel(0)
    AMBIENT_CHANNEL = pygame.mixer.Channel(1)
    TAUNT_CHANNEL = pygame.mixer.Channel(2)
