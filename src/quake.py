import sys
from pprint import pprint
from file import FileReader
from typing import Tuple, Dict, List
from exceptions import EventException, LogAnalyzerException
from abc import ABC, abstractmethod
import logging


class GameEvent(ABC):

    def __init__(self, id: str):
        self.id = id

    @abstractmethod
    def process(self, log: str):
        pass


class GameEventFactory():

    def __init__(self):
        self.events = {}

    def register(self, event: GameEvent):
        self.events[event.id] = event

    def get(self, event_id: str) -> GameEvent:
        if event_id not in self.events:
            raise EventException(f"Event {event_id} not registered")
        return self.events[event_id]


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


class QuakeGame():

    total_kills: int = 0
    kills_by_means: Dict[str, int] = {}
    kills_by_player: Dict[str, int] = {}
    players: List[str] = []

    def __init__(self):
        logging.debug("New Quake Game")
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


quake_events = GameEventFactory()
quake_events.register(QuakeInitGameEvent())
quake_events.register(QuakeClientConnectEvent())
quake_events.register(QuakeKillEvent())
quake_events.register(QuakeShutdownGameEvent())


class QuakeLogAnalyzer():

    events: GameEventFactory
    game: QuakeGame
    game_id: int = 0

    def __init__(self, log: FileReader, events: GameEventFactory = quake_events):
        self.log = log
        self.events = events

    def process(self):
        lines = 0
        for line in self.log.read_lines():
            lines += 1
            if lines < 10:
                continue
            self._process_line(line)

    def _process_line(self, line: str):
        try:
            time, event, log = self._parse_line(line)
            self._process_event(event, log)
        except EventException as e:
            # logging.warning(e)
            pass
        except Exception as e:
            logging.exception(e)

    def _process_event(self, event: str, log: str):
        self.events.get(event).process(self, log)

    def _sanitize_line(self, line: str) -> str:
        return line.strip()

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

    def shutdown_game(self):
        self.game_id += 1
        self.print_game_stats()
        del (self.game)

    def print_game_stats(self):
        pprint({f"game_{self.game_id}": self.game.stats()})
