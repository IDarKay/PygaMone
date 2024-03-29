class StructureParseError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "StructureParseError, {} ".format(self.message)
        else:
            return "StructureParseError has been raised"


class NPCParseError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "NPCParseError, {} ".format(self.message)
        else:
            return "NPCParseError has been raised"


class TriggerParseError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "TriggerParseError, {} ".format(self.message)
        else:
            return "TriggerParseError has been raised"


class PokemonParseError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "PokemonParseError, {} ".format(self.message)
        else:
            return "PokemonParseError has been raised"


class AbilityParseError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "AbilityParseError, {} ".format(self.message)
        else:
            return "AbilityParseError has been raised"


class LevelParseError(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "LevelParseError, {} ".format(self.message)
        else:
            return "LevelParseError has been raised"


class NullPointerError(Exception):

    def __init__(self, *args):
        pass

    def __str__(self):
        return "NullPointerError"
