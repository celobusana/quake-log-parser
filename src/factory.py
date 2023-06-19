from exception import EventException

class GameEventFactory():

    def __init__(self):
        self.events = {}

    def register(self, event: "GameEvent"):
        self.events[event.id] = event

    def get(self, event_id: str) -> "GameEvent":
        if event_id not in self.events:
            raise EventException(f"Event {event_id} not registered")
        return self.events[event_id]
