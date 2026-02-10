"""
test_expanded_inventory.py

Unit tests for expanded grocery/hardware stores, new Electronics Surplus store,
and all new item additions from Phase 1.
"""

from datetime import timedelta

from src.io_interface import MockIO
from src.core.game_world import GameState
from src.core.items import (
    GroceryNumber, HardwareNumber, ElectronicsNumber, SuperNumber
)


class TestGroceryExpanded:
    """Tests for expanded grocery store inventory."""

    def setup_method(self) -> None:
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_grocery_has_8_items(self) -> None:
        """GroceryNumber.GetStoreItems() returns 8 items."""
        grocery = GroceryNumber("Grocery", "288-7955", self.state)
        items = grocery.GetStoreItems()
        assert len(items) == 8

    def test_grocery_original_items_unchanged(self) -> None:
        """Original 4 grocery items are present with correct prices."""
        grocery = GroceryNumber("Grocery", "288-7955", self.state)
        items = grocery.GetStoreItems()
        assert items["spicy-food"] == 10
        assert items["caffeine"] == 5
        assert items["bananas"] == 2
        assert items["ice-cubes"] == 6

    def test_grocery_new_items_prices(self) -> None:
        """New grocery items have correct prices."""
        grocery = GroceryNumber("Grocery", "288-7955", self.state)
        items = grocery.GetStoreItems()
        assert items["energy-drinks"] == 8
        assert items["canned-soup"] == 4
        assert items["chocolate-bar"] == 3
        assert items["protein-bar"] == 6

    def test_grocery_food_feel_has_8_items(self) -> None:
        """GroceryNumber.FoodFeel() returns 8 items."""
        grocery = GroceryNumber("Grocery", "288-7955", self.state)
        feel = grocery.FoodFeel()
        assert len(feel) == 8

    def test_grocery_original_feel_boosts_unchanged(self) -> None:
        """Original feel boosts are present with correct values."""
        grocery = GroceryNumber("Grocery", "288-7955", self.state)
        feel = grocery.FoodFeel()
        assert feel["spicy-food"] == 30
        assert feel["caffeine"] == 20
        assert feel["bananas"] == 5
        assert feel["ice-cubes"] == 2

    def test_grocery_new_feel_boosts(self) -> None:
        """New grocery items have correct feel boosts."""
        grocery = GroceryNumber("Grocery", "288-7955", self.state)
        feel = grocery.FoodFeel()
        assert feel["energy-drinks"] == 25
        assert feel["canned-soup"] == 10
        assert feel["chocolate-bar"] == 8
        assert feel["protein-bar"] == 15

    def test_grocery_items_and_feel_keys_match(self) -> None:
        """Every store item has a corresponding feel boost entry."""
        grocery = GroceryNumber("Grocery", "288-7955", self.state)
        items = grocery.GetStoreItems()
        feel = grocery.FoodFeel()
        assert set(items.keys()) == set(feel.keys())


class TestHardwareExpanded:
    """Tests for expanded hardware store inventory."""

    def setup_method(self) -> None:
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_hardware_has_8_items(self) -> None:
        """HardwareNumber.GetStoreItems() returns 8 items."""
        hardware = HardwareNumber("Hardware Store", "592-2874", self.state)
        items = hardware.GetStoreItems()
        assert len(items) == 8

    def test_hardware_original_items_unchanged(self) -> None:
        """Original 3 hardware items are present with correct prices."""
        hardware = HardwareNumber("Hardware Store", "592-2874", self.state)
        items = hardware.GetStoreItems()
        assert items["hammer"] == 20
        assert items["box-of-nails"] == 5
        assert items["plywood-sheet"] == 30

    def test_hardware_new_items_prices(self) -> None:
        """New hardware items have correct prices."""
        hardware = HardwareNumber("Hardware Store", "592-2874", self.state)
        items = hardware.GetStoreItems()
        assert items["copper-wire"] == 15
        assert items["metal-brackets"] == 10
        assert items["soldering-iron"] == 25
        assert items["duct-tape"] == 3
        assert items["wire-cutters"] == 12


class TestElectronicsStore:
    """Tests for the new Electronics Surplus store."""

    def setup_method(self) -> None:
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.electronics = ElectronicsNumber(
            "Electronics Surplus", "743-8291", self.state
        )

    def test_electronics_has_6_items(self) -> None:
        """ElectronicsNumber.GetStoreItems() returns 6 items."""
        items = self.electronics.GetStoreItems()
        assert len(items) == 6

    def test_electronics_item_prices(self) -> None:
        """Electronics items have correct prices."""
        items = self.electronics.GetStoreItems()
        assert items["vacuum-tubes"] == 20
        assert items["crystal-oscillator"] == 35
        assert items["copper-coil"] == 18
        assert items["battery-pack"] == 12
        assert items["signal-amplifier"] == 40
        assert items["insulated-cable"] == 8

    def test_electronics_greeting(self) -> None:
        """ElectronicsNumber.Greeting() outputs correct text."""
        self.electronics.Greeting()
        assert "Electronics Surplus. What do you need?" in self.mock_io.outputs

    def test_electronics_time_waste(self) -> None:
        """ElectronicsNumber.TimeWaste() advances time by 5 minutes."""
        before = self.state.watch.curr_time
        self.electronics.TimeWaste("vacuum-tubes")
        after = self.state.watch.curr_time
        assert after - before == timedelta(minutes=5)

    def test_electronics_feel_change(self) -> None:
        """ElectronicsNumber.FeelChange() decreases feel by 5."""
        before = self.state.hero.feel
        self.electronics.FeelChange()
        assert self.state.hero.feel == before - 5

    def test_electronics_schedule_order_message(self) -> None:
        """ElectronicsNumber.ScheduleOrder() outputs shipping message."""
        from src.delivery import EventQueue
        self.state.SetEventQueue(EventQueue(self.state.watch))
        self.electronics.ScheduleOrder("vacuum-tubes")
        assert "We'll ship that out. Should arrive in about 3 days." in self.mock_io.outputs

    def test_electronics_schedule_order_event(self) -> None:
        """ElectronicsNumber.ScheduleOrder() schedules a 3-day delivery event."""
        from src.delivery import EventQueue
        eq = EventQueue(self.state)
        self.state.SetEventQueue(eq)
        before = self.state.watch.curr_time
        self.electronics.ScheduleOrder("battery-pack")
        # Event queue should have 1 event at 3 days out
        assert len(eq.queue) == 1
        event_time = eq.queue[0][1]
        assert event_time == before + timedelta(days=3)

    def test_electronics_delivery_arrives_at_toolbox(self) -> None:
        """Electronics delivery places item in toolbox after 3 days."""
        from src.delivery import EventQueue
        eq = EventQueue(self.state)
        self.state.SetEventQueue(eq)
        self.electronics.ScheduleOrder("battery-pack")
        # Advance time past delivery
        self.state.watch.curr_time += timedelta(days=4)
        eq.Examine()
        toolbox = self.state.apartment.main.toolbox
        item = toolbox.GetFirstItemByName("battery-pack")
        assert item is not None
        assert item.name == "battery-pack"

    def test_ordering_from_electronics_deducts_balance(self) -> None:
        """Ordering from electronics store deducts correct balance."""
        from src.delivery import EventQueue
        eq = EventQueue(self.state)
        self.state.SetEventQueue(eq)
        # Simulate ordering battery-pack ($12)
        self.mock_io.set_inputs(["battery-pack"])
        before_balance = self.state.hero.curr_balance
        self.electronics.Interact()
        assert self.state.hero.curr_balance == before_balance - 12


class TestPhoneRegistration:
    """Tests for phone number registration."""

    def setup_method(self) -> None:
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_phone_has_4_numbers(self) -> None:
        """Phone now has 4 phone numbers."""
        phone = self.state.apartment.main.phone
        assert len(phone.phone_numbers) == 4

    def test_electronics_in_phone_numbers(self) -> None:
        """Electronics Surplus is registered in the phone."""
        phone = self.state.apartment.main.phone
        names = [pn.name for pn in phone.phone_numbers]
        assert "Electronics Surplus" in names

    def test_electronics_number_is_correct(self) -> None:
        """Electronics Surplus phone number is 743-8291."""
        phone = self.state.apartment.main.phone
        for pn in phone.phone_numbers:
            if pn.name == "Electronics Surplus":
                assert pn.number == "743-8291"
                return
        assert False, "Electronics Surplus not found"
