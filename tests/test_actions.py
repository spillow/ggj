"""
Test suite for actions.py

Tests all action functions using the MockIO interface to verify
proper behavior and output.
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path so we can import game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.io_interface import MockIO
from src.gamestate import GameState, Object, Container, Hero, Food, Watch, Openable, Room, Closet
from src.delivery import EventQueue
from src import actions


class TestActions:
    """Test all action functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero
        # Set up event queue for mail_check test
        self.event_queue = EventQueue(self.state)
        self.state.SetEventQueue(self.event_queue)

    def test_debug_items(self):
        """Test that debug items are properly added to hero inventory."""
        actions.debug_items(self.state)
        
        # Check that items were added and picked up by the hero
        hammer = self.hero.GetFirstItemByName("hammer")
        nails = self.hero.GetFirstItemByName("box-of-nails")
        plywood = self.hero.GetFirstItemByName("plywood-sheet")
        
        assert hammer is not None
        assert nails is not None
        assert plywood is not None
        # Items should be in hero's inventory even though parent property doesn't change
        assert hammer in self.hero.contents
        assert nails in self.hero.contents
        assert plywood in self.hero.contents
        # Items should not be in main room contents anymore
        assert hammer not in self.state.apartment.main.contents
        assert nails not in self.state.apartment.main.contents
        assert plywood not in self.state.apartment.main.contents

    def test_call_phone(self):
        """Test phone calling action."""
        actions.call_phone(self.state)
        outputs = self.mock_io.get_all_outputs()
        # Phone interaction should produce some output
        assert len(outputs) > 0

    def test_rolodex(self):
        """Test showing phone rolodex."""
        actions.rolodex(self.state)
        outputs = self.mock_io.get_all_outputs()
        # Rolodex should show phone numbers
        assert len(outputs) > 0

    def test_look_at_watch_with_watch(self):
        """Test looking at watch when hero has one."""
        # Hero should start with a watch
        actions.look_at_watch(self.state)
        outputs = self.mock_io.get_all_outputs()
        # Should show time information
        assert len(outputs) > 0

    def test_look_at_watch_without_watch(self):
        """Test looking at watch when hero doesn't have one."""
        # Remove the watch
        watch = self.hero.GetFirstItemByName("watch")
        if watch:
            self.hero.Destroy([watch])
        
        actions.look_at_watch(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "Not carrying a watch!" in " ".join(outputs)

    def test_ponder(self):
        """Test pondering action with valid input."""
        # Set up mock input
        self.mock_io.set_inputs(["2"])  # 2 hours
        
        initial_time = self.state.watch.curr_time
        initial_feel = self.hero.feel
        
        actions.ponder(self.state)
        
        # Check time advanced and feel decreased
        assert self.state.watch.curr_time == initial_time + timedelta(hours=2)
        assert self.hero.feel == initial_feel - 20  # 10 per hour

    def test_ponder_invalid_input(self):
        """Test pondering with invalid then valid input."""
        self.mock_io.set_inputs(["abc", "1"])  # Invalid then valid
        
        initial_time = self.state.watch.curr_time
        actions.ponder(self.state)
        
        outputs = self.mock_io.get_all_outputs()
        assert "What? Give me a number." in " ".join(outputs)
        assert self.state.watch.curr_time == initial_time + timedelta(hours=1)

    def test_ponder_too_long(self):
        """Test pondering with excessive hours."""
        self.mock_io.set_inputs(["2000", "1"])  # Too long, then valid
        
        actions.ponder(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "That's too long to sit and do nothing." in " ".join(outputs)

    def test_check_balance(self):
        """Test checking money balance."""
        actions.check_balance(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert f"Current Balance: ${self.hero.curr_balance}" in " ".join(outputs)

    def test_check_feel_good(self):
        """Test checking feel when feeling good."""
        self.hero.feel = 50  # High feel value
        actions.check_feel(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "Feeling good" in " ".join(outputs)

    def test_check_feel_okay(self):
        """Test checking feel when feeling okay."""
        self.hero.feel = 30  # Medium feel value
        actions.check_feel(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "Feeling okay" in " ".join(outputs)

    def test_check_feel_low(self):
        """Test checking feel when feeling low."""
        self.hero.feel = 10  # Low feel value
        actions.check_feel(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "I'm about to hit the sheets!" in " ".join(outputs)

    def test_mail_check_with_check(self):
        """Test mailing a check when hero has one."""
        # Add a check to hero's inventory properly
        check = Object("check", self.state.apartment.main)
        self.hero.Pickup(check)  # Use proper pickup method
        
        initial_balance = self.hero.curr_balance
        actions.mail_check(self.state)
        
        outputs = self.mock_io.get_all_outputs()
        assert "Check is out.  Big money tomorrow!" in " ".join(outputs)
        # Check should be removed from inventory
        assert self.hero.GetFirstItemByName("check") is None
        
        # Clear output for clean testing (pickup generates output)
        self.mock_io.outputs.clear()

    def test_mail_check_without_check(self):
        """Test mailing a check when hero doesn't have one."""
        actions.mail_check(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "You're not holding a check.  How's the cabinet looking?" in " ".join(outputs)

    def test_mail_check_event_execution(self):
        """Test that mailing a check creates and executes an event."""
        from datetime import timedelta
        
        # Add a check to hero's inventory
        check = Object("check", self.state.apartment.main)
        self.hero.Pickup(check)
        
        initial_balance = self.hero.curr_balance
        actions.mail_check(self.state)
        
        # Advance time to trigger the event
        self.state.watch.curr_time += timedelta(days=2)
        
        # Clear previous outputs
        self.mock_io.clear()
        
        # Execute pending events
        if self.state.event_queue:
            self.state.event_queue.Examine()
        
        # Check that the bank deposit happened
        outputs = self.mock_io.get_all_outputs()
        assert "new bank deposit!" in " ".join(outputs)
        assert self.hero.curr_balance == initial_balance + 100

    def test_inspect_room_with_items(self):
        """Test inspecting room with items present."""
        # Add an item to the room
        test_item = Object("test-item", self.state.apartment.main)
        
        actions.inspect_room(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "You look around the room.  You see:" in " ".join(outputs)
        assert "test-item" in " ".join(outputs)

    def test_inspect_room_empty(self):
        """Test inspecting an empty room."""
        # Clear the room contents
        self.state.apartment.main.contents.clear()
        
        actions.inspect_room(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "Nothing!" in " ".join(outputs)

    def test_eat_thing_success(self):
        """Test eating food from fridge."""
        # Open fridge and add food
        fridge = self.state.apartment.main.fridge
        fridge.Open(self.hero)
        food = Food("apple", fridge, 10)  # 10 feel restoration
        
        initial_feel = self.hero.feel
        actions.eat_thing(self.state, "apple")
        
        # Food should be consumed and feel increased
        assert self.hero.feel > initial_feel

    def test_eat_thing_fridge_closed(self):
        """Test eating when fridge is closed."""
        actions.eat_thing(self.state, "apple")
        outputs = self.mock_io.get_all_outputs()
        assert "Right, I have to open the fridge first." in " ".join(outputs)

    def test_eat_thing_not_near_fridge(self):
        """Test eating when not near fridge."""
        # Move hero to bedroom
        self.state.apartment.bedroom.Enter(self.state.apartment.main, self.hero)
        
        actions.eat_thing(self.state, "apple")
        outputs = self.mock_io.get_all_outputs()
        assert "Step a little closer to the fridge." in " ".join(outputs)

    def test_eat_thing_food_not_found(self):
        """Test eating non-existent food."""
        fridge = self.state.apartment.main.fridge
        fridge.Open(self.hero)
        
        actions.eat_thing(self.state, "nonexistent")
        outputs = self.mock_io.get_all_outputs()
        assert "I don't see that food in there." in " ".join(outputs)

    def test_examine_thing_success(self):
        """Test examining an object in the room."""
        # Add examinable object to room
        test_item = Object("test-item", self.state.apartment.main)
        
        actions.examine_thing(self.state, "test-item")
        # Should not crash (exact output depends on object's Examine method)

    def test_examine_thing_not_found(self):
        """Test examining non-existent object."""
        actions.examine_thing(self.state, "nonexistent")
        outputs = self.mock_io.get_all_outputs()
        assert "I don't see that in the room." in " ".join(outputs)

    def test_watch_tv_success(self):
        """Test watching TV."""
        actions.watch_tv(self.state, "tv")
        # Should not crash and may produce output

    def test_watch_tv_wrong_object(self):
        """Test watching non-TV object."""
        # Add non-TV object
        fake_tv = Object("fake-tv", self.state.apartment.main)
        
        actions.watch_tv(self.state, "fake-tv")
        outputs = self.mock_io.get_all_outputs()
        assert "I don't know how to watch that!" in " ".join(outputs)

    def test_open_thing_success(self):
        """Test opening a container."""
        actions.open_thing(self.state, "fridge")
        # Should attempt to open the fridge

    def test_open_thing_not_found(self):
        """Test opening non-existent object."""
        actions.open_thing(self.state, "nonexistent")
        outputs = self.mock_io.get_all_outputs()
        assert "I don't see that in the room." in " ".join(outputs)

    def test_close_thing_success(self):
        """Test closing a container."""
        # First open the fridge
        fridge = self.state.apartment.main.fridge
        fridge.Open(self.hero)
        
        actions.close_thing(self.state, "fridge")
        # Should attempt to close the fridge

    def test_get_object_from_openable(self):
        """Test getting object from open container."""
        # Open fridge and add item
        fridge = self.state.apartment.main.fridge
        fridge.Open(self.hero)
        test_item = Object("test-item", fridge)
        
        actions.get_object(self.state, "test-item", "fridge")
        # Item should be picked up by hero
        assert self.hero.GetFirstItemByName("test-item") is not None

    def test_get_object_from_closed_container(self):
        """Test getting object from closed container."""
        actions.get_object(self.state, "test-item", "fridge")
        outputs = self.mock_io.get_all_outputs()
        assert "Try opening it first." in " ".join(outputs)

    def test_get_object_not_in_container(self):
        """Test getting non-existent object from container."""
        fridge = self.state.apartment.main.fridge
        fridge.Open(self.hero)
        
        actions.get_object(self.state, "nonexistent", "fridge")
        outputs = self.mock_io.get_all_outputs()
        assert "I don't see that in the fridge." in " ".join(outputs)

    def test_get_object_container_not_found(self):
        """Test getting object from non-existent container."""
        actions.get_object(self.state, "test-item", "nonexistent")
        outputs = self.mock_io.get_all_outputs()
        assert "I don't see that in the room." in " ".join(outputs)

    def test_get_object_from_container(self):
        """Test getting object from a regular Container (not Openable)."""
        # Add item to table (which is a Container, not Openable)
        table = self.state.apartment.main.table
        test_item = Object("test-item", table)
        
        actions.get_object(self.state, "test-item", "table")
        # Item should be picked up by hero
        assert self.hero.GetFirstItemByName("test-item") is not None

    def test_get_object_not_in_container(self):
        """Test getting non-existent object from regular Container."""
        actions.get_object(self.state, "nonexistent", "table")
        outputs = self.mock_io.get_all_outputs()
        assert "I don't see that on the table." in " ".join(outputs)

    def test_get_object_from_non_container(self):
        """Test getting object from object that's not a container."""
        # Add a non-container object to the room
        regular_obj = Object("regular-obj", self.state.apartment.main)
        
        actions.get_object(self.state, "something", "regular-obj")
        outputs = self.mock_io.get_all_outputs()
        assert "How could I do that?" in " ".join(outputs)

    def test_inventory_with_items(self):
        """Test inventory display with items."""
        # Add item to hero's inventory
        test_item = Object("test-item", self.hero)
        
        actions.inventory(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "You are carrying the following:" in " ".join(outputs)
        assert "test-item" in " ".join(outputs)

    def test_inventory_empty(self):
        """Test inventory display when empty."""
        # Clear hero's inventory
        self.hero.contents.clear()
        
        actions.inventory(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "You have no objects in your inventory" in " ".join(outputs)

    def test_enter_room_success(self):
        """Test moving to a different room."""
        actions.enter_room(self.state, "bedroom")
        # Hero should move to bedroom
        assert self.hero.GetRoom() == self.state.apartment.bedroom

    def test_enter_room_same_room(self):
        """Test trying to enter current room."""
        actions.enter_room(self.state, "main")
        outputs = self.mock_io.get_all_outputs()
        assert "Already there." in " ".join(outputs)

    def test_enter_room_not_found(self):
        """Test entering non-existent room."""
        actions.enter_room(self.state, "nonexistent")
        outputs = self.mock_io.get_all_outputs()
        assert "I haven't built that wing yet." in " ".join(outputs)

    def test_nail_self_in_success(self):
        """Test nailing self in closet with required items."""
        # Give hero required items and move to closet
        actions.debug_items(self.state)  # Adds hammer, nails, plywood
        self.state.apartment.closet.Enter(self.state.apartment.main, self.hero)
        
        initial_time = self.state.watch.curr_time
        initial_feel = self.hero.feel
        
        actions.nail_self_in(self.state)
        
        outputs = self.mock_io.get_all_outputs()
        assert "You have successfully nailed yourself into a rather small closet." in " ".join(outputs)
        
        # Check state changes
        assert self.state.apartment.closet.state == Closet.CLOSET_NAILED
        assert self.state.watch.curr_time == initial_time + timedelta(hours=2)
        assert self.hero.feel == initial_feel - 20
        
        # Plywood should be destroyed
        assert self.hero.GetFirstItemByName("plywood-sheet") is None

    def test_nail_self_in_not_in_closet(self):
        """Test nailing self in when not in closet."""
        actions.nail_self_in(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "Gotta be in the closet to start nailing!" in " ".join(outputs)

    def test_nail_self_in_already_nailed(self):
        """Test nailing self in when already nailed."""
        # Move to closet and set as already nailed
        self.state.apartment.closet.Enter(self.state.apartment.main, self.hero)
        self.state.apartment.closet.state = Closet.CLOSET_NAILED
        
        actions.nail_self_in(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "Wasn't once enough?" in " ".join(outputs)

    def test_nail_self_in_no_items(self):
        """Test nailing self in with no items."""
        # Move to closet but clear inventory
        self.state.apartment.closet.Enter(self.state.apartment.main, self.hero)
        self.hero.contents.clear()
        
        actions.nail_self_in(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "You have no objects with which to do that" in " ".join(outputs)

    def test_nail_self_in_missing_hammer(self):
        """Test nailing self in without hammer."""
        self.state.apartment.closet.Enter(self.state.apartment.main, self.hero)
        # Add only nails and plywood, no hammer
        nails = Object("box-of-nails", self.hero)
        plywood = Object("plywood-sheet", self.hero)
        
        actions.nail_self_in(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "Perhaps a hammer?" in " ".join(outputs)

    def test_nail_self_in_missing_nails(self):
        """Test nailing self in without nails."""
        self.state.apartment.closet.Enter(self.state.apartment.main, self.hero)
        # Add only hammer and plywood, no nails
        hammer = Object("hammer", self.hero)
        plywood = Object("plywood-sheet", self.hero)
        
        actions.nail_self_in(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "Perhaps some nails?" in " ".join(outputs)

    def test_nail_self_in_missing_plywood(self):
        """Test nailing self in without plywood."""
        self.state.apartment.closet.Enter(self.state.apartment.main, self.hero)
        # Add only hammer and nails, no plywood
        hammer = Object("hammer", self.hero)
        nails = Object("box-of-nails", self.hero)
        
        actions.nail_self_in(self.state)
        outputs = self.mock_io.get_all_outputs()
        assert "Perhaps some wood?" in " ".join(outputs)


class TestThingifyDecorator:
    """Test the thingify decorator specifically."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_thingify_finds_object(self):
        """Test thingify decorator finds object in room."""
        # Add test object to room
        test_obj = Object("test-obj", self.state.apartment.main)
        
        # Create a simple test function using thingify
        @actions.thingify
        def test_func(state, obj):
            state.hero.io.output(f"Found {obj.name}")
        
        test_func(self.state, "test-obj")
        outputs = self.mock_io.get_all_outputs()
        assert "Found test-obj" in " ".join(outputs)

    def test_thingify_object_not_found(self):
        """Test thingify decorator when object not found."""
        @actions.thingify
        def test_func(state, obj):
            state.hero.io.output(f"Found {obj.name}")
        
        test_func(self.state, "nonexistent")
        outputs = self.mock_io.get_all_outputs()
        assert "I don't see that in the room." in " ".join(outputs)


class TestAttemptFunction:
    """Test the attempt helper function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)

    def test_attempt_success(self):
        """Test attempt function with successful operation."""
        def success_func():
            return "success"
        
        actions.attempt(success_func, "Error", self.state.hero)
        # Should not produce error output
        outputs = self.mock_io.get_all_outputs()
        assert len([o for o in outputs if "Error" in o]) == 0

    def test_attempt_attribute_error(self):
        """Test attempt function with AttributeError."""
        def failing_func():
            raise AttributeError("test error")
        
        actions.attempt(failing_func, "Test error occurred", self.state.hero)
        outputs = self.mock_io.get_all_outputs()
        assert "Test error occurred" in " ".join(outputs)