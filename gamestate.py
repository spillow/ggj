"""
gamestate.py

This module defines the core game state and object model for a text-based adventure game.
It includes classes for rooms, containers, objects, the player character (Hero), and
various interactable items such as phones, food, and tools. The game logic for moving
between rooms, interacting with objects, and managing time and events is implemented here.
"""

import datetime
from datetime import timedelta
import alterego
import time
import delivery
from typing import Callable, Any, Optional, List, Dict, Type, Union

# decorator for Interact()


def sameroom(func: Callable) -> Callable:
    """
    Decorator to ensure that the hero and the object are in the same room before allowing interaction.
    """

    def check(self: Any, hero: 'Hero') -> None:
        if hero.GetRoom() == self.GetRoom():
            func(self, hero)
        else:
            print(f"Must be in the same room as the {self.name}")

    return check


class Object(object):
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
            self.parent.contents.append(self)

    def Interact(self) -> None:
        """
        Placeholder for interaction logic. Should be overridden by subclasses.
        """
        assert 'Implement your own Interact()!'

    def __str__(self) -> str:
        """
        Return the string representation of the object.
        """
        return f"{self.name}"

    def GetRoom(self) -> 'Room':
        """
        Traverse up the parent chain to find the containing Room.
        """
        currParent = self.parent
        while not isinstance(currParent, Room):
            currParent = currParent.parent

        return currParent  # type: ignore


class Food(Object):
    """
    Represents a food item that can be eaten to boost the hero's feel.
    """
    feelBoost: int

    def __init__(self, name: str, parent: Optional['Container'], feelBoost: int) -> None:
        """
        Initialize a food item with a feel boost value.
        """
        super(Food, self).__init__(name, parent)
        self.feelBoost = feelBoost

    def Eat(self, hero: 'Hero') -> None:
        """
        Eat the food, increasing the hero's feel and advancing time.
        """
        hero.Pickup(self)
        hero.Destroy([self])
        hero.feel += self.feelBoost
        watch = hero.GetFirstItemByName('watch')
        watch.currTime += timedelta(minutes=20)


class Container(Object):
    """
    Represents a container that can hold other objects.
    """
    contents: List[Object]

    def __init__(self, name: str, parent: Optional['Container']) -> None:
        """
        Initialize a container with an empty contents list.
        """
        super(Container, self).__init__(name, parent)
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
        else:
            return None

    @sameroom
    def Examine(self, hero: 'Hero') -> None:
        """
        Print the contents of the container if the hero is in the same room.
        """
        if not self.contents:
            print(f"nothing to see for the {self.name}")
            print()
        else:
            print(f"{self.name} contains:")
            for item in self.contents:
                print(f"    {item}")
            print()

    def GenFields(self) -> None:
        """
        Dynamically add each contained item as an attribute of the container.
        """
        for item in self.contents:
            setattr(self, item.name, item)


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

    def __eq__(self, other: Any) -> bool:
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
            print(f"{item+'.'*(maxlen-len(item))+'.........'}${cost}.00")
        while True:
            choice = input("> ")
            if not choice in (x for (x, _) in items.items()):
                emit("We don't have that.")
                continue

            self.TimeWaste(choice)
            self.FeelChange()

            if self.gamestate.hero.currBalance < items[choice]:
                emit("Insufficient funds.")
                break
            else:
                self.gamestate.hero.currBalance -= items[choice]
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
        mainroom = self.gamestate.apartment.main
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
        self.gamestate.watch.currTime += timedelta(minutes=30)

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
        tomorrow = self.gamestate.watch.currTime + timedelta(days=1)

        def purchase(a: Any, b: Any) -> None:
            Food(choice, self.gamestate.apartment.main.fridge,
                 self.FoodFeel()[choice])
            print("Food truck order has arrived!")
        self.gamestate.eventQueue.AddEvent(purchase, tomorrow)


class HardwareNumber(StoreNumber):
    """
    Phone number for the hardware store.
    """

    def GetStoreItems(self) -> Dict[str, int]:
        """
        Return available hardware items and their costs.
        """
        mainroom = self.gamestate.apartment.main
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
        self.gamestate.watch.currTime += timedelta(minutes=2)

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
        twoDays = self.gamestate.watch.currTime + timedelta(days=2)

        def purchase(a: Any, b: Any) -> None:
            if choice == 'plywood-sheet':
                location = self.gamestate.apartment.main.table
            else:
                location = self.gamestate.apartment.main.toolbox

            Object(choice, location)
        self.gamestate.eventQueue.AddEvent(purchase, twoDays)


class SuperNumber(PhoneNumber):
    """
    Phone number for the building super.
    """

    def Interact(self) -> None:
        """
        Simulate calling the super, who does not answer.
        """
        print("Calling the super...")
        for i in range(3):
            print("ring...")
            time.sleep(1)

        print("Okay, doesn't look like anybody is answering.")

        self.gamestate.hero.feel -= 30
        self.gamestate.watch.currTime += timedelta(minutes=20)


class TV(Object):
    """
    Represents a TV object that can be examined for news.
    """

    def __init__(self, parent: Optional['Container']) -> None:
        """
        Initialize the TV object.
        """
        super(TV, self).__init__("tv", parent)

    @sameroom
    def Examine(self, hero: 'Hero') -> None:
        """
        Display a news message when the TV is examined.
        """
        print("You turn on the tv.")
        print()
        print("""Breaking news: prominent astrophysicists have recently
discovered a strange anomaly in space.  The origins are not yet clear.
Stay tuned for further details.""")


class Phone(Object):
    """
    Represents a phone object that can be used to call numbers.
    """
    gamestate: 'GameState'
    phoneNumbers: List[PhoneNumber]

    def __init__(self, gamestate: 'GameState', parent: Optional['Container']) -> None:
        """
        Initialize the phone with a list of phone numbers.
        """
        super(Phone, self).__init__("phone", parent)
        self.gamestate = gamestate

        self.phoneNumbers = [
            GroceryNumber("Grocery", "288-7955", gamestate),
            HardwareNumber("Hardware Store", "592-2874", gamestate),
            SuperNumber("The Super", "198-2888", gamestate)
        ]

    def prompt(self, s: str) -> str:
        """
        Prompt the user for input.
        """
        return input(s)

    @sameroom
    def Rolodex(self, hero: 'Hero') -> None:
        """
        List all available phone numbers.
        """
        for phonenumber in self.phoneNumbers:
            print(phonenumber)
        print()

    @sameroom
    def Interact(self, hero: 'Hero') -> None:
        """
        Prompt the user to enter a phone number and handle the call.
        """
        number = self.prompt("What number?: ")
        for phoneNumber in self.phoneNumbers:
            if number == phoneNumber.number:
                phoneNumber.Interact()
                return

        print("Who's number is that?")
        print()


class Watch(Object):
    """
    Represents a watch object that tracks the current game time.
    """
    currTime: datetime.datetime

    def __init__(self, parent: Optional['Container']) -> None:
        """
        Initialize the watch with a starting time.
        """
        super(Watch, self).__init__("watch", parent)

        # March 15, 1982 at 3:14 AM
        self.currTime = datetime.datetime(
            1982,  # year
            3,    # month
            15,   # day
            3,    # hour
            14)   # minute

    def GetDateAsString(self) -> str:
        """
        Return the current date and time as a formatted string.
        """
        return self.currTime.strftime("%A %B %d, %Y at %I:%M %p")

    @sameroom
    def Interact(self, hero: 'Hero') -> None:
        """
        Display the current time.
        """
        print(f"\nThe current time is {self.GetDateAsString()}")
        print()


class Hero(Container):
    """
    Represents the player character.
    """
    INITIAL_FEEL: int = 50
    feel: int
    currBalance: int
    state: int

    def __init__(self, startRoom: 'Room') -> None:
        """
        Initialize the hero with starting feel and balance.
        """
        super(Hero, self).__init__("me", startRoom)
        self.feel = Hero.INITIAL_FEEL
        self.currBalance = 100
        self.state = Openable.State.OPEN

    def ClearPath(self, thing: Object) -> bool:
        """
        Check if there is a clear path to pick up an object (i.e., not blocked by closed containers).
        """
        if self.parent == thing.parent:
            return True

        if isinstance(thing.parent, Openable):
            if thing.parent.state == Openable.State.CLOSED:
                return False

        return self.ClearPath(thing.parent)

    def Pickup(self, thing: Object) -> None:
        """
        Attempt to pick up an object, checking for room and path.
        """
        if not self.GetRoom() is thing.GetRoom():
            print("I can't pick up something in a different room.")
        elif not self.ClearPath(thing):
            print("Got to dig a little deeper.")
        elif thing.weight > 100:
            print("I can't pick this up.")
        elif thing in self.contents:
            print("Yup, already got that.")
        else:
            self.contents.append(thing)
            thing.parent.contents.remove(thing)
            print("Got it.")
        print()

    def Destroy(self, thing: Union[List[Object], Object]) -> None:
        """
        Remove an object or list of objects from the hero's inventory.
        """
        if isinstance(thing, list):
            for item in thing:
                if item in self.contents:
                    self.contents.remove(item)
                else:
                    print("I don't have that.")
        else:
            if thing in self.contents:
                self.contents.remove(thing)
            else:
                print("I don't have that.")

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
        super(Openable, self).__init__(name, parent)
        self.state = Openable.State.CLOSED

    @sameroom
    def Examine(self, hero: 'Hero') -> None:
        """
        Print the contents if open, otherwise prompt to open first.
        """
        if self.state != Openable.State.OPEN:
            print(f"The {self.name} must be opened first.")
            return

        if not self.contents:
            print(f"nothing in the {self.name}.")
            print()
        else:
            print("{self.name} contains:")
            for item in self.contents:
                print(f"    {item}")
            print()

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
            print(f"\nThe {self.name} is already open.")
        else:
            print(f"\nThe {self.name} is now open.")

        self.state = Openable.State.OPEN

    @sameroom
    def Close(self, hero: 'Hero') -> None:
        """
        Close the container.
        """
        if self.state == Openable.State.CLOSED:
            print(f"\nThe {self.name} is already closed.")
        else:
            print(f"\nThe {self.name} is now closed.")

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
        elif self.state == Openable.State.CLOSED:
            return f"a {self.name}, it is closed"
        else:
            assert False, 'unknown state!'


class Room(Container):
    """
    Represents a room in the apartment.
    """

    def __init__(self, name: str, parent: Optional['Container']) -> None:
        """
        Initialize a room.
        """
        super(Room, self).__init__(name, parent)

    def Leave(self, hero: 'Hero') -> bool:
        """
        Determine if the hero can leave the room.
        """
        return True

    def Enter(self, fromRoom: 'Room', hero: 'Hero') -> None:
        """
        Move the hero into this room from another room.
        """
        if fromRoom.Leave(hero):
            hero.ChangeRoom(self)
            print(f"You are now in the {self.name}")


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
        super(Closet, self).__init__(name, parent)
        self.state = Closet.CLOSET_READY

    def Leave(self, hero: 'Hero') -> bool:
        """
        Determine if the hero can leave the closet.
        """
        if self.state == Closet.CLOSET_NAILED:
            print("\nPerhaps you should ponder exactly how you'll do that?")
            return False
        elif self.state == Closet.CLOSET_READY:
            return True
        else:
            assert 'unknown closet state!'


class Apartment(Container):
    """
    Represents the player's apartment, containing all rooms and main objects.
    """
    gamestate: 'GameState'
    main: 'Room'
    bedroom: 'Room'
    bathroom: 'Room'
    closet: 'Closet'

    def __init__(self, gamestate: 'GameState') -> None:
        """
        Initialize the apartment and its rooms and main objects.
        """
        super(Apartment, self).__init__("apartment", None)
        self.gamestate = gamestate

        self.main = Room("main", self)
        self.bedroom = Room("bedroom", self)
        self.bathroom = Room("bathroom", self)
        self.closet = Closet("closet", self)
        self.GenFields()

        phone = Phone(gamestate, self.main)
        toolbox = Openable("toolbox", self.main)
        fridge = Openable("fridge", self.main)
        cabinet = Openable("cabinet", self.main)
        table = Container("table", self.main)
        tv = TV(self.main)

        self.main.GenFields()


class GameState:
    """
    Tracks the overall state of the game, including the apartment, hero, and time.
    """
    BEGIN: int = 0
    APARTMENT_READY: int = 1
    apartment: Apartment
    hero: Hero
    alterEgo: Any
    watch: Watch

    def __init__(self) -> None:
        """
        Initialize the game state, apartment, hero, and watch.
        """
        self.apartment = Apartment(self)
        self.hero = Hero(self.apartment.main)
        self.alterEgo = alterego.AlterEgo()

        self.watch = Watch(self.hero)

    def SetEventQueue(self, queue: Any) -> None:
        """
        Set the event queue for scheduled events.
        """
        self.eventQueue = queue

    def emit(self, s: str) -> None:
        """
        Print a message to the player.
        """
        print(s)
        print()

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
            for i in range(5):
                self.emit(".")
                time.sleep(1)
            # Now run the alterego during his sleep
            self.alterEgo.run(self)
            # Now that he is finished, reset
            self.hero.feel = self.hero.INITIAL_FEEL
            self.IntroPrompt()

    def prompt(self) -> str:
        """
        Prompt the player for the next action.
        """
        userInput = input("What do we do next?: ")
        return userInput
