class EventException(Exception):
    def __init__(self, message: str):
        self.message = message


class LogAnalyzerException(Exception):
    def __init__(self, message: str):
        self.message = message
