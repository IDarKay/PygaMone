from typing import List, Tuple


class BackGround(object):

    def __init__(self, bg_path: str, ally_base_coord: List[List[Tuple[int, int]]], enemy_base_coord: List[List[Tuple[int, int]]]):
        self.bg_path = bg_path
        self.ally_base_coord = ally_base_coord
        self.enemy_base_coord = enemy_base_coord


FOREST: BackGround = BackGround('assets/textures/battle/bg/forest.png', [ [(100, 420)],  [(10, 420), (410, 420)], [(0, 420), (325, 420), (650, 420)]],
    [ [(670, 240)], [(670, 240), (290, 240)], [(670, 240), (335, 240), (0, 240)] ])