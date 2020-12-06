from typing import List, Tuple


class BackGround(object):

    def __init__(self, bg_path: str, ally_base_coord: List[Tuple[int, int]], enemy_base_coord: List[Tuple[int, int]]):
        self.bg_path = bg_path
        self.ally_base_coord = ally_base_coord
        self.enemy_base_coord = enemy_base_coord


FOREST: BackGround = BackGround('assets/textures/battle/bg/forest.png', [(0, 420), (300, 420)], [(670, 240), (378, 240)])