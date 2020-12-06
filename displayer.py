from typing import List, Dict, Any, NoReturn
import game_error as er
import pygame
import game

DEFAULT_START = [0, 0]


class Displayer(object):

    def __init__(self, images_path: str, start: List[float], data: Dict[str, Any], path: str):
        self.__images_path: str = images_path
        self.__start: List[float] = start

        # if game.DISPLAYER_CACHE.have(path):
        #     self.image: pygame.Surface = game.DISPLAYER_CACHE.get(path)
        # else:
        if game.IMAGE_CACHE.have(images_path):
            self.image: pygame.Surface = game.IMAGE_CACHE.get(images_path)
        else:
            self.image: pygame.Surface = pygame.image.load("assets/textures/{}.png".format(images_path))
            game.IMAGE_CACHE.put(images_path, self.image)

        rescale = data["rescale"] if "rescale" in data else 2
        if "from" in data:
            d = data["from"]
            if isinstance(d, list) and len(d) == 2:
                plot_start = d
            else:
                raise er.StructureParseError("In valid from ({}) in {} need be [int, int]".format(d, path))

            if "to" not in data:
                raise er.StructureParseError("No to in {} but there are from ned to [ini, int]".format(path))
            d = data["to"]
            if isinstance(d, list) and len(d) == 2:
                plot_end = d
            else:
                raise er.StructureParseError("In valid to ({}) in {} need be [int, int]".format(d, path))
            # self.image_size = (plot_end[0] - plot_start[0]) * rescale, (plot_end[1] - plot_start[1]) * rescale

            s = pygame.Surface((plot_end[0] - plot_start[0], plot_end[1] - plot_start[1]), pygame.SRCALPHA)
            s.blit(self.image, (0, 0), (pygame.Rect(plot_start[0], plot_start[1], plot_end[0], plot_end[1])))
            self.image = s
        # elif rescale == 1:
        #     self.image_size = self.image.get_size()
        if rescale != 1:
            # if "from" not in data:
            #     self.image_size = int(self.image.get_size()[0] * rescale), int(self.image.get_size()[0] * rescale)
            s = self.image.get_rect().size
            self.image = pygame.transform.scale(self.image, (s[0] * rescale, s[1] * rescale))
            # game.IMAGE_CACHE.put(path, self.image)
        self.image_size = self.image.get_size()




    def get_image(self) -> pygame.Surface:
        return self.image

    def __del__(self):
        # safe unload
        del self.image

    def display(self, display: pygame.Surface, x: int, y: int) -> NoReturn:
        coord = int(x + self.__start[0] * game.CASE_SIZE), int(y + self.__start[1] * game.CASE_SIZE)
        # if self.need_plot:
        #     print(self.plot)
        #     display.blit(self.image, coord, self.plot)
        # else:
        display.blit(self.image, coord)


def parse(data: Dict[str, Any], path: str) -> Displayer:
    image = data["image"]
    if not image:
        raise er.StructureParseError("No image from {}".format(path))
    start = data["start"] if "start" in data else DEFAULT_START
    return Displayer(image, start, data, path)
