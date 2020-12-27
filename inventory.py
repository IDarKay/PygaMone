import item.items as items
import item.item as item_


class Inventory(object):

    def __init__(self, data: dict):
        self.__data: dict = data
        self.__categories_data: dict[str, dict[item_.Item, int]] = {}
        self.setup_data()

    def get_category(self, category: str) -> dict[item_.Item, int]:
        return self.__categories_data.get(category, {})

    def add_items(self, it: item_.Item, amount: int = 1) -> int:
        if it is None:
            return 0
        new_amount = max(self.__data.get(it.identifier, 0) + amount, 0)
        if new_amount <= 0:
            if it.identifier in self.__data:
                del self.__data[it.identifier]
            sub_data = self.__categories_data.setdefault(it.category, {})
            if it in sub_data:
                del sub_data[it]
        else:
            self.__data[it.identifier] = new_amount
            sub_data = self.__categories_data.setdefault(it.category, {})
            sub_data[it] = new_amount
            return new_amount

    def remove_items(self, it: item_.Item, amount: int = 1) -> int:
        return self.add_items(it, -amount)

    def get_amount(self, it: item_.Item) -> int:
        if it is None:
            return 0
        return self.__data.get(it.identifier, 0)

    def setup_data(self):
        to_remove = []
        for item, amount in self.__data.items():
            try:
                it = items.ITEMS[item]
                sub_data = self.__categories_data.setdefault(it.category, {})
                sub_data[it] = amount
            except (IndexError, KeyError):
                to_remove.append(item)
        for it in to_remove:
            del self.__data[it]

    def get_data(self) -> dict:
        return self.__data
