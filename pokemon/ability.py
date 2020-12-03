import utils
import pokemon.pokemon_type as p_type
import game_error as err
import os
import json
import game

CATEGORYS = ["PHYSICAL", "SPECIAL", "STATUS"]

ABILITYS = {}

class Ability(object):

    def __init__(self, _id, data):
        self._id = _id
        self.data = data
        self.type = p_type.TYPES[self.get_args("type", type_check=str)]
        self.category = self.get_args("category")
        if self.category not in CATEGORYS:
            raise err.AbilityParseError("Invalid category for {}".format(_id))
        self.pp = self.get_args("pp", type_check=int)
        self.max_pp = self.get_args("max_pp", type_check=int)
        self.power = self.get_args("power", type_check=int)
        self.accuracy = self.get_args("accuracy", type_check=int)
        self.contact = self.get_args("contact", default=False, type_check=bool)
        self.protect = self.get_args("protect", default=False, type_check=bool)
        self.magic_coat = self.get_args("magic_coat", default=False, type_check=bool)
        self.snatch = self.get_args("snatch", default=False, type_check=bool)
        self.mirror_move = self.get_args("mirror_move", default=False, type_check=bool)
        self.king_rock = self.get_args("king_rock", default=False, type_check=bool)
        self.target = self.get_args("target")
        del self.data

    def get_name(self):
        return game.get_game_instance().get_message("ability." + self._id)

    def get_args(self, key: str, default=None, type_check=None):
        return utils.get_args(self.data, key, self._id, default, type_check, _type="ability")


load = False


def load_ability():
    global load, ABILITYS
    if not load:
        load = True
        for file in os.listdir("data/ability"):
            if file.endswith(".json"):
                _id = file[0:-5]
                with open(os.path.join("data/ability", file), 'r', encoding='utf-8') as _file:
                    ABILITYS[_id] = Ability(_id, json.load(_file))