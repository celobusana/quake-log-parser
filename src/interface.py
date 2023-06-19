import logging
from abc import ABC, abstractmethod
from factory import GameEventFactory
from exception import EventException
from typing import List, Tuple
from pprint import pprint

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

class GameEvent(ABC):

    def __init__(self, id: str):
        self.id = id

    @abstractmethod
    def process(self, log: str):
        pass
    
class LogReader(ABC):
    
    @abstractmethod
    def get_records(self) -> List[str]:
        pass
    
class LogAnalyzer(ABC):

    events: GameEventFactory
    game: Game
    game_id: int = 0

    def __init__(self, log: LogReader, events: GameEventFactory):
        self.log = log
        self.events = events

    def process(self):
        lines = 0
        for line in self.log.get_records():
            lines += 1
            if lines < 10:
                continue
            self._process_line(line)

    def _process_line(self, line: str):
        try:
            time, event, log = self._parse_line(line)
            self._process_event(event, log)
        except EventException as e:
            # logging.warning(e)
            pass
        except Exception as e:
            logging.exception(e)

    def _process_event(self, event: str, log: str):
        self.events.get(event).process(self, log)

    def shutdown_game(self):
        self.game_id += 1
        self.print_game_stats()
        del (self.game)

    def print_game_stats(self):
        pprint({f"game_{self.game_id}": self.game.stats()})

    @abstractmethod
    def _parse_line(self, line: str) -> Tuple[str, str, str]:
        pass

