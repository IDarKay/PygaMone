import game
import sys
import pygame
import start_menu
import sound_manager

SCREEN_SIZE = (1600, 900)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(sys.argv)
    pygame.init()
    pygame.display.set_caption("Test Pokemon")
    screen = pygame.display.set_mode(SCREEN_SIZE)
    no_start_gui: bool = "--non-start-gui" in sys.argv
    sound_manager.init()
    if no_start_gui:
        game.Game(screen)
    else:
        start_menu.StartMenu(screen)
