import pygame
import sound_manager
import game
import start_menu
import sys
import utils
import locale
import ctypes

SCREEN_SIZE = (1600, 900)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    if is_admin() or "--no-admin" in sys.argv:
        locale.setlocale(locale.LC_ALL, '')
        pygame.init()
        pygame.display.set_caption("Pokemon Fan Game")
        pygame.display.set_allow_screensaver(True)
        pygame.display.set_icon(pygame.image.load('assets/textures/item/master-ball.png'))
        screen = pygame.display.set_mode(SCREEN_SIZE)
        utils.force()

        no_start_gui: bool = "--non-start-gui" in sys.argv
        sound_manager.init()
        if no_start_gui:
            game.Game(screen)
        else:
            start_menu.StartMenu(screen)
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
