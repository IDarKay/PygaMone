import item.item as item
import pokemon.player_pokemon as player_pokemon


class Revive(item.GiveableItem, item.NormalUsableItem):

    def __init__(self, _id: str, image_name: str, heal: float):
        super().__init__("item.revive." + _id, image_name, item.HEAL)
        self.heal = heal

    def can_use(self, poke: 'player_pokemon.PlayerPokemon') -> bool:
        return 0 == poke.heal

    def use(self, poke: 'player_pokemon.PlayerPokemon'):
        poke.heal = int(poke.get_max_heal() * self.heal)
