from abc import ABC, abstractmethod


class Game(ABC):
    def __init__(self, name: str):
        self.name = name
        self._reset()

    @abstractmethod
    def _reset(self):
        pass

    @abstractmethod
    def stats(self):
        pass
