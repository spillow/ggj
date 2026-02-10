"""
rooms.py

Room hierarchy and apartment structure for the game.
Contains room definitions, apartment layout, and room-specific logic.
"""

from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING

from .game_objects import Container, Openable

if TYPE_CHECKING:
    from .characters import Hero
    from .items import Journal, Mirror, Phone, TV
    from .game_world import GameState


class Room(Container):
    """
    Represents a room in the apartment.
    """

    def __init__(self, name: str, parent: Container | None) -> None:
        """
        Initialize a room.
        """
        super().__init__(name, parent)

    def Interact(self) -> None:
        """
        Rooms are entered rather than directly interacted with.
        """
        pass

    def Leave(self, _hero: 'Hero') -> bool:
        """
        Determine if the hero can leave the room.
        """
        return True

    def Enter(self, from_room: 'Room', hero: 'Hero') -> None:
        """
        Move the hero into this room from another room.
        """
        if from_room.Leave(hero):
            hero.ChangeRoom(self)
            hero.io.output(f"You are now in the {self.name}")


class MainRoom(Room):
    """
    Represents the main room of the apartment with specific objects.
    """
    phone: 'Phone'
    toolbox: Openable
    fridge: Openable
    cabinet: Openable
    table: Container
    tv: 'TV'

    def __init__(self, name: str, parent: Container | None, gamestate: 'GameState') -> None:
        """
        Initialize the main room with its objects.
        """
        super().__init__(name, parent)

        # Import here to avoid circular imports
        from .items import Phone, TV
        
        self.phone = Phone(gamestate, self)
        self.toolbox = Openable("toolbox", self)
        self.fridge = Openable("fridge", self)
        self.cabinet = Openable("cabinet", self)
        self.table = Container("table", self)
        self.tv = TV(self, gamestate)

    def Interact(self) -> None:
        """
        Main room doesn't have special interactions.
        """
        pass


class Bedroom(Room):
    """
    Represents the bedroom with a bookshelf containing a journal.
    """
    gamestate: 'GameState'
    bookshelf: Container
    journal: 'Journal'
    barricaded: bool

    def __init__(self, name: str, parent: Container | None, gamestate: 'GameState') -> None:
        """
        Initialize the bedroom with its objects.
        """
        super().__init__(name, parent)
        self.gamestate = gamestate
        self.barricaded: bool = False

        from .items import Journal

        self.bookshelf = Container("bookshelf", self)
        self.journal = Journal(self.bookshelf)

    def Interact(self) -> None:
        """
        Bedroom doesn't have special interactions.
        """
        pass


class Bathroom(Room):
    """
    Represents the bathroom with a medicine cabinet and mirror.
    """
    gamestate: 'GameState'
    medicine_cabinet: Openable
    mirror: 'Mirror'

    def __init__(self, name: str, parent: Container | None, gamestate: 'GameState') -> None:
        """
        Initialize the bathroom with its objects.
        """
        super().__init__(name, parent)
        self.gamestate = gamestate

        from .items import Mirror
        from .game_objects import Object

        self.medicine_cabinet = Openable("medicine-cabinet", self)
        self.mirror = Mirror(self, gamestate)
        Object("aspirin", self.medicine_cabinet)

    def Interact(self) -> None:
        """
        Bathroom doesn't have special interactions.
        """
        pass


class Closet(Room):
    """
    Represents a closet, which may be nailed shut.
    """
    
    class State(IntEnum):
        """
        Enum for closet state.
        """
        READY = 0
        NAILED = 1
    
    state: int

    def __init__(self, name: str, parent: Container | None) -> None:
        """
        Initialize the closet in the ready state.
        """
        super().__init__(name, parent)
        self.state = Closet.State.READY

    def Interact(self) -> None:
        """
        Closet doesn't have special interactions.
        """
        pass

    def Leave(self, hero: 'Hero') -> bool:
        """
        Determine if the hero can leave the closet.
        """
        if self.state == Closet.State.NAILED:
            hero.io.output("\nPerhaps you should ponder exactly how you'll do that?")
            return False
        if self.state == Closet.State.READY:
            return True
        raise ValueError('unknown closet state!')


class Apartment(Container):
    """
    Represents the player's apartment, containing all rooms and main objects.
    """
    gamestate: 'GameState'
    main: MainRoom
    bedroom: Bedroom
    bathroom: Bathroom
    closet: Closet

    def __init__(self, gamestate: 'GameState') -> None:
        """
        Initialize the apartment and its rooms and main objects.
        """
        super().__init__("apartment", None)
        self.gamestate = gamestate

        self.main = MainRoom("main", self, gamestate)
        self.bedroom = Bedroom("bedroom", self, gamestate)
        self.bathroom = Bathroom("bathroom", self, gamestate)
        self.closet = Closet("closet", self)

    def Interact(self) -> None:
        """
        Apartment doesn't have special interactions.
        """
        pass