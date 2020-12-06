import pygame
import main
import utils
import game
import sound_manager

class StartMenu(object):

    def __init__(self, screen: pygame.Surface):
        self.__screen: pygame.Surface = screen
        self.__display: pygame.Surface = pygame.Surface(main.SCREEN_SIZE)
        self.__display.set_alpha(255)
        self.__open_time = utils.current_milli_time()
        # self.__sound = pygame.mixer.Sound('assets/sound/music/ps_1.mp3')
        self.__sound = pygame.mixer.Sound('assets/sound/music/start.mp3')
        self.__logo = pygame.image.load('assets/textures/hud/logo_full.png')

        self.__bg = pygame.transform.scale(pygame.image.load('assets/textures/hud/main_screen.png'), main.SCREEN_SIZE)
        self.__font = pygame.font.Font("assets/font/MyFont-Regular.otf", 24)
        self.__text = self.__font.render('Press a button to play !', True, (0, 0, 0))
        self.__text_size = self.__text.get_rect().size
        self.__clock = pygame.time.Clock()
        while self.__tick():
            self.__clock.tick(100)

    def dell_var(self):
        del self.__open_time, self.__sound, self.__logo, self.__bg, self.__font, self.__text
        del self.__text_size, self.__display, self.__clock

    def __tick(self):

        dif_t = utils.current_milli_time() - self.__open_time

        if dif_t < 3000:
            self.__display.fill((255, 255, 255))
            self.__display.blit(self.__logo, ((main.SCREEN_SIZE[0] - 600) // 2, (main.SCREEN_SIZE[1] - 128) // 2))
            self.__screen.blit(self.__display, (0, 0))
        else:

            if sound_manager.MUSIC_CHANNEL.get_sound() is None:
                sound_manager.MUSIC_CHANNEL.play(self.__sound)
            self.__screen.blit(self.__bg, (0, 0))
            self.__screen.blit(self.__text, ((main.SCREEN_SIZE[0] - self.__text_size[0]) // 2,
                                              (main.SCREEN_SIZE[1] - self.__text_size[1]) // 2))

            i = self.__display.get_alpha()
            if i > 0:
                self.__display.fill((255, 255, 255))
                if i > 50:
                    self.__display.blit(self.__logo, ((main.SCREEN_SIZE[0] - 600) // 2, (main.SCREEN_SIZE[1] - 128) // 2))
                self.__display.set_alpha(max(0, i - 2))
                self.__screen.blit(self.__display, (0, 0))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.dell_var()
                return False
            if event.type == pygame.KEYDOWN:
                if dif_t > 3000:
                    sound_manager.MUSIC_CHANNEL.stop()
                    self.dell_var()
                    game.Game(self.__screen)
                    return False

        return True
