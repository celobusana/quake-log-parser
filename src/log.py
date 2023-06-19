import sys
from pprint import pprint
from interface import LogReader
from typing import Tuple, Dict, List
from exception import EventException, LogAnalyzerException
import logging

class LogFileReader(LogReader):
    
    def __init__(self, log_file: str):
        self.log_file = log_file
        self._open_file()
        
    def _open_file(self):
        self.file = open(self.log_file, "r")
        
    def get_records(self) -> List[str]:
        return self.file.readlines()
    
