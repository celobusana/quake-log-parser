from abc import ABC, abstractmethod
from pprint import pprint


class Game(ABC):
    game_id: int = 0
    
    def __init__(self, name: str):
        self.name = name
        self.generate_next_game_id()
        self._reset()

    @abstractmethod
    def _reset(self):
        pass
    
    @classmethod
    def generate_next_game_id(cls) -> int:
        cls.game_id += 1
        return cls.game_id    

    def shutdown(self):
        self.print_game_stats()

    def print_game_stats(self):
        pprint({f"game_{self.game_id}": self.stats()})

    @abstractmethod
    def stats(self):
        pass
