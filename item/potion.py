import item.item as item
import pokemon.player_pokemon as player_pokemon


class Potion(item.GiveableItem, item.NormalUsableItem):

    def __init__(self, _id: str, image_name: str, heal: int):
        super().__init__("item.potion." + _id, image_name, item.HEAL)
        self.heal = heal

    def can_use(self, poke: 'player_pokemon.PlayerPokemon') -> bool:
        return 0 < poke.heal < poke.get_max_heal()

    def use(self, poke: 'player_pokemon.PlayerPokemon'):
        if poke.heal == 0:
            return
        poke.heal = min(poke.heal + self.heal, poke.get_max_heal())


class MaxPotion(Potion):

    def __init__(self):
        super().__init__("max_potion", "max-potion", 0)

    def use(self, poke: 'player_pokemon.PlayerPokemon'):
        if poke.heal == 0:
            return
        poke.heal = poke.get_max_heal()