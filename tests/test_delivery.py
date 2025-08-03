"""
Tests for the delivery/event queue system.
"""

import pytest
from datetime import datetime, timedelta
from src.delivery import EventQueue
from src.gamestate import GameState
from src.io_interface import MockIO


class TestEventQueue:
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.queue = EventQueue(self.state)

    def test_event_queue_initialization(self):
        """Test EventQueue can be created."""
        queue = EventQueue(self.state)
        assert queue.state == self.state
        assert queue.queue == []

    def test_add_event(self):
        """Test adding an event to the queue."""
        def test_action(curr_time, event_time):
            pass
        
        fire_time = datetime.now() + timedelta(hours=1)
        self.queue.AddEvent(test_action, fire_time)
        
        assert len(self.queue.queue) == 1
        assert self.queue.queue[0][0] == test_action
        assert self.queue.queue[0][1] == fire_time

    def test_examine_no_events_ready(self):
        """Test examining queue when no events are ready to fire."""
        def test_action(curr_time, event_time):
            pass
        
        # Add event in the future
        future_time = self.state.watch.curr_time + timedelta(hours=1)
        self.queue.AddEvent(test_action, future_time)
        
        initial_queue_length = len(self.queue.queue)
        self.queue.Examine()
        
        # Event should remain in queue
        assert len(self.queue.queue) == initial_queue_length

    def test_examine_events_ready_to_fire(self):
        """Test examining queue when events are ready to fire."""
        executed = []
        
        def test_action(curr_time, event_time):
            executed.append((curr_time, event_time))
        
        # Add event in the past (ready to fire)
        past_time = self.state.watch.curr_time - timedelta(hours=1)
        self.queue.AddEvent(test_action, past_time)
        
        self.queue.Examine()
        
        # Event should be executed and removed from queue
        assert len(self.queue.queue) == 0
        assert len(executed) == 1
        assert executed[0][0] == self.state.watch.curr_time  # curr_time
        assert executed[0][1] == past_time  # event_time

    def test_examine_mixed_events(self):
        """Test examining queue with both ready and future events."""
        executed = []
        
        def test_action(curr_time, event_time):
            executed.append(f"executed at {event_time}")
        
        # Add past event (ready to fire)
        past_time = self.state.watch.curr_time - timedelta(hours=1)
        self.queue.AddEvent(test_action, past_time)
        
        # Add future event (not ready)
        future_time = self.state.watch.curr_time + timedelta(hours=1)
        self.queue.AddEvent(test_action, future_time)
        
        self.queue.Examine()
        
        # Only past event should execute, future event should remain
        assert len(self.queue.queue) == 1
        assert len(executed) == 1
        assert self.queue.queue[0][1] == future_time  # Future event still in queue

    def test_examine_multiple_ready_events(self):
        """Test examining queue with multiple ready events."""
        executed = []
        
        def test_action1(curr_time, event_time):
            executed.append("action1")
        
        def test_action2(curr_time, event_time):
            executed.append("action2")
        
        # Add multiple past events
        past_time1 = self.state.watch.curr_time - timedelta(hours=2)
        past_time2 = self.state.watch.curr_time - timedelta(hours=1)
        
        self.queue.AddEvent(test_action1, past_time1)
        self.queue.AddEvent(test_action2, past_time2)
        
        self.queue.Examine()
        
        # Both events should execute and be removed
        assert len(self.queue.queue) == 0
        assert len(executed) == 2
        assert "action1" in executed
        assert "action2" in executed