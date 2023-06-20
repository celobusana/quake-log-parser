import logging
from typing import Dict, List, Union

from exception import EventException, LogAnalyzerException
from interfaces.game import Game
from interfaces.log import (LogAnalyzer, LogEvent, LogEventDto,
                            LogEventFactory, LogReader)


class QuakeInitLogEvent(LogEvent):
    def __init__(self):
        super().__init__("InitGame")

    def process(self, log_analyzer: "QuakeLogAnalyzer", log_event: LogEventDto):  # type: ignore
        if hasattr(log_analyzer, "game") and log_analyzer.game:
            logging.warning("New game started before the previous one ended")
            log_analyzer.shutdown_game()
        log_analyzer.game = QuakeGame()


class QuakeClientConnectEvent(LogEvent):
    def __init__(self):
        super().__init__("ClientConnect")

    def process(self, log_analyzer: "QuakeLogAnalyzer", log_event: LogEventDto):  # type: ignore
        logging.debug(f"ClientConnect {log_event.log}")


class QuakeShutdownLogEvent(LogEvent):
    def __init__(self):
        super().__init__("ShutdownGame")

    def process(self, log_analyzer: "QuakeLogAnalyzer", log_event: LogEventDto):  # type: ignore
        logging.debug(f"Shutdown {log_event.log}")
        log_analyzer.game.shutdown()
        del (log_analyzer.game)


class QuakeKillEvent(LogEvent):
    def __init__(self):
        super().__init__("Kill")

    def process(self, log_analyzer: "QuakeLogAnalyzer", log_event: LogEventDto):  # type: ignore
        log = log_event.log
        log_starts_at = log.find(":") + 1
        details = log[log_starts_at:]
        weapon = details.rsplit(" ", 1)[-1]
        players = details.replace(f"by {weapon}", "").strip().split(" killed ")
        if len(players) != 2:
            raise LogAnalyzerException(f"Invalid kill event {log}")
        log_analyzer.game.add_kill(players[0], players[1], weapon)


class QuakeGame(Game):
    total_kills: int = 0
    players: Dict[str, Dict[str, Union[str, int]]] = {}
    kills_by_means: Dict[str, int] = {}

    def __init__(self):
        super().__init__("Quake")

    def _reset(self):
        self.total_kills = 0
        self.players = {}
        self.kills_by_means = {}

    def add_kill(self, killer: str, killed: str, weapon: str):
        logging.debug(f" Add Kill -> {killer} killed {killed} by {weapon}")
        self.total_kills += 1

        self.add_player(killer)
        self.add_player(killed)
        self.add_kill_by_means(weapon)
        self.add_kill_by_player(killer, killed)

    def add_kill_by_means(self, weapon: str):
        if weapon not in self.kills_by_means:
            self.kills_by_means[weapon] = 0
        self.kills_by_means[weapon] += 1

    def add_kill_by_player(self, player: str, killed: str):
        points = 1
        if player == killed:
            points = -1
        if player == "<world>":
            player = killed
            points = -1
        self.players[player]["score"] += points  # type: ignore

    def add_player(self, player: str):
        if player == "<world>":
            return
        if player not in self.players:
            self.players[player] = {"nickname": player, "score": 0}

    def get_scores(self) -> Dict[str, int]:
        scores: Dict[str, int] = {}
        for player in self.players:
            scores[player] = int(self.players[player]["score"])
        return scores

    def get_players(self) -> List[str]:
        return list(self.players.keys())

    def stats(self):
        return {
            "total_kills": self.total_kills,
            "players": self.get_players(),
            "kills": self.get_scores(),
            "kills_by_means": self.kills_by_means,
        }


class QuakeLogAnalyzer(LogAnalyzer):
    game: QuakeGame

    def __init__(self, file: LogReader):
        quake_events = LogEventFactory()
        quake_events.register(QuakeInitLogEvent())
        quake_events.register(QuakeClientConnectEvent())
        quake_events.register(QuakeKillEvent())
        quake_events.register(QuakeShutdownLogEvent())

        super().__init__(file, quake_events)

    def _parse_log(self, line: str) -> LogEventDto:
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

        return LogEventDto(event, time, detail)

    def _sanitize_line(self, line: str) -> str:
        return line.strip()
