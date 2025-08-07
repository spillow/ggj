"""
game_world.py

GameState coordination and world state management.
Contains the main GameState class that orchestrates all game components.
"""

from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING

from .. import alterego
from ..io_interface import IOInterface, ConsoleIO
from .characters import Hero
from .rooms import Apartment
from .items import Watch

if TYPE_CHECKING:
    from ..delivery import EventQueue


class GameState:
    """
    Tracks the overall state of the game, including the apartment, hero, and time.
    """
    
    class State(IntEnum):
        """
        Enum for game state.
        """
        BEGIN = 0
        APARTMENT_READY = 1
        
    apartment: Apartment
    hero: Hero
    alter_ego: alterego.AlterEgo
    watch: Watch
    io: IOInterface
    event_queue: 'EventQueue' | None

    def __init__(self, io: IOInterface | None = None) -> None:
        """
        Initialize the game state, apartment, hero, and watch.
        """
        self.io = io or ConsoleIO()
        self.apartment = Apartment(self)
        self.hero = Hero(self.apartment.main, self.io)
        self.alter_ego = alterego.AlterEgo()
        self.event_queue: 'EventQueue' | None = None

        self.watch = Watch(self.hero)

    def SetEventQueue(self, queue: 'EventQueue') -> None:
        """
        Set the event queue for scheduled events.
        """
        self.event_queue = queue

    def emit(self, s: str) -> None:
        """
        Print a message to the player.
        """
        self.io.output(s)
        self.io.output("")

    def IntroPrompt(self) -> None:
        """
        Display the introductory prompt to the player.
        """
        self.emit(
            f"You wake up in your apartment.  It is {self.watch.GetDateAsString()}")

        self.emit("In the corner you see a toolbox.")

    def Examine(self) -> None:
        """
        Check the hero's feel and handle passing out if necessary.
        """
        if self.hero.feel <= 0:
            self.hero.feel = 0
            self.emit("I'm feeling very tired.  I'm going to pass out.....")
            for _ in range(5):
                self.emit(".")
                self.io.sleep(1)
            # Now run the alterego during his sleep
            self.alter_ego.run(self)
            # Now that he is finished, reset
            self.hero.feel = self.hero.INITIAL_FEEL
            self.IntroPrompt()

    def prompt(self) -> str:
        """
        Prompt the player for the next action.
        """
        user_input = self.io.get_input("What do we do next?: ")
        return user_input