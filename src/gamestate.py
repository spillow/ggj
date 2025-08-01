"""
gamestate.py

This module defines the core game state and object model for a text-based adventure game.
It includes classes for rooms, containers, objects, the player character (Hero), and
various interactable items such as phones, food, and tools. The game logic for moving
between rooms, interacting with objects, and managing time and events is implemented here.
"""

from typing import Callable, Optional, List, Dict, Union, TYPE_CHECKING
import datetime
from datetime import timedelta
from . import alterego
from .io_interface import IOInterface, ConsoleIO

if TYPE_CHECKING:
    from .delivery import EventQueue

# decorator for Interact()


def sameroom(func: Callable[..., None]) -> Callable[..., None]:
    """
    Decorator to ensure that the hero and the object are in the same room before
    allowing interaction.
    """

    def check(self: 'Object', hero: 'Hero') -> None:
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
    parent: Optional['Container']

    def __init__(self, name: str, parent: Optional['Container']) -> None:
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
        curr_parent = self.parent
        while curr_parent is not None and not isinstance(curr_parent, Room):
            curr_parent = curr_parent.parent

        if curr_parent is None:
            raise ValueError("Object is not contained in a Room")
        return curr_parent


class Food(Object):
    """
    Represents a food item that can be eaten to boost the hero's feel.
    """
    feel_boost: int

    def __init__(self, name: str, parent: Optional['Container'], feelBoost: int) -> None:
        """
        Initialize a food item with a feel boost value.
        """
        super().__init__(name, parent)
        self.feel_boost = feelBoost

    def Interact(self) -> None:
        """
        Food items cannot be directly interacted with - they must be eaten.
        """
        pass

    def Eat(self, hero: 'Hero') -> None:
        """
        Eat the food, increasing the hero's feel and advancing time.
        """
        hero.Pickup(self)
        hero.Destroy([self])
        hero.feel += self.feel_boost
        watch = hero.GetFirstItemByName('watch')
        if isinstance(watch, Watch):
            watch.curr_time += timedelta(minutes=20)


class Container(Object):
    """
    Represents a container that can hold other objects.
    """
    contents: List[Object]

    def __init__(self, name: str, parent: Optional['Container']) -> None:
        """
        Initialize a container with an empty contents list.
        """
        super().__init__(name, parent)
        self.contents: List[Object] = []
        self.weight = 1000  # containers are just too much

    def GetItemsByName(self, name: str) -> List[Object]:
        """
        Return all items in the container with the given name.
        """
        return [x for x in self.contents if x.name == name]

    def GetFirstItemByName(self, name: str) -> Optional[Object]:
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



class PhoneNumber:
    """
    Represents a phone number that can be called in the game.
    """
    name: str
    number: str
    gamestate: 'GameState'

    def __init__(self, name: str, number: str, gamestate: 'GameState') -> None:
        """
        Initialize a phone number with a name and number.
        """
        self.name = name
        self.number = number
        self.gamestate = gamestate

    def __str__(self) -> str:
        """
        Return the string representation of the phone number.
        """
        return f"{self.name}: {self.number}"

    def __eq__(self, other: object) -> bool:
        """
        Compare the phone number to another value.
        """
        return other == self.number


class StoreNumber(PhoneNumber):
    """
    Abstract base class for store phone numbers.
    """

    def Interact(self) -> None:
        """
        Handle the interaction when calling the store, including ordering items.
        """
        emit = self.gamestate.emit
        items = self.GetStoreItems()
        self.Greeting()
        maxlen = max(len(x) for (x, _) in items.items())
        for (item, cost) in items.items():
            self.gamestate.io.output(f"{item+'.'*(maxlen-len(item))+'.........'}${cost}.00")
        while True:
            choice = self.gamestate.io.get_input("> ")
            if not choice in (x for (x, _) in items.items()):
                emit("We don't have that.")
                continue

            self.TimeWaste(choice)
            self.FeelChange()

            if self.gamestate.hero.curr_balance < items[choice]:
                emit("Insufficient funds.")
                break
            self.gamestate.hero.curr_balance -= items[choice]
            self.ScheduleOrder(choice)
            break

    def GetStoreItems(self) -> Dict[str, int]:
        """
        Return a dictionary of items and their costs for the store.
        """
        raise NotImplementedError

    def Greeting(self) -> None:
        """
        Print a greeting message for the store.
        """
        raise NotImplementedError

    def TimeWaste(self, choice: str) -> None:
        """
        Advance time when ordering from the store.
        """
        raise NotImplementedError

    def FeelChange(self) -> None:
        """
        Change the hero's feel when ordering from the store.
        """
        raise NotImplementedError

    def ScheduleOrder(self, choice: str) -> None:
        """
        Schedule the delivery of the ordered item.
        """
        raise NotImplementedError


class GroceryNumber(StoreNumber):
    """
    Phone number for the grocery store.
    """

    def GetStoreItems(self) -> Dict[str, int]:
        """
        Return available grocery items and their costs.
        """
        foods = {
            "spicy-food": 10,
            "caffeine": 5,
            "bananas": 2,
            "ice-cubes": 6
        }
        return foods

    def Greeting(self) -> None:
        """
        Print the grocery store greeting.
        """
        emit = self.gamestate.emit
        emit("Hello this is the grocery store.  What would you like to order?")

    def TimeWaste(self, choice: str) -> None:
        """
        Advance time by 30 minutes for grocery orders.
        """
        self.gamestate.watch.curr_time += timedelta(minutes=30)

    def FeelChange(self) -> None:
        """
        Decrease hero's feel by 2 for grocery orders.
        """
        self.gamestate.hero.feel -= 2

    def FoodFeel(self) -> Dict[str, int]:
        """
        Return the feel boost for each food item.
        """
        feel = {
            "spicy-food": 30,
            "caffeine": 20,
            "bananas": 5,
            "ice-cubes": 2
        }
        return feel

    def ScheduleOrder(self, choice: str) -> None:
        """
        Schedule the delivery of the ordered grocery item for tomorrow.
        """
        emit = self.gamestate.emit
        emit("Thanks! We'll get that out to you tomorrow.")
        tomorrow = self.gamestate.watch.curr_time + timedelta(days=1)

        def purchase(_curr_time: datetime.datetime, _event_time: datetime.datetime) -> None:
            Food(choice, self.gamestate.apartment.main.fridge,
                 self.FoodFeel()[choice])
            self.gamestate.io.output("Food truck order has arrived!")
        if self.gamestate.event_queue is not None:
            self.gamestate.event_queue.AddEvent(purchase, tomorrow)


class HardwareNumber(StoreNumber):
    """
    Phone number for the hardware store.
    """

    def GetStoreItems(self) -> Dict[str, int]:
        """
        Return available hardware items and their costs.
        """
        # mainroom = self.gamestate.apartment.main  # Unused variable
        hardware = {
            "hammer": 20,
            "box-of-nails": 5,
            "plywood-sheet": 30
        }
        return hardware

    def Greeting(self) -> None:
        """
        Print the hardware store greeting.
        """
        emit = self.gamestate.emit
        emit("Hello this is the hardware store.  Hope we got what you're looking for!")

    def TimeWaste(self, choice: str) -> None:
        """
        Advance time by 2 minutes for hardware orders.
        """
        self.gamestate.watch.curr_time += timedelta(minutes=2)

    def FeelChange(self) -> None:
        """
        Decrease hero's feel by 10 for hardware orders.
        """
        self.gamestate.hero.feel -= 10

    def ScheduleOrder(self, choice: str) -> None:
        """
        Schedule the delivery of the ordered hardware item in two days.
        """
        emit = self.gamestate.emit
        emit("Thanks! We'll get that out to you in a couple days.")
        two_days = self.gamestate.watch.curr_time + timedelta(days=2)

        def purchase(_curr_time: datetime.datetime, _event_time: datetime.datetime) -> None:
            if choice == 'plywood-sheet':
                location = self.gamestate.apartment.main.table
            else:
                location = self.gamestate.apartment.main.toolbox

            Object(choice, location)
        if self.gamestate.event_queue is not None:
            self.gamestate.event_queue.AddEvent(purchase, two_days)


class SuperNumber(PhoneNumber):
    """
    Phone number for the building super.
    """

    def Interact(self) -> None:
        """
        Simulate calling the super, who does not answer.
        """
        self.gamestate.io.output("Calling the super...")
        for _ in range(3):
            self.gamestate.io.output("ring...")
            self.gamestate.io.sleep(1)

        self.gamestate.io.output("Okay, doesn't look like anybody is answering.")

        self.gamestate.hero.feel -= 30
        self.gamestate.watch.curr_time += timedelta(minutes=20)


class TV(Object):
    """
    Represents a TV object that can be examined for news.
    """

    def __init__(self, parent: Optional['Container']) -> None:
        """
        Initialize the TV object.
        """
        super().__init__("tv", parent)

    def Interact(self) -> None:
        """
        Watching TV is the main interaction.
        """
        pass

    @sameroom
    def Examine(self, hero: 'Hero') -> None:
        """
        Display a news message when the TV is examined.
        """
        hero.io.output("You turn on the tv.")
        hero.io.output("")
        hero.io.output("""Breaking news: prominent astrophysicists have recently
discovered a strange anomaly in space.  The origins are not yet clear.
Stay tuned for further details.""")


class Phone(Object):
    """
    Represents a phone object that can be used to call numbers.
    """
    gamestate: 'GameState'
    phone_numbers: List[PhoneNumber]

    def __init__(self, gamestate: 'GameState', parent: Optional['Container']) -> None:
        """
        Initialize the phone with a list of phone numbers.
        """
        super().__init__("phone", parent)
        self.gamestate = gamestate

        self.phone_numbers = [
            GroceryNumber("Grocery", "288-7955", gamestate),
            HardwareNumber("Hardware Store", "592-2874", gamestate),
            SuperNumber("The Super", "198-2888", gamestate)
        ]

    def prompt(self, s: str) -> str:
        """
        Prompt the user for input.
        """
        return self.gamestate.io.get_input(s)

    @sameroom
    def Rolodex(self, hero: 'Hero') -> None:
        """
        List all available phone numbers.
        """
        for phonenumber in self.phone_numbers:
            hero.io.output(str(phonenumber))
        hero.io.output("")

    @sameroom
    def Interact(self, _hero: 'Hero') -> None:
        """
        Prompt the user to enter a phone number and handle the call.
        """
        number = self.prompt("What number?: ")
        for phone_number in self.phone_numbers:
            if number == phone_number.number:
                phone_number.Interact()
                return

        self.gamestate.io.output("Who's number is that?")
        self.gamestate.io.output("")


class Watch(Object):
    """
    Represents a watch object that tracks the current game time.
    """
    curr_time: datetime.datetime

    def __init__(self, parent: Optional['Container']) -> None:
        """
        Initialize the watch with a starting time.
        """
        super().__init__("watch", parent)

        # March 15, 1982 at 3:14 AM
        self.curr_time = datetime.datetime(
            1982,  # year
            3,    # month
            15,   # day
            3,    # hour
            14)   # minute

    def GetDateAsString(self) -> str:
        """
        Return the current date and time as a formatted string.
        """
        return self.curr_time.strftime("%A %B %d, %Y at %I:%M %p")

    @sameroom
    def Interact(self, hero: 'Hero') -> None:
        """
        Display the current time.
        """
        hero.io.output(f"\nThe current time is {self.GetDateAsString()}")
        hero.io.output("")


class Hero(Container):
    """
    Represents the player character.
    """
    INITIAL_FEEL: int = 50
    feel: int
    curr_balance: int
    state: int
    io: IOInterface

    def __init__(self, startRoom: 'Room', io: IOInterface) -> None:
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

    def Destroy(self, thing: Union[List[Object], Object]) -> None:
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


class Openable(Container):
    """
    Represents a container that can be opened or closed.
    """
    state: int

    class State:
        """
        Enum for open/closed state.
        """
        OPEN = 0
        CLOSED = 1

    def __init__(self, name: str, parent: Optional['Container']) -> None:
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
        Return a string describing the container and its contents.
        """
        if self.state == Openable.State.OPEN:
            if self.contents:
                descr = f"an open {self.name}, containing:\n"
                for o in self.contents:
                    descr += f"    a {o.name}\n"
            else:
                descr = f"an open {self.name} with nothing in it"

            return descr.strip()
        if self.state == Openable.State.CLOSED:
            return f"a {self.name}, it is closed"
        assert False, 'unknown state!'


class Room(Container):
    """
    Represents a room in the apartment.
    """

    def __init__(self, name: str, parent: Optional['Container']) -> None:
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
    toolbox: 'Openable'
    fridge: 'Openable'
    cabinet: 'Openable'
    table: 'Container'
    tv: 'TV'

    def __init__(self, name: str, parent: Optional['Container'], gamestate: 'GameState') -> None:
        """
        Initialize the main room with its objects.
        """
        super().__init__(name, parent)

        self.phone = Phone(gamestate, self)
        self.toolbox = Openable("toolbox", self)
        self.fridge = Openable("fridge", self)
        self.cabinet = Openable("cabinet", self)
        self.table = Container("table", self)
        self.tv = TV(self)

    def Interact(self) -> None:
        """
        Main room doesn't have special interactions.
        """
        pass


class Closet(Room):
    """
    Represents a closet, which may be nailed shut.
    """
    CLOSET_READY = 0
    CLOSET_NAILED = 1
    state: int

    def __init__(self, name: str, parent: Optional['Container']) -> None:
        """
        Initialize the closet in the ready state.
        """
        super().__init__(name, parent)
        self.state = Closet.CLOSET_READY

    def Interact(self) -> None:
        """
        Closet doesn't have special interactions.
        """
        pass

    def Leave(self, hero: 'Hero') -> bool:
        """
        Determine if the hero can leave the closet.
        """
        if self.state == Closet.CLOSET_NAILED:
            hero.io.output("\nPerhaps you should ponder exactly how you'll do that?")
            return False
        if self.state == Closet.CLOSET_READY:
            return True
        raise ValueError('unknown closet state!')


class Apartment(Container):
    """
    Represents the player's apartment, containing all rooms and main objects.
    """
    gamestate: 'GameState'
    main: 'MainRoom'
    bedroom: 'Room'
    bathroom: 'Room'
    closet: 'Closet'

    def __init__(self, gamestate: 'GameState') -> None:
        """
        Initialize the apartment and its rooms and main objects.
        """
        super().__init__("apartment", None)
        self.gamestate = gamestate

        self.main = MainRoom("main", self, gamestate)
        self.bedroom = Room("bedroom", self)
        self.bathroom = Room("bathroom", self)
        self.closet = Closet("closet", self)

    def Interact(self) -> None:
        """
        Apartment doesn't have special interactions.
        """
        pass


class GameState:
    """
    Tracks the overall state of the game, including the apartment, hero, and time.
    """
    BEGIN: int = 0
    APARTMENT_READY: int = 1
    apartment: Apartment
    hero: Hero
    alter_ego: alterego.AlterEgo
    watch: Watch
    io: IOInterface
    event_queue: Optional['EventQueue']

    def __init__(self, io: Optional[IOInterface] = None) -> None:
        """
        Initialize the game state, apartment, hero, and watch.
        """
        self.io = io or ConsoleIO()
        self.apartment = Apartment(self)
        self.hero = Hero(self.apartment.main, self.io)
        self.alter_ego = alterego.AlterEgo()
        self.event_queue: Optional['EventQueue'] = None

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
