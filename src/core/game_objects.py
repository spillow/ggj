"""
game_objects.py

Core game object classes providing the foundation for all game entities.
Contains the base Object class and fundamental container types.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..io_interface import IOInterface


def sameroom(func: Callable[..., None]) -> Callable[..., None]:
    """
    Decorator to ensure that the hero and the object are in the same room before
    allowing interaction.
    """

    def check(self: Object, hero: 'Hero') -> None:
        if hero.GetRoom() == self.GetRoom():
            func(self, hero)
        else:
            hero.io.output(f"Must be in the same room as the {self.name}")

    return check


class Object:
    """
    Base class for all objects in the game. Tracks name, weight, and parent container.
    """
    name: str
    weight: int
    parent: Container | None

    def __init__(self, name: str, parent: Container | None) -> None:
        """
        Initialize an object with a name and parent container.
        """
        self.name = name
        # set if this is important for a particular object
        self.weight = 0
        self.parent = parent

        if parent is not None:
            parent.contents.append(self)

    def Interact(self) -> None:
        """
        Placeholder for interaction logic. Should be overridden by subclasses.
        """
        raise NotImplementedError('Implement your own Interact()!')

    def __str__(self) -> str:
        """
        Return the string representation of the object.
        """
        return f"{self.name}"

    def GetRoom(self) -> 'Room':
        """
        Traverse up the parent chain to find the containing Room.
        """
        # Import here to avoid circular imports
        from .rooms import Room
        
        curr_parent = self.parent
        while curr_parent is not None and not isinstance(curr_parent, Room):
            curr_parent = curr_parent.parent

        if curr_parent is None:
            raise ValueError("Object is not contained in a Room")
        return curr_parent


class Container(Object):
    """
    Represents a container that can hold other objects.
    """
    contents: list[Object]

    def __init__(self, name: str, parent: Container | None) -> None:
        """
        Initialize a container with an empty contents list.
        """
        super().__init__(name, parent)
        self.contents: list[Object] = []
        self.weight = 1000  # containers are just too much

    def GetItemsByName(self, name: str) -> list[Object]:
        """
        Return all items in the container with the given name.
        """
        return [x for x in self.contents if x.name == name]

    def GetFirstItemByName(self, name: str) -> Object | None:
        """
        Return the first item in the container with the given name, or None.
        """
        items = self.GetItemsByName(name)
        if items:
            return items[0]
        return None

    def Interact(self) -> None:
        """
        Containers are examined rather than directly interacted with.
        """
        pass

    @sameroom
    def Examine(self, hero: 'Hero') -> None:
        """
        Print the contents of the container if the hero is in the same room.
        """
        if not self.contents:
            hero.io.output(f"nothing to see for the {self.name}")
            hero.io.output("")
        else:
            hero.io.output(f"{self.name} contains:")
            for item in self.contents:
                hero.io.output(f"    {item}")
            hero.io.output("")


class Openable(Container):
    """
    Represents a container that can be opened or closed.
    """
    state: int

    class State(IntEnum):
        """
        Enum for open/closed state.
        """
        OPEN = 0
        CLOSED = 1

    def __init__(self, name: str, parent: Container | None) -> None:
        """
        Initialize an openable container in the closed state.
        """
        super().__init__(name, parent)
        self.state = Openable.State.CLOSED

    def Interact(self) -> None:
        """
        Openable containers are opened/closed rather than directly interacted with.
        """
        pass

    @sameroom
    def Examine(self, hero: 'Hero') -> None:
        """
        Print the contents if open, otherwise prompt to open first.
        """
        if self.state != Openable.State.OPEN:
            hero.io.output(f"The {self.name} must be opened first.")
            return

        if not self.contents:
            hero.io.output(f"nothing in the {self.name}.")
            hero.io.output("")
        else:
            hero.io.output(f"{self.name} contains:")
            for item in self.contents:
                hero.io.output(f"    {item}")
            hero.io.output("")

    def isOpen(self) -> bool:
        """
        Return True if the container is open.
        """
        return self.state == Openable.State.OPEN

    def isClosed(self) -> bool:
        """
        Return True if the container is closed.
        """
        return self.state == Openable.State.CLOSED

    @sameroom
    def Open(self, hero: 'Hero') -> None:
        """
        Open the container.
        """
        if self.state == Openable.State.OPEN:
            hero.io.output(f"\nThe {self.name} is already open.")
        else:
            hero.io.output(f"\nThe {self.name} is now open.")

        self.state = Openable.State.OPEN

    @sameroom
    def Close(self, hero: 'Hero') -> None:
        """
        Close the container.
        """
        if self.state == Openable.State.CLOSED:
            hero.io.output(f"\nThe {self.name} is already closed.")
        else:
            hero.io.output(f"\nThe {self.name} is now closed.")

        self.state = Openable.State.CLOSED

    def __str__(self) -> str:
        """
        Return the string representation of the openable container.
        """
        return f"{self.name} ({'open' if self.isOpen() else 'closed'})"


