import datetime
from datetime import timedelta
import alterego
import time
import delivery
from typing import Callable, Any, Optional, List, Dict, Type, Union

# decorator for Interact()
def sameroom(func: Callable) -> Callable:
    def check(self: Any, hero: 'Hero') -> None:
        if hero.GetRoom() == self.GetRoom():
            func(self, hero)
        else:
            print("Must be in the same room as the {0}".format(self.name))

    return check

class Object(object):
    name: str
    weight: int
    parent: Optional['Container']

    def __init__(self, name: str, parent: Optional['Container']) -> None:
        self.name = name
        # set if this is important for a particular object
        self.weight = 0
        self.parent = parent

        if parent is not None:
            self.parent.contents.append(self)

    def Interact(self) -> None:
        assert 'Implement your own Interact()!'

    def __str__(self) -> str:
        return "{0}".format(self.name)

    def GetRoom(self) -> 'Room':
        currParent = self.parent
        while not isinstance(currParent, Room):
            currParent = currParent.parent

        return currParent  # type: ignore

class Food(Object):
    feelBoost: int

    def __init__(self, name: str, parent: Optional['Container'], feelBoost: int) -> None:
        super(Food, self).__init__(name, parent)
        self.feelBoost = feelBoost

    def Eat(self, hero: 'Hero') -> None:
        hero.Pickup(self)
        hero.Destroy([self])
        hero.feel += self.feelBoost
        watch = hero.GetFirstItemByName('watch')
        watch.currTime += timedelta(minutes=20)

class Container(Object):
    contents: List[Object]

    def __init__(self, name: str, parent: Optional['Container']) -> None:
        super(Container, self).__init__(name, parent)
        self.contents: List[Object] = []
        self.weight = 1000 # containers are just too much

    def GetItemsByName(self, name: str) -> List[Object]:
        return [x for x in self.contents if x.name == name]

    def GetFirstItemByName(self, name: str) -> Optional[Object]:
        items = self.GetItemsByName(name)
        if items:
            return items[0]
        else:
            return None

    @sameroom
    def Examine(self, hero: 'Hero') -> None:
        if not self.contents:
            print("nothing to see for the {}".format(self.name))
            print()
        else:
            print("{} contains:".format(self.name))
            for item in self.contents:
                print("    {0}".format(item))
            print()

    def GenFields(self) -> None:
        for item in self.contents:
            setattr(self, item.name, item)

class PhoneNumber:
    name: str
    number: str
    gamestate: 'GameState'

    def __init__(self, name: str, number: str, gamestate: 'GameState') -> None:
        self.name      = name
        self.number    = number
        self.gamestate = gamestate

    def __str__(self) -> str:
        return "{name}: {number}".format(name=self.name, number=self.number)

    def __eq__(self, other: Any) -> bool:
        return other == self.number

class StoreNumber(PhoneNumber):
    def Interact(self) -> None:
        emit = self.gamestate.emit
        items = self.GetStoreItems()
        self.Greeting()
        maxlen = max(len(x) for (x,_) in items.items())
        for (item, cost) in items.items():
            print("{0}${1}.00".format(item+'.'*(maxlen-len(item))+'.........', cost))
        while True:
            choice = input("> ")
            if not choice in (x for (x,_) in items.items()):
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
        raise NotImplementedError

    def Greeting(self) -> None:
        raise NotImplementedError

    def TimeWaste(self, choice: str) -> None:
        raise NotImplementedError

    def FeelChange(self) -> None:
        raise NotImplementedError

    def ScheduleOrder(self, choice: str) -> None:
        raise NotImplementedError

class GroceryNumber(StoreNumber):
    def GetStoreItems(self) -> Dict[str, int]:
        mainroom = self.gamestate.apartment.main
        foods = {
            "spicy-food" : 10,
            "caffeine"   : 5,
            "bananas"    : 2,
            "ice-cubes"  : 6
        }
        return foods

    def Greeting(self) -> None:
        emit = self.gamestate.emit
        emit("Hello this is the grocery store.  What would you like to order?")

    def TimeWaste(self, choice: str) -> None:
        self.gamestate.watch.currTime += timedelta(minutes=30)

    def FeelChange(self) -> None:
        self.gamestate.hero.feel -= 2

    def FoodFeel(self) -> Dict[str, int]:
        feel = {
            "spicy-food" : 30,
            "caffeine"   : 20,
            "bananas"    : 5,
            "ice-cubes"  : 2
        }
        return feel

    def ScheduleOrder(self, choice: str) -> None:
        emit = self.gamestate.emit
        emit("Thanks! We'll get that out to you tomorrow.")
        tomorrow = self.gamestate.watch.currTime + timedelta(days=1)
        def purchase(a: Any, b: Any) -> None:
            Food(choice, self.gamestate.apartment.main.fridge,
                 self.FoodFeel()[choice])
            print("Food truck order has arrived!")
        self.gamestate.eventQueue.AddEvent(purchase, tomorrow)

class HardwareNumber(StoreNumber):
    def GetStoreItems(self) -> Dict[str, int]:
        mainroom = self.gamestate.apartment.main
        hardware = {
            "hammer"        : 20,
            "box-of-nails"  : 5,
            "plywood-sheet" : 30
        }
        return hardware

    def Greeting(self) -> None:
        emit = self.gamestate.emit
        emit("Hello this is the hardware store.  Hope we got what you're looking for!")

    def TimeWaste(self, choice: str) -> None:
        self.gamestate.watch.currTime += timedelta(minutes=2)

    def FeelChange(self) -> None:
        self.gamestate.hero.feel -= 10

    def ScheduleOrder(self, choice: str) -> None:
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
    def Interact(self) -> None:
        print("Calling the super...")
        for i in range(3):
            print("ring...")
            time.sleep(1)

        print("Okay, doesn't look like anybody is answering.")

        self.gamestate.hero.feel -= 30
        self.gamestate.watch.currTime += timedelta(minutes=20)

class TV(Object):
    def __init__(self, parent: Optional['Container']) -> None:
        super(TV, self).__init__("tv", parent)

    @sameroom
    def Examine(self, hero: 'Hero') -> None:
        print("You turn on the tv.")
        print()
        print("""Breaking news: prominent astrophysicists have recently
discovered a strange anomaly in space.  The origins are not yet clear.
Stay tuned for further details.""")

class Phone(Object):
    gamestate: 'GameState'
    phoneNumbers: List[PhoneNumber]

    def __init__(self, gamestate: 'GameState', parent: Optional['Container']) -> None:
        super(Phone, self).__init__("phone", parent)
        self.gamestate = gamestate

        self.phoneNumbers = [
            GroceryNumber("Grocery", "288-7955", gamestate),
            HardwareNumber("Hardware Store", "592-2874", gamestate),
            SuperNumber("The Super", "198-2888", gamestate)
        ]

    def prompt(self, s: str) -> str:
        return input(s)

    @sameroom
    def Rolodex(self, hero: 'Hero') -> None:
        for phonenumber in self.phoneNumbers:
            print(phonenumber)
        print()

    @sameroom
    def Interact(self, hero: 'Hero') -> None:
        number = self.prompt("What number?: ")
        for phoneNumber in self.phoneNumbers:
            if number == phoneNumber.number:
                phoneNumber.Interact()
                return

        print("Who's number is that?")
        print()

class Watch(Object):
    currTime: datetime.datetime

    def __init__(self, parent: Optional['Container']) -> None:
        super(Watch, self).__init__("watch", parent)

        # March 15, 1982 at 3:14 AM
        self.currTime = datetime.datetime(
            1982, # year
            3,    # month
            15,   # day
            3,    # hour
            14)   # minute

    def GetDateAsString(self) -> str:
        return self.currTime.strftime("%A %B %d, %Y at %I:%M %p")

    @sameroom
    def Interact(self, hero: 'Hero') -> None:
        print("\nThe current time is {time}".format(time=self.GetDateAsString()))
        print()

class Hero(Container):
    INITIAL_FEEL: int = 50
    feel: int
    currBalance: int
    state: int

    def __init__(self, startRoom: 'Room') -> None:
        super(Hero, self).__init__("me", startRoom)
        self.feel          = Hero.INITIAL_FEEL
        self.currBalance   = 100
        self.state         = Openable.State.OPEN

    def ClearPath(self, thing: Object) -> bool:
        if self.parent == thing.parent:
            return True

        if isinstance(thing.parent, Openable):
            if thing.parent.state == Openable.State.CLOSED:
                return False

        return self.ClearPath(thing.parent)

    def Pickup(self, thing: Object) -> None:
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
        # stopping logic
        self.parent = room

class Openable(Container):
    state: int

    class State:
        OPEN   = 0
        CLOSED = 1

    def __init__(self, name: str, parent: Optional['Container']) -> None:
        super(Openable, self).__init__(name, parent)
        self.state = Openable.State.CLOSED

    @sameroom
    def Examine(self, hero: 'Hero') -> None:
        if self.state != Openable.State.OPEN:
            print("The {} must be opened first.".format(self.name))
            return

        if not self.contents:
            print("nothing in the {}.".format(self.name))
            print()
        else:
            print("{} contains:".format(self.name))
            for item in self.contents:
                print("    {0}".format(item))
            print()

    def isOpen(self) -> bool:
        return self.state == Openable.State.OPEN

    def isClosed(self) -> bool:
        return self.state == Openable.State.CLOSED

    @sameroom
    def Open(self, hero: 'Hero') -> None:
        if self.state == Openable.State.OPEN:
            print("\nThe {0} is already open.".format(self.name))
        else:
            print("\nThe {0} is now open.".format(self.name))

        self.state = Openable.State.OPEN

    @sameroom
    def Close(self, hero: 'Hero') -> None:
        if self.state == Openable.State.CLOSED:
            print("\nThe {0} is already closed.".format(self.name))
        else:
            print("\nThe {0} is now closed.".format(self.name))

        self.state = Openable.State.CLOSED

    def __str__(self) -> str:
        if self.state == Openable.State.OPEN:
            if self.contents:
                descr = "an open {name}, containing:\n".format(name=self.name)
                for o in self.contents:
                    descr += "    a {name}\n".format(name=o.name)
            else:
                descr = "an open {name} with nothing in it".format(name=self.name)

            return descr.strip()
        elif self.state == Openable.State.CLOSED:
            return "a {name}, it is closed".format(name=self.name)
        else:
            assert False, 'unknown state!'

class Room(Container):
    def __init__(self, name: str, parent: Optional['Container']) -> None:
        super(Room, self).__init__(name, parent)

    def Leave(self, hero: 'Hero') -> bool:
        return True

    def Enter(self, fromRoom: 'Room', hero: 'Hero') -> None:
        if fromRoom.Leave(hero):
            hero.ChangeRoom(self)
            print("You are now in the {}".format(self.name))

class Closet(Room):
    CLOSET_READY    = 0
    CLOSET_NAILED   = 1
    state: int

    def __init__(self, name: str, parent: Optional['Container']) -> None:
        super(Closet, self).__init__(name, parent)
        self.state = Closet.CLOSET_READY

    def Leave(self, hero: 'Hero') -> bool:
        if self.state == Closet.CLOSET_NAILED:
            print("\nPerhaps you should ponder exactly how you'll do that?")
            return False
        elif self.state == Closet.CLOSET_READY:
            return True
        else:
            assert 'unknown closet state!'

class Apartment(Container):
    gamestate: 'GameState'
    main: 'Room'
    bedroom: 'Room'
    bathroom: 'Room'
    closet: 'Closet'

    def __init__(self, gamestate: 'GameState') -> None:
        super(Apartment, self).__init__("apartment", None)
        self.gamestate = gamestate

        self.main     = Room("main", self)
        self.bedroom  = Room("bedroom", self)
        self.bathroom = Room("bathroom", self)
        self.closet   = Closet("closet", self)
        self.GenFields()

        phone   = Phone(gamestate, self.main)
        toolbox = Openable("toolbox", self.main)
        fridge  = Openable("fridge", self.main)
        cabinet = Openable("cabinet", self.main)
        table   = Container("table", self.main)
        tv      = TV(self.main)

        self.main.GenFields()

class GameState:
    BEGIN: int = 0
    APARTMENT_READY: int = 1
    apartment: Apartment
    hero: Hero
    alterEgo: Any
    watch: Watch

    def __init__(self) -> None:
        self.apartment = Apartment(self)
        self.hero      = Hero(self.apartment.main)
        self.alterEgo  = alterego.AlterEgo()

        self.watch = Watch(self.hero)

    def SetEventQueue(self, queue: Any) -> None:
        self.eventQueue = queue

    def emit(self, s: str) -> None:
        print(s)
        print()

    def IntroPrompt(self) -> None:
        self.emit("You wake up in your apartment.  It is {date}".
            format(date=self.watch.GetDateAsString()))

        self.emit("In the corner you see a toolbox.")

    def Examine(self) -> None:
        # Check the 'feel' of our hero to see whether he needs to hit
        # the sack.
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
        userInput = input("What do we do next?: ")
        return userInput
