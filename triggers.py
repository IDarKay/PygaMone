from typing import Dict, Any, Tuple, NoReturn, Callable
import game_error as err
import json
import game
import hud.hud as hud
import sound_manager
import sounds
from hud import pc_hud

LOAD_LVL = "LOAD_LVL"
DIALOGUE = "DIALOGUE"
PC = "PC"


class Trigger(object):

    def __init__(self, _id: str, data: Dict[str, Any]):
        self.id_ = _id
        if "collision_side" not in data:
            raise err.TriggerParseError("No collision_side in file wth id {}".format(_id))
        self.side: Dict[str, Tuple[Any]] = {}
        if "loc" not in data:
            raise err.TriggerParseError("No location in trigger with id {}".format(_id))
        self.loc = data["loc"][0:4]

        for key, value in data["collision_side"].items():
            self.side[key] = self.dat(value)

    def get_property(self, data: Dict[str, Any], key: str, cast_check=None) -> Any:
        if key not in data:
            raise err.TriggerParseError("No {} in trigger id: {}".format(key, self.id_))
        value = data[key]
        if cast_check and not isinstance(value, cast_check):
            raise err.TriggerParseError(
                "Value for {} in {} isn't good type need be {}".format(key, self.id_, cast_check))
        return value

    def dat(self, data) -> Tuple:
        return ()

    def trigger(self, data) -> NoReturn:
        pass


class LoadLvlTrigger(Trigger):

    def __init__(self, _id: str, data: Dict[str, Any]):
        super().__init__(_id, data)

    def dat(self, data) -> Tuple:
        return (
            self.get_property(data, "lvl_name", str),
            self.get_property(data, "player_x"),
            self.get_property(data, "player_y")
        )

    def trigger(self, data) -> NoReturn:
        game.game_instance.unload_level()
        game.game_instance.load_level(data[0], data[1], data[2])
        pass


class PCTrigger(Trigger):

    def __init__(self, _id: str, data: Dict[str, Any]):
        super().__init__(_id, data)
        print(self.side)

    def dat(self, data) -> Tuple:
        return ()

    def trigger(self, data) -> NoReturn:
        if game.game_instance.player.is_action_press and game.game_instance.player.current_menu is None:
            sound_manager.start_in_first_empty_taunt(sounds.PC_OPEN)
            game.game_instance.player.open_menu(pc_hud.PCHud(game.game_instance.player))


class ShowTextTrigger(Trigger):

    def __init__(self, _id: str, data: Dict[str, Any]):
        super().__init__(_id, data)

    def dat(self, data) -> Tuple:
        return (
            self.get_property(data, "need_action", bool),
            self.get_property(data, "text", str),
        )

    def trigger(self, data) -> NoReturn:
        if (not data[0]) or game.game_instance.player.is_action_press and (
                not game.game_instance.player.current_dialogue):
            game.game_instance.player.open_dialogue(hud.QuestionDialog(
                hud.Dialog.split(game.game_instance.get_message("test")),
                self.callback, ["oui", "non", "jsp"], speed_skip=True), over=False, check_last_open=1000)

    def callback(self, value: str, index: int) -> NoReturn:
        return False


TRIGGERS: Dict[str, Callable[[str, Dict[str, Any]], Trigger]] = {
    LOAD_LVL: LoadLvlTrigger,
    DIALOGUE: ShowTextTrigger,
    PC: PCTrigger
}


def load(data: dict[str, Any]) -> Trigger:
    # with open("data/trigger/{}.json".format(path), 'r', encoding='utf-8') as file:
    #     data = json.load(file)

    if not data:
        raise err.TriggerParseError("No data")

    if "type" not in data:
        raise err.TriggerParseError("No type in data")

    type_ = data["type"]

    return TRIGGERS[type_](type_, data)
