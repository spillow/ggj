"""
test_room_objects.py

Unit tests for new Bedroom and Bathroom room objects from Phase 1:
bookshelf, journal, mirror, medicine-cabinet.
"""

from src.io_interface import MockIO
from src.core.game_world import GameState
from src.core.rooms import Bedroom, Bathroom
from src.core.items import Journal, Mirror
from src.core.game_objects import Container, Openable


class TestBedroom:
    """Tests for the Bedroom room and its objects."""

    def setup_method(self) -> None:
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.bedroom = self.state.apartment.bedroom

    def test_bedroom_is_bedroom_class(self) -> None:
        """Apartment bedroom is a Bedroom instance."""
        assert isinstance(self.bedroom, Bedroom)

    def test_bedroom_has_bookshelf(self) -> None:
        """Bedroom has a bookshelf attribute."""
        assert hasattr(self.bedroom, 'bookshelf')
        assert isinstance(self.bedroom.bookshelf, Container)

    def test_bookshelf_name(self) -> None:
        """Bookshelf has the correct name."""
        assert self.bedroom.bookshelf.name == "bookshelf"

    def test_bookshelf_is_in_bedroom(self) -> None:
        """Bookshelf is a child of the bedroom."""
        assert self.bedroom.bookshelf.parent is self.bedroom

    def test_bookshelf_contains_journal(self) -> None:
        """Bookshelf contains a journal."""
        journal = self.bedroom.bookshelf.GetFirstItemByName("journal")
        assert journal is not None
        assert isinstance(journal, Journal)

    def test_journal_reference(self) -> None:
        """Bedroom.journal references the journal in the bookshelf."""
        assert self.bedroom.journal is not None
        assert isinstance(self.bedroom.journal, Journal)
        bookshelf_journal = self.bedroom.bookshelf.GetFirstItemByName("journal")
        assert self.bedroom.journal is bookshelf_journal


class TestJournal:
    """Tests for the Journal item."""

    def setup_method(self) -> None:
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero
        self.journal = self.state.apartment.bedroom.journal

    def test_journal_name(self) -> None:
        """Journal has the correct name."""
        assert self.journal.name == "journal"

    def test_journal_is_pickable(self) -> None:
        """Journal weight allows it to be picked up (weight <= 100)."""
        assert self.journal.weight <= 100
        assert self.journal.weight == 1

    def test_journal_examine_outputs_text(self) -> None:
        """Journal.Examine() outputs the placeholder description."""
        # Move hero to bedroom so sameroom check passes
        self.hero.ChangeRoom(self.state.apartment.bedroom)
        self.journal.Examine(self.hero)
        combined = " ".join(self.mock_io.outputs)
        assert "worn leather journal" in combined
        assert "handwriting" in combined

    def test_journal_examine_requires_same_room(self) -> None:
        """Journal.Examine() requires hero in same room."""
        # Hero starts in main room, journal is in bedroom
        self.mock_io.clear()
        self.journal.Examine(self.hero)
        combined = " ".join(self.mock_io.outputs)
        assert "Must be in the same room" in combined

    def test_journal_can_be_picked_up(self) -> None:
        """Hero can pick up the journal from the bookshelf."""
        self.hero.ChangeRoom(self.state.apartment.bedroom)
        self.hero.Pickup(self.journal)
        assert self.journal in self.hero.contents


class TestBathroom:
    """Tests for the Bathroom room and its objects."""

    def setup_method(self) -> None:
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.bathroom = self.state.apartment.bathroom

    def test_bathroom_is_bathroom_class(self) -> None:
        """Apartment bathroom is a Bathroom instance."""
        assert isinstance(self.bathroom, Bathroom)

    def test_bathroom_has_medicine_cabinet(self) -> None:
        """Bathroom has a medicine_cabinet attribute."""
        assert hasattr(self.bathroom, 'medicine_cabinet')
        assert isinstance(self.bathroom.medicine_cabinet, Openable)

    def test_medicine_cabinet_name(self) -> None:
        """Medicine cabinet has the correct name."""
        assert self.bathroom.medicine_cabinet.name == "medicine-cabinet"

    def test_medicine_cabinet_starts_closed(self) -> None:
        """Medicine cabinet starts in closed state."""
        assert self.bathroom.medicine_cabinet.isClosed()

    def test_medicine_cabinet_contains_aspirin(self) -> None:
        """Medicine cabinet contains aspirin."""
        aspirin = self.bathroom.medicine_cabinet.GetFirstItemByName("aspirin")
        assert aspirin is not None
        assert aspirin.name == "aspirin"

    def test_bathroom_has_mirror(self) -> None:
        """Bathroom has a mirror attribute."""
        assert hasattr(self.bathroom, 'mirror')
        assert isinstance(self.bathroom.mirror, Mirror)


class TestMirror:
    """Tests for the Mirror item."""

    def setup_method(self) -> None:
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.hero = self.state.hero
        self.mirror = self.state.apartment.bathroom.mirror

    def test_mirror_name(self) -> None:
        """Mirror has the correct name."""
        assert self.mirror.name == "mirror"

    def test_mirror_cannot_be_picked_up(self) -> None:
        """Mirror is too heavy to pick up (weight >= 1000)."""
        assert self.mirror.weight >= 1000

    def test_mirror_examine_outputs_text(self) -> None:
        """Mirror.Examine() outputs the description."""
        self.hero.ChangeRoom(self.state.apartment.bathroom)
        self.mirror.Examine(self.hero)
        combined = " ".join(self.mock_io.outputs)
        assert "mirror" in combined.lower()
        assert "tired" in combined

    def test_mirror_examine_requires_same_room(self) -> None:
        """Mirror.Examine() requires hero in same room."""
        # Hero starts in main room, mirror is in bathroom
        self.mock_io.clear()
        self.mirror.Examine(self.hero)
        combined = " ".join(self.mock_io.outputs)
        assert "Must be in the same room" in combined

    def test_mirror_pickup_fails(self) -> None:
        """Hero cannot pick up the mirror due to weight."""
        self.hero.ChangeRoom(self.state.apartment.bathroom)
        self.hero.Pickup(self.mirror)
        # Mirror should NOT be in hero inventory
        assert self.mirror not in self.hero.contents
