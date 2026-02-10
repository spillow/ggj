"""
test_evolving_world.py

Unit tests for the evolving TV news and super phone responses (Phase 2).
Tests TV_NEWS dictionary, TV.Examine() per day, SUPER_RESPONSES, and
SuperNumber.Interact() per day.
"""

from datetime import datetime, timedelta

from src.io_interface import MockIO
from src.core.game_world import GameState
from src.core.items import TV_NEWS, SUPER_RESPONSES, SUPER_DEFAULT_RESPONSE


class TestTVNews:
    """Tests for TV news broadcasts changing each day."""

    def setup_method(self) -> None:
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def _set_day(self, day: int) -> None:
        """Set the watch to the start of the given day (midnight)."""
        self.state.watch.curr_time = datetime(1982, 3, 14 + day, 0, 0)

    def test_tv_news_has_7_entries(self) -> None:
        """TV_NEWS dict should have entries for days 1 through 7."""
        assert len(TV_NEWS) == 7
        for day in range(1, 8):
            assert day in TV_NEWS

    def test_tv_day1_message_matches_original(self) -> None:
        """Day 1 TV message must match the original text exactly for backward compat."""
        # Move hero to main room (already there at start)
        self._set_day(1)
        self.state.apartment.main.tv.Examine(self.hero)
        output = "\n".join(self.mock_io.outputs)
        assert "You turn on the tv." in output
        assert "Breaking news: prominent astrophysicists have recently" in output
        assert "discovered a strange anomaly in space." in output
        assert "Stay tuned for further details." in output

    def test_tv_day2_message(self) -> None:
        """Day 2 should show the anomaly growing report."""
        self._set_day(2)
        self.state.apartment.main.tv.Examine(self.hero)
        output = "\n".join(self.mock_io.outputs)
        assert "UPDATE: The anomaly has been confirmed to be growing" in output

    def test_tv_day3_message(self) -> None:
        """Day 3 should show gravitational disturbances."""
        self._set_day(3)
        self.state.apartment.main.tv.Examine(self.hero)
        output = "\n".join(self.mock_io.outputs)
        assert "DEVELOPING: Gravitational disturbances" in output

    def test_tv_day4_message(self) -> None:
        """Day 4 should show the emergency bulletin."""
        self._set_day(4)
        self.state.apartment.main.tv.Examine(self.hero)
        output = "\n".join(self.mock_io.outputs)
        assert "EMERGENCY BULLETIN" in output

    def test_tv_day5_message(self) -> None:
        """Day 5 should predict the anomaly closing."""
        self._set_day(5)
        self.state.apartment.main.tv.Examine(self.hero)
        output = "\n".join(self.mock_io.outputs)
        assert "anomaly will collapse and close" in output
        assert "Dr. Hernandez" in output

    def test_tv_day6_message(self) -> None:
        """Day 6 should say the anomaly is shrinking."""
        self._set_day(6)
        self.state.apartment.main.tv.Examine(self.hero)
        output = "\n".join(self.mock_io.outputs)
        assert "anomaly is visibly shrinking" in output

    def test_tv_day7_message(self) -> None:
        """Day 7 should announce the anomaly has closed."""
        self._set_day(7)
        self.state.apartment.main.tv.Examine(self.hero)
        output = "\n".join(self.mock_io.outputs)
        assert "THE ANOMALY HAS CLOSED" in output

    def test_tv_day8_defaults_to_day7(self) -> None:
        """Days 8+ should default to the Day 7 message."""
        self._set_day(8)
        self.state.apartment.main.tv.Examine(self.hero)
        output = "\n".join(self.mock_io.outputs)
        assert "THE ANOMALY HAS CLOSED" in output

    def test_tv_day10_defaults_to_day7(self) -> None:
        """Day 10 should also get the Day 7 message."""
        self._set_day(10)
        self.state.apartment.main.tv.Examine(self.hero)
        output = "\n".join(self.mock_io.outputs)
        assert "THE ANOMALY HAS CLOSED" in output

    def test_tv_preamble_always_present(self) -> None:
        """Every TV examine should start with 'You turn on the tv.'"""
        for day in range(1, 8):
            self.mock_io.outputs.clear()
            self._set_day(day)
            self.state.apartment.main.tv.Examine(self.hero)
            assert self.mock_io.outputs[0] == "You turn on the tv."


class TestSuperResponses:
    """Tests for the building super's phone responses changing per day."""

    def setup_method(self) -> None:
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero

    def _set_day(self, day: int) -> None:
        """Set the watch to the start of the given day."""
        self.state.watch.curr_time = datetime(1982, 3, 14 + day, 10, 0)

    def _get_super(self):
        """Return the SuperNumber object from the phone."""
        for pn in self.state.apartment.main.phone.phone_numbers:
            if pn.number == "198-2888":
                return pn
        raise AssertionError("SuperNumber not found")

    def test_super_day1_no_answer(self) -> None:
        """Days 1-3: super does not answer."""
        self._set_day(1)
        super_num = self._get_super()
        initial_feel = self.hero.feel
        super_num.Interact()
        output = "\n".join(self.mock_io.outputs)
        assert "Okay, doesn't look like anybody is answering." in output
        assert self.hero.feel == initial_feel - 30

    def test_super_day2_no_answer(self) -> None:
        """Day 2: super does not answer."""
        self._set_day(2)
        super_num = self._get_super()
        super_num.Interact()
        output = "\n".join(self.mock_io.outputs)
        assert "Okay, doesn't look like anybody is answering." in output

    def test_super_day3_no_answer(self) -> None:
        """Day 3: super does not answer."""
        self._set_day(3)
        super_num = self._get_super()
        super_num.Interact()
        output = "\n".join(self.mock_io.outputs)
        assert "Okay, doesn't look like anybody is answering." in output

    def test_super_day4_answers_with_complaint(self) -> None:
        """Day 4: super answers with tenant complaints about noises."""
        self._set_day(4)
        super_num = self._get_super()
        super_num.Interact()
        output = "\n".join(self.mock_io.outputs)
        assert "other tenants have been complaining" in output
        assert "noises from your apartment at night" in output
        assert "power surges" in output

    def test_super_day5_answers_with_threat(self) -> None:
        """Day 5: super answers with threat text."""
        self._set_day(5)
        super_num = self._get_super()
        super_num.Interact()
        output = "\n".join(self.mock_io.outputs)
        assert "power company is threatening" in output
        assert "half a mind to come up there myself" in output

    def test_super_day6_answers_with_default(self) -> None:
        """Day 6+: super answers with default calmed-down response."""
        self._set_day(6)
        super_num = self._get_super()
        super_num.Interact()
        output = "\n".join(self.mock_io.outputs)
        assert "Things seem to have calmed down" in output

    def test_super_day7_answers_with_default(self) -> None:
        """Day 7 also uses the default response."""
        self._set_day(7)
        super_num = self._get_super()
        super_num.Interact()
        output = "\n".join(self.mock_io.outputs)
        assert "Things seem to have calmed down" in output

    def test_super_day4_feel_penalty_reduced(self) -> None:
        """Day 4+ super call should only cost -10 feel (not -30)."""
        self._set_day(4)
        super_num = self._get_super()
        initial_feel = self.hero.feel
        super_num.Interact()
        assert self.hero.feel == initial_feel - 10

    def test_super_day4_time_penalty_reduced(self) -> None:
        """Day 4+ super call should only cost +5 min (not +20)."""
        self._set_day(4)
        super_num = self._get_super()
        initial_time = self.state.watch.curr_time
        super_num.Interact()
        assert self.state.watch.curr_time == initial_time + timedelta(minutes=5)

    def test_super_day1_time_penalty_original(self) -> None:
        """Days 1-3 super call should cost +20 min (original behavior)."""
        self._set_day(1)
        super_num = self._get_super()
        initial_time = self.state.watch.curr_time
        super_num.Interact()
        assert self.state.watch.curr_time == initial_time + timedelta(minutes=20)

    def test_super_always_rings_three_times(self) -> None:
        """The super call should always ring 3 times, even when answering."""
        self._set_day(4)
        super_num = self._get_super()
        super_num.Interact()
        ring_count = sum(1 for o in self.mock_io.outputs if o == "ring...")
        assert ring_count == 3

    def test_super_responses_dict_has_day4_and_day5(self) -> None:
        """SUPER_RESPONSES dict should have entries for days 4 and 5."""
        assert 4 in SUPER_RESPONSES
        assert 5 in SUPER_RESPONSES

    def test_super_default_response_is_string(self) -> None:
        """SUPER_DEFAULT_RESPONSE should be a non-empty string."""
        assert isinstance(SUPER_DEFAULT_RESPONSE, str)
        assert len(SUPER_DEFAULT_RESPONSE) > 0
