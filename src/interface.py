import logging
from abc import ABC, abstractmethod
from factory import GameEventFactory
from exception import EventException
from typing import List, Dict
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
    
class LogEvent(ABC):
    
    def __init__(self, event: str, time: str, log: str):
        self.event = event
        self.time = time
        self.log = log
    
class LogAnalyzer(ABC):

    events: GameEventFactory
    game: Game
    game_id: int = 0

    def __init__(self, log: LogReader, events: GameEventFactory):
        self.log = log
        self.events = events

    def process(self):
        for record in self.log.get_records():
            self._process_log(record)

    def _process_log(self, line: str):
        try:
            log_event = self._parse_log(line)
            self._process_log_event(log_event)
        except EventException as e:
            pass
        except Exception as e:
            logging.exception(e)

    def _process_log_event(self, log_event: LogEvent):
        self.events.get(log_event.event).process(self, log_event)

    def shutdown_game(self):
        self.game_id += 1
        self.print_game_stats()
        del(self.game)

    def print_game_stats(self):
        pprint({f"game_{self.game_id}": self.game.stats()})

    @abstractmethod
    def _parse_log(self, line: str) -> LogEvent:
        pass

