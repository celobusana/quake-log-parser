import os
import logging
from file import FileReader
from quake import QuakeLogAnalyzer

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

LOG_FILE = os.path.join(os.getcwd(), "qgames.log")

file = FileReader(LOG_FILE)

quake_log_analyzer = QuakeLogAnalyzer(file)
quake_log_analyzer.process()


