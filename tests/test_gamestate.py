"""
Test suite for gamestate.py

Tests the core game objects and mechanics using the MockIO interface.
"""

from io_interface import MockIO
from gamestate import GameState, Object, Container, Hero, Food, Watch, Openable, Room
import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path so we can import game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGameState:
    """Test the main GameState class."""

    def test_gamestate_initialization(self):
        """Test that GameState initializes correctly with MockIO."""
        mock_io = MockIO()
        state = GameState(mock_io)

        assert state.io is mock_io
        assert state.hero is not None
        assert state.apartment is not None
        assert state.watch is not None
        assert state.hero.feel == Hero.INITIAL_FEEL
        assert state.hero.currBalance == 100


class TestHero:
    """Test the Hero class functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def test_hero_initialization(self):
        """Test hero starts with correct values."""
        assert self.hero.feel == Hero.INITIAL_FEEL
        assert self.hero.currBalance == 100
        assert self.hero.io is self.mock_io

    def test_pickup_success(self):
        """Test successful item pickup."""
        # Create a test object in the same room
        test_obj = Object("test-item", self.hero.parent)
        test_obj.weight = 10

        self.hero.Pickup(test_obj)

        assert test_obj in self.hero.contents
        assert "Got it." in self.mock_io.get_all_outputs()

    def test_pickup_too_heavy(self):
        """Test pickup fails for heavy objects."""
        # Create a heavy object
        heavy_obj = Object("heavy-item", self.hero.parent)
        heavy_obj.weight = 150

        self.hero.Pickup(heavy_obj)

        assert heavy_obj not in self.hero.contents
        assert "I can't pick this up." in self.mock_io.get_all_outputs()

    def test_pickup_different_room(self):
        """Test pickup fails for objects in different room."""
        # Create object in different room
        other_room = Room("other", self.state.apartment)
        test_obj = Object("distant-item", other_room)

        self.hero.Pickup(test_obj)

        assert test_obj not in self.hero.contents
        assert "I can't pick up something in a different room." in self.mock_io.get_all_outputs()


class TestFood:
    """Test the Food class functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def test_food_eating(self):
        """Test that eating food increases feel and advances time."""
        initial_feel = self.hero.feel
        initial_time = self.state.watch.currTime

        # Create food in hero's inventory
        food = Food("apple", self.hero, 10)
        food.Eat(self.hero)

        assert self.hero.feel == initial_feel + 10
        assert self.state.watch.currTime == initial_time + \
            timedelta(minutes=20)
        assert food not in self.hero.contents


class TestContainer:
    """Test the Container class functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def test_container_examine_empty(self):
        """Test examining an empty container."""
        container = Container("box", self.hero.parent)
        container.Examine(self.hero)

        outputs = self.mock_io.get_all_outputs()
        assert "nothing to see for the box" in outputs

    def test_container_examine_with_items(self):
        """Test examining a container with items."""
        container = Container("box", self.hero.parent)
        Object("item1", container)
        Object("item2", container)

        container.Examine(self.hero)

        outputs = self.mock_io.get_all_outputs()
        assert "box contains:" in outputs
        assert "    item1" in outputs
        assert "    item2" in outputs

    def test_get_items_by_name(self):
        """Test retrieving items by name."""
        container = Container("box", self.hero.parent)
        item1 = Object("apple", container)
        item2 = Object("apple", container)
        item3 = Object("orange", container)

        apples = container.GetItemsByName("apple")
        oranges = container.GetItemsByName("orange")
        bananas = container.GetItemsByName("banana")

        assert len(apples) == 2
        assert item1 in apples and item2 in apples
        assert len(oranges) == 1
        assert item3 in oranges
        assert len(bananas) == 0


class TestWatch:
    """Test the Watch class functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def test_watch_initialization(self):
        """Test watch starts with correct date."""
        watch = Watch(self.hero)
        expected_date = datetime(1982, 3, 15, 3, 14)
        assert watch.currTime == expected_date

    def test_watch_interact(self):
        """Test interacting with watch displays time."""
        self.state.watch.Interact(self.hero)

        outputs = self.mock_io.get_all_outputs()
        time_output = next(
            (output for output in outputs if "current time" in output), None)
        assert time_output is not None
        assert "Monday March 15, 1982 at 03:14 AM" in time_output


class TestOpenable:
    """Test the Openable class functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def test_openable_starts_closed(self):
        """Test that openable containers start closed."""
        container = Openable("chest", self.hero.parent)
        assert container.isClosed()
        assert not container.isOpen()

    def test_open_container(self):
        """Test opening a container."""
        container = Openable("chest", self.hero.parent)
        container.Open(self.hero)

        assert container.isOpen()
        outputs = self.mock_io.get_all_outputs()
        assert any("The chest is now open." in output for output in outputs)

    def test_close_container(self):
        """Test closing a container."""
        container = Openable("chest", self.hero.parent)
        container.Open(self.hero)
        container.Close(self.hero)

        assert container.isClosed()
        outputs = self.mock_io.get_all_outputs()
        assert any("The chest is now closed." in output for output in outputs)

    def test_examine_closed_container(self):
        """Test examining a closed container."""
        container = Openable("chest", self.hero.parent)
        container.Examine(self.hero)

        outputs = self.mock_io.get_all_outputs()
        assert "The chest must be opened first." in outputs


if __name__ == "__main__":
    pytest.main([__file__])
