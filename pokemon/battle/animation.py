from abc import abstractmethod
from pygame import Surface


class Animation(object):

    @abstractmethod
    def tick(self, display: Surface) -> bool:
        pass

    def is_priority(self) -> int:
        return 0

    def get_compare_value(self) -> int:
        return 0

    def on_key_action(self) -> bool:
        return True

    def __gt__(self, other):
        if isinstance(other, Animation):
            p1, p2 = self.is_priority(), other.is_priority()
            return p1 > p2 or (p1 == p2 and self.get_compare_value() > other.get_compare_value())
        else:
            raise ValueError("other need be animation")

    def __lt__(self, other):
        if isinstance(other, Animation):
            p1, p2 = self.is_priority(), other.is_priority()
            return p1 < p2 or (p1 == p2 and self.get_compare_value() < other.get_compare_value())
        else:
            raise ValueError("other need be animation")
