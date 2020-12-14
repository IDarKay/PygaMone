from typing import NoReturn, Union, Optional
import pokemon.battle.battle as battle
import utils
import sound_manager
import sounds
import pokemon.battle.battle as battle
import pygame
import game
import pokemon.player_pokemon as player_pokemon
import pokemon.pokemon as pokemon

class XpAnimation(battle.Battle):

    def __init__(self, bat: 'battle.Battle', xp_tab: list[int]):
        self.bat = bat
        self.xp_tab = xp_tab
        self.init = False

    def tick(self, display: pygame.Surface) -> bool:
        if not self.init:
            self.init = True
            self.start = utils.current_milli_time()
        ct_s = utils.current_milli_time() - self.start
        draw_xp_pokemon(display, [(500, True), (0, False)] * 3)
        draw_pokemon_stats(display, game.game_instance.player.team[0], {st: 5 for st in pokemon.STATS}, 1 - min(ct_s / 600, 1))
        return False


x = lambda y: (y - 900) / (-100 / 53)


def draw_pokemon_stats(display: pygame.Surface, poke: 'player_pokemon.PlayerPokemon', up: dict[str, int], fusion: float = 1):
    pygame.draw.rect(display, "#FFFFFF", (583, 150, 350, 214), border_radius=4)
    y = 150
    for st in pokemon.STATS:
        y += 10
        display.blit(game.FONT_24.render(game.get_game_instance().get_message(f'stats.{st}'), True, (0, 0, 0))
                     , (600, y))
        stats_n = poke.get_stats(st, False)
        if fusion == 0:
            stats_n += up[st]
        display.blit(tx := game.FONT_24.render(str(stats_n), True, (0, 0, 0)), (800 - tx.get_size()[0], y))
        if fusion != 0:
            add_x = 800 + 30 * fusion
            display.blit(game.FONT_24.render(f'+ {up[st]}', True, "#7e0000"), (add_x, y))

        y += 24



def draw_xp_pokemon(display: pygame.Surface, progress: Optional[list[tuple[int, bool]]]) -> NoReturn:

    pygame.draw.polygon(display, (255, 255, 255), ((477, 0), (583, 0), (265, 600), (159, 600)))
    pygame.draw.polygon(display, "#f4f4f4", ((0, 0), (477, 0), (159, 600), (0, 600)))
    y = 10
    h = 70
    c = 5
    for i in range(6):
        pygame.draw.polygon(display, "#e0e0e0", ((0, y), (x(y), y), (x(y + h), y + h), (0, y + h)))
        poke = game.game_instance.player.team[i]
        if poke:
            im = poke.get_front_image(0.7)
            delta_x, delta_y = utils.get_first_color(im)
            display.blit(im, (40 - delta_x // 2, y + 60 - delta_y))
            display.blit(game.FONT_24.render(poke.get_name(True), True, (0, 0, 0)), (80, y + 10))
            display.blit(game.FONT_24.render(f'N. {poke.lvl}', True, (0, 0, 0)), (80, y + h - 5 - game.FONT_SIZE_24[1]))
            if progress and (xp_p := progress[i][0]) > 0:
                display.blit(tx := game.FONT_24.render(f'+ {(xp_p):,}', True, (0, 0, 0)),
                             (230 - tx.get_size()[0], y + h - 5 - game.FONT_SIZE_24[1]))
                if progress[i][1]:
                    display.blit(game.FONT_24.render(game.game_instance.get_message("level_up"), True, (227, 25, 45)),
                                 (240, y + 10))

            xp = poke.current_xp_status()
            utils.draw_progress_bar(display, (80, y + h - 4), (150, 4), "#5a5a5a", "#45c1fd", xp[0] / xp[1])

        y += h + c

