"""
items.py

Specialized game objects including Food, Phone, TV, Watch and phone number system.
Contains item-specific interactions and behaviors.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from .game_objects import Object, Container, sameroom

if TYPE_CHECKING:
    from .characters import Hero
    from .game_world import GameState


class Food(Object):
    """
    Represents a food item that can be eaten to boost the hero's feel.
    """
    feel_boost: int

    def __init__(self, name: str, parent: Container | None, feelBoost: int) -> None:
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


@dataclass
class PhoneNumber:
    """
    Represents a phone number that can be called in the game.
    """
    name: str
    number: str
    gamestate: 'GameState'

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

    def GetStoreItems(self) -> dict[str, int]:
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

    def GetStoreItems(self) -> dict[str, int]:
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

    def FoodFeel(self) -> dict[str, int]:
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

        def purchase(_curr_time: datetime, _event_time: datetime) -> None:
            Food(choice, self.gamestate.apartment.main.fridge,
                 self.FoodFeel()[choice])
            self.gamestate.io.output("Food truck order has arrived!")
        if self.gamestate.event_queue is not None:
            self.gamestate.event_queue.AddEvent(purchase, tomorrow)


class HardwareNumber(StoreNumber):
    """
    Phone number for the hardware store.
    """

    def GetStoreItems(self) -> dict[str, int]:
        """
        Return available hardware items and their costs.
        """
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

        def purchase(_curr_time: datetime, _event_time: datetime) -> None:
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

    def __init__(self, parent: Container | None) -> None:
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
        hero.io.output("")


class Phone(Object):
    """
    Represents a phone object that can be used to call numbers.
    """
    gamestate: 'GameState'
    phone_numbers: list[PhoneNumber]

    def __init__(self, gamestate: 'GameState', parent: Container | None) -> None:
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
    curr_time: datetime

    def __init__(self, parent: Container | None) -> None:
        """
        Initialize the watch with a starting time.
        """
        super().__init__("watch", parent)

        # March 15, 1982 at 3:14 AM
        self.curr_time = datetime(
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