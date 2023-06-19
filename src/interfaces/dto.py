from abc import ABC


class LogEventDto(ABC):
    def __init__(self, event: str, time: str, log: str):
        self.event = event
        self.time = time
        self.log = log
