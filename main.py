import pygame
import sound_manager
import game
import start_menu
import sys
import utils
import locale


def is_admin():
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return True


def set_admin():
    try:
        import ctypes
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    except:
        pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    if is_admin() or "--no-admin" in sys.argv:
        locale.setlocale(locale.LC_ALL, '')
        pygame.init()
        pygame.display.set_caption("Pokemon Fan Game")
        pygame.display.set_allow_screensaver(True)
        pygame.display.set_icon(pygame.image.load('assets/textures/item/master-ball.png'))
        flags = pygame.RESIZABLE
        screen = pygame.display.set_mode(size=(1060, 600), flags=flags)
        utils.force()

        no_start_gui: bool = "--non-start-gui" in sys.argv
        sound_manager.init()
        if no_start_gui:
            game.Game(screen)
        else:
            start_menu.StartMenu(screen)
    else:
        set_admin()
