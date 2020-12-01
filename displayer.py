import game_error as er
import pygame
import game

DEFAULT_START = [0, 0]


class Displayer(object):

    def __init__(self, images_path, start, data, path):
        self.images_path = images_path
        self.start = start

        if game.DISPLAYER_CACHE.have(path):
            self.image = game.DISPLAYER_CACHE.get(path)
        else:
            if game.IMAGE_CACHE.have(images_path):
                self.image = game.IMAGE_CACHE.get(images_path)
            else:
                self.image = pygame.image.load("assets/textures/{}.png".format(images_path))
                game.IMAGE_CACHE.put(images_path, self.image)

            rescale = data["rescale"] if "rescale" in data else 1
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
                s = pygame.Surface((plot_end[0] - plot_start[0], plot_end[1] - plot_start[1]), pygame.SRCALPHA)
                s.blit(self.image, (0, 0), (pygame.Rect(plot_start[0], plot_start[1], plot_end[0], plot_end[1])))
                self.image = s
            if rescale > 1:
                s = self.image.get_rect().size
                self.image = pygame.transform.scale(self.image, (s[0] * rescale, s[1] * rescale))
                game.IMAGE_CACHE.put(path, self.image)

    def get_image(self):
        return self.image

    def __del__(self):
        # safe unload
        del self.image

    def display(self, display, x, y):
        """

        :type display: pygame.Surface
        """
        coord = int(x + self.start[0] * game.CASE_SIZE), int(y + self.start[1] * game.CASE_SIZE)
        # if self.need_plot:
        #     print(self.plot)
        #     display.blit(self.image, coord, self.plot)
        # else:
        display.blit(self.image, coord)


def parse(data, path):
    image = data["image"]
    if not image:
        raise er.StructureParseError("No image from {}".format(path))
    start = data["start"] if "start" in data else DEFAULT_START
    return Displayer(image, start, data, path)
