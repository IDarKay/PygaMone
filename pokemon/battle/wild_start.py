from typing import NoReturn
import game
import random
import pokemon.battle.battle as battle
import pokemon.player_pokemon as player_pokemon
import sounds
# type

TALL_GRASS: str = "TALL_GRASS"
DARK_GRASS: str = "DARk_GRASS"


def player_in_area(area_type: str) -> NoReturn:
    player = game.game_instance.player
    if player.current_dialogue or player.current_menu or player.current_battle or player.get_non_null_team_number() == 0:
        return
    if random.random() < 0.005:
        p = game.game_instance.level.get_random_wild(area_type)
        if p is None:
            print("No pokemon in this level for type: ", area_type)

        b = battle.Battle(
            [player.team[0]],
            [player_pokemon.PlayerPokemon.create_pokemon(p, 20)],
            True,
            sound=sounds.BATTLE_DPP_TRAINER
        )

        player.start_battle(b)

        # game.game_instance.player.start_battle()

