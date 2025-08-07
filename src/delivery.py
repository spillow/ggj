from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .gamestate import GameState


class EventQueue:
    def __init__(self, state: GameState) -> None:
        self.queue: list[tuple[Callable[[datetime, datetime], None], datetime]] = []
        self.state = state

    def AddEvent(self, action: Callable[[datetime, datetime], None], timeToFire: datetime) -> None:
        self.queue.append((action, timeToFire))

    def Examine(self) -> None:
        toFire = [(action, time) for (action, time) in self.queue if
                  self.state.watch.curr_time >= time]

        rem = [(action, time) for (action, time) in self.queue if
               self.state.watch.curr_time < time]

        self.queue = rem

        for action, time in toFire:
            action(self.state.watch.curr_time, time)
