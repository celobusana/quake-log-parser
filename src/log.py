from typing import List

from interfaces.log import LogReader


class LogFileReader(LogReader):
    game_id: int = 0

    def __init__(self, log_file: str):
        self.log_file = log_file
        self._open_file()

    def _open_file(self):
        self.file = open(self.log_file, "r")

    def get_records(self) -> List[str]:
        return self.file.readlines()
