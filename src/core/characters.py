"""
characters.py

Character classes for the game, including the player Hero.
Contains player stats, inventory management, and character-specific logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .game_objects import Container, Object, Openable

if TYPE_CHECKING:
    from ..io_interface import IOInterface
    from .rooms import Room


class Hero(Container):
    """
    Represents the player character.
    """
    INITIAL_FEEL: int = 50
    feel: int
    curr_balance: int
    state: int
    io: IOInterface

    def __init__(self, startRoom: 'Room', io: 'IOInterface') -> None:
        """
        Initialize the hero with starting feel and balance.
        """
        super().__init__("me", startRoom)
        self.feel = Hero.INITIAL_FEEL
        self.curr_balance = 100
        self.state = Openable.State.OPEN
        self.io = io

    def Interact(self) -> None:
        """
        Heroes don't interact with themselves.
        """
        pass

    def ClearPath(self, thing: Object) -> bool:
        """
        Check if there is a clear path to pick up an object
        (i.e., not blocked by closed containers).
        """
        if self.parent == thing.parent:
            return True

        if isinstance(thing.parent, Openable):
            if thing.parent.state == Openable.State.CLOSED:
                return False

        if thing.parent is not None:
            return self.ClearPath(thing.parent)
        return False

    def Pickup(self, thing: Object) -> None:
        """
        Attempt to pick up an object, checking for room and path.
        """
        if not self.GetRoom() is thing.GetRoom():
            self.io.output("I can't pick up something in a different room.")
        elif not self.ClearPath(thing):
            self.io.output("Got to dig a little deeper.")
        elif thing.weight > 100:
            self.io.output("I can't pick this up.")
        elif thing in self.contents:
            self.io.output("Yup, already got that.")
        else:
            self.contents.append(thing)
            if thing.parent is not None:
                thing.parent.contents.remove(thing)
            self.io.output("Got it.")
        self.io.output("")

    def Destroy(self, thing: list[Object] | Object) -> None:
        """
        Remove an object or list of objects from the hero's inventory.
        """
        if isinstance(thing, list):
            for item in thing:
                if item in self.contents:
                    self.contents.remove(item)
                else:
                    self.io.output("I don't have that.")
        else:
            if thing in self.contents:
                self.contents.remove(thing)
            else:
                self.io.output("I don't have that.")

    def ChangeRoom(self, room: 'Room') -> None:
        """
        Move the hero to a different room.
        """
        # stopping logic
        self.parent = room