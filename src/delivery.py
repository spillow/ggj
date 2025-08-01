from typing import List, Tuple, Callable
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .gamestate import GameState


class EventQueue:
    def __init__(self, state: 'GameState') -> None:
        self.queue: List[Tuple[Callable[[datetime.datetime, datetime.datetime], None], datetime.datetime]] = []
        self.state = state

    def AddEvent(self, action: Callable[[datetime.datetime, datetime.datetime], None], timeToFire: datetime.datetime) -> None:
        self.queue.append((action, timeToFire))

    def Examine(self) -> None:
        toFire = [(action, time) for (action, time) in self.queue if
                  self.state.watch.curr_time >= time]

        rem = [(action, time) for (action, time) in self.queue if
               self.state.watch.curr_time < time]

        self.queue = rem

        for action, time in toFire:
            action(self.state.watch.curr_time, time)
