from typing import NoReturn
import game
import random
import pokemon.battle.battle as battle
import pokemon.player_pokemon as player_pokemon
import character.player as pl
import sounds
# type

TALL_GRASS: str = "TALL_GRASS"
DARK_GRASS: str = "DARk_GRASS"


def player_in_area(area_type: str) -> NoReturn:
    player = game.game_instance.player
    if player.current_dialogue or player.current_menu or player.current_battle or player.get_non_null_team_number() == 0:
        return
    if random.random() < 0.005:
       start_wild(area_type, player)




def start_wild(area_type: str, player: 'pl.Player'):
    p = game.game_instance.level.get_random_wild(area_type)
    if p is None:
        print("No pokemon in this level for type: ", area_type)
    b = battle.Battle(
        battle.BattleTeam(
            [
                battle.BattlePlayer(False, [], (0,), disp=battle.BattlePlayerDisplay(False, "", []))
             ], False),
        battle.BattleTeam(
            [
                battle.BattlePlayer(True, [player_pokemon.PlayerPokemon.create_pokemon(p, 20)], (0,), wild=True),
                battle.BattlePlayer(True, [player_pokemon.PlayerPokemon.create_pokemon(p, 20)], (1,), wild=True),
            ], True),
        True
    )

    player.start_battle(b)