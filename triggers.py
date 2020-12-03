import game_error as err
import json
import game
import character.player as player
import hud.hud as hud

LOAD_LVL = "LOAD_LVL"
DIALOGUE = "DIALOGUE"

class Trigger(object):

    def __init__(self, _id, data):
        self._id = _id
        if "collision_side" not in data:
            raise err.TriggerParseError("No collision_side in file wth id {}".format(id))
        self.side = {}

        for key, value in data["collision_side"].items():
            self.side[key] = self.dat(value)

    def get_property(self, data, key, cast_check=None):
        if key not in data:
            raise err.TriggerParseError("No {} in trigger id: {}".format(key, self._id))
        value = data[key]
        if cast_check and not isinstance(value, cast_check):
            raise err.TriggerParseError(
                "Value for {} in {} isn't good type need be {}".format(key, self._id, cast_check))
        return value

    def dat(self, data):
        return ()

    def trigger(self, data):
        pass


class LoadLvlTrigger(Trigger):

    def __init__(self, id, data):
        super().__init__(id, data)

    def dat(self, data):
        return (
            self.get_property(data, "lvl_name", str),
            self.get_property(data, "player_x"),
            self.get_property(data, "player_y")
        )

    def trigger(self, data):
        game.game_instance.unload_level()
        game.game_instance.load_level(data[0], data[1], data[2])
        pass


class ShowTextTrigger(Trigger):

    def __init__(self, id, data):
        super().__init__(id, data)

    def dat(self, data):
        return (
            self.get_property(data, "need_action", bool),
            self.get_property(data, "text", str),
        )

    def trigger(self, data):
        if (not data[0]) or game.game_instance.player.is_action_press and (not game.game_instance.player.current_dialogue):
            game.game_instance.player.open_dialogue(hud.QuestionDialog(
                hud.Dialog.split(game.game_instance.get_message("test")),
                 self.callback, ["oui", "non", "jsp"], speed_skip=True), check_last_open=1000)

    def callback(self, value, index):
        print(value, index)
        return False

TRIGGERS = {
    LOAD_LVL: LoadLvlTrigger,
    DIALOGUE: ShowTextTrigger
}

def load(path):
    with open("data/trigger/{}.json".format(path), 'r', encoding='utf-8') as file:
        data = json.load(file)

    if not data:
        raise err.TriggerParseError("No data in {}".format(path))

    if not "type" in data:
        raise err.TriggerParseError("No type in {}".format(path))

    type = data["type"]

    return TRIGGERS[type](type, data)
