import argparse
import logging
import os

from games.quake import QuakeLogAnalyzer
from log import LogFileReader

parser = argparse.ArgumentParser()
parser.add_argument(
    "--log-level",
    help="Set the logging level",
    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    default="INFO",
)
parser.add_argument("--log-file", help="Define the log file")
args = parser.parse_args()
logging.basicConfig(level=args.log_level)

if __name__ == "__main__":
    logging.info("Starting Quake Log Analyzer")
    LOG_FILE = os.path.join(os.getcwd(), args.log_file)
    file = LogFileReader(LOG_FILE)

    quake_log_analyzer = QuakeLogAnalyzer(file)
    quake_log_analyzer.process()
