from abc import abstractmethod
from pygame import Surface

class Animation(object):

    @abstractmethod
    def tick(self, display: Surface) -> bool:
        pass

    def is_priority(self) -> bool:
        return False

    def get_compare_value(self) -> int:
        return 0

    def on_key_action(self) -> bool:
        return False

    def __gt__(self, other):
        if isinstance(other, Animation):
            return (self.is_priority() and not other.is_priority()) or self.get_compare_value() > other.get_compare_value()
        else:
            raise ValueError("other need be animation")

    def __lt__(self, other):
        if isinstance(other, Animation):
            return (not self.is_priority() and other.is_priority()) or self.get_compare_value() < other.get_compare_value()
        else:
            raise ValueError("other need be animation")
