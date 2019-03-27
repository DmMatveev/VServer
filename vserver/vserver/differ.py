from functools import lru_cache
from typing import List, NamedTuple, Dict


class Differ:
    def __init__(self, current: List[Dict[str, str]], past: List[Dict[str, str]], unique_key: str):
        self.current, self.past = current, past
        self.unique_key = unique_key

        self.intersect = self.current_keys.intersection(self.past_keys)

    @property
    @lru_cache()
    def added(self) -> List[Dict]:
        """
            Возвращает новые объекты, которые надо добавить
        """
        result = []

        current_unique_key = map(lambda x: x[self.unique_key], self.current)
        past_unique_key = map(lambda x: x[self.unique_key], self.past)

        difference = set(current_unique_key) - set(past_unique_key)

        for d in difference:
            for current in self.current:
                if current[self.unique_key] == d:
                    result.append(current)
                    break

        return result



    @property
    @lru_cache()
    def removed(self) -> List:
        return 2

    def changed(self):
        """ Find keys that have been changed """
        return set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])

    def unchanged(self):
        """ Find keys that are unchanged """
        return set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])

    def new_or_changed(self):
        """ Find keys that are new or changed """
        # return set(k for k, v in self.current_dict.items()
        #           if k not in self.past_keys or v != self.past_dict[k])
        return self.added().union(self.changed())
