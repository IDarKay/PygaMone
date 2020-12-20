from pygame import Surface

from pokemon.battle.animation import Animation
import pokemon.battle.battle as battle


class EvolutionAnimation(Animation):

    def tick(self, display: Surface) -> bool:
        pass

    def __init__(self, bat: 'battle.Battle'):
        self._bat = bat
        self._init = False
        self.action = False
        self._start = 0