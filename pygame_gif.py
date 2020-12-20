from typing import List, NoReturn, Tuple, Dict
import os
import utils, pygame


try:
    import PIL
    from PIL import Image
    from PIL.GifImagePlugin import getheader, getdata
except ImportError:
    PIL = None

try:
    import numpy as np
except ImportError:
    np = None

TOKEN = 0
LOAD_GIF: Dict[int, 'GifInstance'] = {}


class GifInstance(object):

    def __init__(self, images: List[pygame.Surface], coord: Tuple[int, int], speed):
        self.__images: List[pygame.Surface] = images
        self.__len = len(images)
        self.__coord = coord
        self.__speed = speed
        self.__ticking = speed * self.__len
        self.__start_time = utils.current_milli_time()

    def render(self, display: pygame.Surface, coord=None) -> NoReturn:
        ps_t = utils.current_milli_time() - self.__start_time
        im = self.__images[(ps_t % self.__ticking) // self.__speed]
        display.blit(im, self.__coord if coord is None else coord)


class PygameGif(object):

    def __init__(self, file: object) -> object:
        images = readGif(file, False)
        self.__py_images = []

        for im in images:
            surf = pygame.image.fromstring(im.tobytes(), im.size, im.mode)
            self.__py_images.append(surf)

    def display(self, coord: Tuple[int, int], speed=100) -> GifInstance:
        return GifInstance(self.__py_images, coord, speed)

    def auto_display(self, coord: Tuple[int, int], speed=100) -> int:
        global TOKEN
        gif = GifInstance(self.__py_images, coord, speed)
        TOKEN += 1
        LOAD_GIF[TOKEN] = gif
        return TOKEN


def un_show(token: int):
    global TOKEN
    del LOAD_GIF[token]


def render(display: pygame.Surface):
    for e in LOAD_GIF.values():
        e.render(display)


def readGif(filename, asNumpy=True):
    """ readGif(filename, asNumpy=True)

    Read images from an animated GIF file.  Returns a list of numpy
    arrays, or, if asNumpy is false, a list if PIL images.

    """

    # Check PIL
    if PIL is None:
        raise RuntimeError("Need PIL to read animated gif files.")

    # Check Numpy
    if np is None:
        raise RuntimeError("Need Numpy to read animated gif files.")

    # Check whether it exists
    if not os.path.isfile(filename):
        raise IOError('File not found: ' + str(filename))

    # Load file using PIL
    pilIm = PIL.Image.open(filename)
    pilIm.seek(0)

    # Read all images inside
    images = []
    try:
        while True:
            # Get image as numpy array
            tmp = pilIm.convert()  # Make without palette
            a = np.asarray(tmp)
            if len(a.shape) == 0:
                raise MemoryError("Too little memory to convert PIL image to array")
            # Store, and next
            images.append(a)
            pilIm.seek(pilIm.tell() + 1)
    except EOFError:
        pass

    # Convert to normal PIL images if needed
    if not asNumpy:
        images2 = images
        images = []
        for index, im in enumerate(images2):
            tmp = PIL.Image.fromarray(im)
            images.append(tmp)

    # Done
    return images


