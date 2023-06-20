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
        """Register a new event in the factory.

        Args:
            event (LogEvent): Event object to be registered.
        """
        self.events[event.id] = event

    def get(self, event_id: str) -> "LogEvent":
        """Get an event from the factory based on id

        Args:
            event_id (str): Event id.

        Raises:
            EventException: If the event is not registered.

        Returns:
            LogEvent: Event object.
        """
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
        """Process the log file."""
        for record in self.log.get_records():
            self._process_log_record(record)

    def _process_log_record(self, line: str):
        """Process one log record.

        Args:
            line (str): Log record.
        """
        try:
            log_event = self._parse_log(line)
            self._process_log_event(log_event)
        except EventException as e:
            logging.debug(e)
        except Exception as e:
            logging.exception(e)

    def _process_log_event(self, log_event: LogEventDto):
        """Process one log event. This method will call the event processor.

        Args:
            log_event (LogEventDto): Log event DTO object.
        """
        self.events.get(log_event.event).process(self, log_event)

    @abstractmethod
    def _parse_log(self, line: str) -> LogEventDto:
        pass
