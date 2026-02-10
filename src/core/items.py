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
            "ice-cubes": 6,
            "energy-drinks": 8,
            "canned-soup": 4,
            "chocolate-bar": 3,
            "protein-bar": 6
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
            "ice-cubes": 2,
            "energy-drinks": 25,
            "canned-soup": 10,
            "chocolate-bar": 8,
            "protein-bar": 15
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
            "plywood-sheet": 30,
            "copper-wire": 15,
            "metal-brackets": 10,
            "soldering-iron": 25,
            "duct-tape": 3,
            "wire-cutters": 12
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


class ElectronicsNumber(StoreNumber):
    """
    Phone number for the electronics surplus store.
    """

    def GetStoreItems(self) -> dict[str, int]:
        """
        Return available electronics items and their costs.
        """
        electronics = {
            "vacuum-tubes": 20,
            "crystal-oscillator": 35,
            "copper-coil": 18,
            "battery-pack": 12,
            "signal-amplifier": 40,
            "insulated-cable": 8
        }
        return electronics

    def Greeting(self) -> None:
        """
        Print the electronics surplus store greeting.
        """
        self.gamestate.emit("Electronics Surplus. What do you need?")

    def TimeWaste(self, choice: str) -> None:
        """
        Advance time by 5 minutes for electronics orders.
        """
        self.gamestate.watch.curr_time += timedelta(minutes=5)

    def FeelChange(self) -> None:
        """
        Decrease hero's feel by 5 for electronics orders.
        """
        self.gamestate.hero.feel -= 5

    def ScheduleOrder(self, choice: str) -> None:
        """
        Schedule the delivery of the ordered electronics item in three days.
        """
        emit = self.gamestate.emit
        emit("We'll ship that out. Should arrive in about 3 days.")
        three_days = self.gamestate.watch.curr_time + timedelta(days=3)

        def purchase(_curr_time: datetime, _event_time: datetime) -> None:
            Object(choice, self.gamestate.apartment.main.toolbox)
        if self.gamestate.event_queue is not None:
            self.gamestate.event_queue.AddEvent(purchase, three_days)


# Day-specific responses when the building super answers (Day 4+)
SUPER_RESPONSES: dict[int, str] = {
    4: (
        "Yeah? Oh, you. Listen, other tenants have been complaining about "
        "noises from your apartment at night. Banging, drilling sounds. "
        "And the electrical -- the whole building's been having power surges. "
        "You know anything about that?"
    ),
    5: (
        "Look, whatever you're doing up there, the power company is "
        "threatening to cut the whole building's service. I've got half "
        "a mind to come up there myself."
    ),
}

# Default response for Day 6+ (used when no device-conditional logic applies)
SUPER_DEFAULT_RESPONSE: str = "Things seem to have calmed down. Try to keep it that way."


class SuperNumber(PhoneNumber):
    """
    Phone number for the building super.
    Days 1-3: no answer (rings 3 times). Day 4+: answers with day-specific response.
    """

    def Interact(self) -> None:
        """
        Simulate calling the super. Days 1-3 no answer; Day 4+ answers with
        day-specific response and reduced feel/time penalties.
        """
        day = self.gamestate.get_current_day()

        self.gamestate.io.output("Calling the super...")
        for _ in range(3):
            self.gamestate.io.output("ring...")
            self.gamestate.io.sleep(1)

        if day < 4:
            # Days 1-3: no answer (original behavior)
            self.gamestate.io.output("Okay, doesn't look like anybody is answering.")
            self.gamestate.hero.feel -= 30
            self.gamestate.watch.curr_time += timedelta(minutes=20)
        else:
            # Day 4+: super answers
            response = SUPER_RESPONSES.get(day, SUPER_DEFAULT_RESPONSE)
            self.gamestate.io.output(response)
            self.gamestate.hero.feel -= 10
            self.gamestate.watch.curr_time += timedelta(minutes=5)


# Day-specific TV news broadcasts from STORY.md
TV_NEWS: dict[int, str] = {
    1: (
        "Breaking news: prominent astrophysicists have recently\n"
        "discovered a strange anomaly in space.  The origins are not yet clear.\n"
        "Stay tuned for further details."
    ),
    2: (
        "UPDATE: The anomaly has been confirmed to be growing. Scientists "
        "describe a 'spacetime distortion' of unknown origin. Localized "
        "gravitational effects have been reported near observatories worldwide."
    ),
    3: (
        "DEVELOPING: Gravitational disturbances now reported worldwide. "
        "Emergency services placed on alert. Scientists say the anomaly "
        "appears to be a 'rift' in the fabric of spacetime itself."
    ),
    4: (
        "EMERGENCY BULLETIN: Localized reality distortions reported near "
        "the anomaly's apparent origin point. Residents urged to remain "
        "indoors. The rift appears to be destabilizing surrounding spacetime."
    ),
    5: (
        "Scientists now predict the anomaly will collapse and close within "
        "48 to 72 hours. 'The rift is healing itself,' says Dr. Hernandez "
        "of the Jet Propulsion Laboratory. 'Spacetime wants to be whole.'"
    ),
    6: (
        "The anomaly is visibly shrinking. Scientists are cautiously "
        "optimistic. 'We expect full closure within 24 hours,' says the "
        "lead researcher. Worldwide vigils continue."
    ),
    7: (
        "THE ANOMALY HAS CLOSED. Scientists confirm the rift in spacetime "
        "has sealed completely. The event is over. World leaders express "
        "relief. Scientists warn that the cause remains unknown."
    ),
}


class TV(Object):
    """
    Represents a TV object that can be examined for day-appropriate news.
    """
    gamestate: 'GameState'

    def __init__(self, parent: Container | None, gamestate: 'GameState') -> None:
        """
        Initialize the TV object with a reference to the game state.
        """
        super().__init__("tv", parent)
        self.gamestate = gamestate

    def Interact(self) -> None:
        """
        Watching TV is the main interaction.
        """
        pass

    @sameroom
    def Examine(self, hero: 'Hero') -> None:
        """
        Display day-appropriate news when the TV is examined.
        Days 1-7 show unique broadcasts. Days 8+ default to the Day 7 message.
        """
        day = self.gamestate.get_current_day()
        news = TV_NEWS.get(day, TV_NEWS[7])
        hero.io.output("You turn on the tv.")
        hero.io.output("")
        hero.io.output(news)
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
            ElectronicsNumber("Electronics Surplus", "743-8291", gamestate),
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


class Journal(Object):
    """
    A worn leather journal found in the bedroom bookshelf.
    Contains backstory text (finalized in Phase 5).
    """

    def __init__(self, parent: Container | None) -> None:
        """
        Initialize the journal as a lightweight, pickable object.
        """
        super().__init__("journal", parent)
        self.weight = 1

    def Interact(self) -> None:
        """
        Journal is examined rather than directly interacted with.
        """
        pass

    @sameroom
    def Examine(self, hero: 'Hero') -> None:
        """
        Display the journal description.
        """
        hero.io.output(
            "A worn leather journal. The pages are filled with your "
            "handwriting, though you don't remember writing most of it."
        )
        hero.io.output("")


class Mirror(Object):
    """
    A bathroom mirror. Too heavy to pick up.
    On Day 4+ shows an Alter Ego flicker and sets mirror_seen flag.
    """
    gamestate: 'GameState'

    def __init__(self, parent: Container | None, gamestate: 'GameState') -> None:
        """
        Initialize the mirror as a heavy, non-pickable object.
        """
        super().__init__("mirror", parent)
        self.weight = 1000
        self.gamestate = gamestate

    def Interact(self) -> None:
        """
        Mirror is examined rather than directly interacted with.
        """
        pass

    @sameroom
    def Examine(self, hero: 'Hero') -> None:
        """
        Display what the hero sees in the mirror.
        On Day 4+ shows an AE flicker and sets gamestate.mirror_seen.
        """
        hero.io.output("You look in the mirror. You see yourself. You look tired.")
        day = self.gamestate.get_current_day()
        if day >= 4:
            hero.io.output(
                "For a moment, your reflection moves on its own. "
                "It smiles at you. Then it's gone."
            )
            self.gamestate.mirror_seen = True
        hero.io.output("")