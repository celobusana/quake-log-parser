from typing import List

from interfaces.log import LogReader


class LogFileReader(LogReader):
    """Class to read log files."""

    def __init__(self, log_file: str):
        """Constructor.

        Args:
            log_file (str): Path to the log file.
        """
        self.log_file = log_file
        self._open_file()

    def _open_file(self):
        """Open the log file."""
        self.file = open(self.log_file, "r")

    def get_records(self) -> List[str]:
        """Get the records from the log file.

        Returns:
            List[str]: List of records (lines).
        """
        return self.file.readlines()
