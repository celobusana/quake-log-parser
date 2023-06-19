import sys
from pprint import pprint
from typing import Tuple, Dict, List
from exception import EventException, LogAnalyzerException
from abc import ABC, abstractmethod
from interface import GameEvent, Game, LogAnalyzer, LogReader
from factory import GameEventFactory
import logging


class QuakeInitGameEvent(GameEvent):

    def __init__(self):
        super().__init__("InitGame")

    def process(self, log_analyzer: "QuakeLogAnalyzer", log: str):
        if hasattr(log_analyzer, "game") and log_analyzer.game:
            logging.warning("New game started before the previous one ended")
            log_analyzer.shutdown_game()
        log_analyzer.game = QuakeGame()


class QuakeClientConnectEvent(GameEvent):

    def __init__(self):
        super().__init__("ClientConnect")

    def process(self, log_analyzer: "QuakeLogAnalyzer", log: str):
        logging.debug(f"ClientConnect {log}")


class QuakeShutdownGameEvent(GameEvent):

    def __init__(self):
        super().__init__("ShutdownGame")

    def process(self, log_analyzer: "QuakeLogAnalyzer", log: str):
        logging.debug(f"Shutdown {log}")
        log_analyzer.shutdown_game()


class QuakeKillEvent(GameEvent):

    def __init__(self):
        super().__init__("Kill")

    def process(self, log_analyzer: "QuakeLogAnalyzer", log: str):
        details = log[log.find(":")+1:]
        weapon = details.rsplit(" ", 1)[-1]
        players = details.replace(f"by {weapon}", "").strip().split(" killed ")
        if len(players) != 2:
            raise LogAnalyzerException(f"Invalid kill event {log}")
        log_analyzer.game.add_kill(players[0], players[1], weapon)


class QuakeGame(Game):

    total_kills: int = 0
    kills_by_means: Dict[str, int] = {}
    kills_by_player: Dict[str, int] = {}
    players: List[str] = []

    def __init__(self):
        super().__init__("Quake")
        
    def _reset(self):
        self.total_kills = 0
        self.players = []
        self.kills_by_means = {}
        self.kills_by_player = {}

    def add_kill(self, killer: str, killed: str, weapon: str):
        logging.debug(f" Add Kill -> {killer} killed {killed} by {weapon}")
        self.total_kills += 1

        self.add_kill_by_means(weapon)
        self.add_kill_by_player(killer, killed)
        self.add_player(killer)
        self.add_player(killed)

    def add_kill_by_means(self, weapon: str):
        if weapon not in self.kills_by_means:
            self.kills_by_means[weapon] = 0
        self.kills_by_means[weapon] += 1

    def add_kill_by_player(self, player: str, killed: str):
        points = 1
        if player == killed:
            points = 0
        if player == "<world>":
            player = killed
            points = -1
        if player not in self.kills_by_player:
            self.kills_by_player[player] = 0
        self.kills_by_player[player] += points
        
    def add_player(self, player: str):
        if player == "<world>":
            return
        if player not in self.players:
            self.players.append(player)

    def stats(self):
        return {
            "total_kills": self.total_kills,
            "players": self.players,
            "kills": self.kills_by_player,
            "kills_by_means": self.kills_by_means
        }


class QuakeLogAnalyzer(LogAnalyzer):

    def __init__(self, file: LogReader):
        quake_events = GameEventFactory()
        quake_events.register(QuakeInitGameEvent())
        quake_events.register(QuakeClientConnectEvent())
        quake_events.register(QuakeKillEvent())
        quake_events.register(QuakeShutdownGameEvent())
        
        super().__init__(file, quake_events)

    def _parse_line(self, line: str) -> Tuple[str, str, str]:
        line = self._sanitize_line(line)

        TIME_FIELD_SIZE = line.find(" ") - 1
        EVENT_FIELD_START = TIME_FIELD_SIZE + 1

        time = line[0:TIME_FIELD_SIZE]
        log = line[EVENT_FIELD_START:]
        if line[7] == "-":
            raise EventException("No event in the line")

        log_split = log.split(":", 1)
        event = log_split[0].strip()
        detail = log_split[1].strip()

        return time, event, detail

    def _sanitize_line(self, line: str) -> str:
        return line.strip()
