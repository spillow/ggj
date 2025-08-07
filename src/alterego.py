
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .gamestate import GameState


class AlterEgo:
    def __init__(self) -> None:
        pass

    def run(self, gamestate: GameState) -> None:
        pass
