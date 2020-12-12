import pokemon.player_pokemon as player_pokemon
import utils


class PokeStatsModifier(object):

    def __init__(self, poke: 'player_pokemon.PlayerPokemon'):
        self.poke = poke
        self.edit: dict[str, int] = {}

    def get(self, stats: str) -> int:
        return self.edit[stats] if stats in self.edit else 0

    def set(self, stats: str, value: int) -> int:
        self.edit[stats] = value
        return value

    def add(self, stats: str, value: int):
        ac = self.get(stats)
        m = ""
        if ac == 6:
            m = "stats.too_high"
        elif ac == -6:
            m = "stats.too_low"
        else:
            m = f"stats.{ 'add' if value > 0 else 'remove' }.{str(utils.min_max(1, abs(value), 3))}"
        self.set(stats, max(-6, min(6, ac + value), 0))
        return m

    #
    # def remove(self, stats: str, value: int):
    #     self.set(stats, max(-6, self.get(stats) - abs(value)))

    def reset(self):
        self.edit.clear()
