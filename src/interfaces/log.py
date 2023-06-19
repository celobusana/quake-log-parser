import logging
from abc import ABC, abstractmethod
from pprint import pprint
from typing import List

from exception import EventException
from interfaces.dto import LogEventDto


class LogEventFactory:
    def __init__(self):
        self.events = {}

    def register(self, event: "LogEvent"):
        self.events[event.id] = event

    def get(self, event_id: str) -> "LogEvent":
        if event_id not in self.events:
            raise EventException(f"Event {event_id} not registered")
        return self.events[event_id]


class LogEvent(ABC):
    def __init__(self, id: str):
        self.id = id

    @abstractmethod
    def process(self, log_analyzer: "LogAnalyzer", log_event: LogEventDto):
        pass


class LogReader(ABC):
    @abstractmethod
    def get_records(self) -> List[str]:
        pass


class LogAnalyzer(ABC):
    events: LogEventFactory
    game_id: int = 0

    def __init__(self, log: LogReader, events: LogEventFactory):
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
            logging.debug(e)
        except Exception as e:
            logging.exception(e)

    def _process_log_event(self, log_event: LogEventDto):
        self.events.get(log_event.event).process(self, log_event)

    def shutdown_game(self):
        self.print_game_stats()
        self.game_id += 1
        del self.game

    def print_game_stats(self):
        pprint({f"game_{self.game_id}": self.game.stats()})

    @abstractmethod
    def _parse_log(self, line: str) -> LogEventDto:
        pass
