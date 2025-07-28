"""
Test suite for Apartment class

Tests the apartment setup, room structure, and initial object placement.
"""

import pytest
import sys
import os

# Add parent directory to path so we can import game modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.io_interface import MockIO
from src.gamestate import GameState, Apartment, Room, Closet, Container, Openable, Phone, TV


class TestApartment:
    """Test the Apartment class setup and structure."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.apartment = self.state.apartment
    
    def test_apartment_initialization(self):
        """Test that apartment initializes correctly."""
        assert isinstance(self.apartment, Apartment)
        assert self.apartment.name == "apartment"
        assert self.apartment.parent is None
        assert self.apartment.gamestate is self.state
    
    def test_apartment_rooms_exist(self):
        """Test that all required rooms are created."""
        # Check that all rooms exist as attributes
        assert hasattr(self.apartment, 'main')
        assert hasattr(self.apartment, 'bedroom')
        assert hasattr(self.apartment, 'bathroom')
        assert hasattr(self.apartment, 'closet')
        
        # Check room types
        assert isinstance(self.apartment.main, Room)
        assert isinstance(self.apartment.bedroom, Room)
        assert isinstance(self.apartment.bathroom, Room)
        assert isinstance(self.apartment.closet, Closet)
    
    def test_apartment_room_names(self):
        """Test that rooms have correct names."""
        assert self.apartment.main.name == "main"
        assert self.apartment.bedroom.name == "bedroom"
        assert self.apartment.bathroom.name == "bathroom"
        assert self.apartment.closet.name == "closet"
    
    def test_apartment_room_parents(self):
        """Test that all rooms have apartment as parent."""
        assert self.apartment.main.parent is self.apartment
        assert self.apartment.bedroom.parent is self.apartment
        assert self.apartment.bathroom.parent is self.apartment
        assert self.apartment.closet.parent is self.apartment
    
    def test_apartment_contains_rooms(self):
        """Test that apartment contents include all rooms."""
        contents_names = [item.name for item in self.apartment.contents]
        assert "main" in contents_names
        assert "bedroom" in contents_names
        assert "bathroom" in contents_names
        assert "closet" in contents_names
        assert len(self.apartment.contents) == 4
    
    def test_main_room_objects(self):
        """Test that main room contains expected objects."""
        main_room = self.apartment.main
        
        # Check that main room has objects
        assert len(main_room.contents) > 0
        
        # Get object names
        object_names = [item.name for item in main_room.contents]
        
        # Check for expected objects
        assert "phone" in object_names
        assert "toolbox" in object_names
        assert "fridge" in object_names
        assert "cabinet" in object_names
        assert "table" in object_names
        assert "tv" in object_names
    
    def test_main_room_object_types(self):
        """Test that main room objects are correct types."""
        main_room = self.apartment.main
        
        # Get objects by name
        phone = main_room.GetFirstItemByName("phone")
        toolbox = main_room.GetFirstItemByName("toolbox")
        fridge = main_room.GetFirstItemByName("fridge")
        cabinet = main_room.GetFirstItemByName("cabinet")
        table = main_room.GetFirstItemByName("table")
        tv = main_room.GetFirstItemByName("tv")
        
        # Check types
        assert isinstance(phone, Phone)
        assert isinstance(toolbox, Openable)
        assert isinstance(fridge, Openable)
        assert isinstance(cabinet, Openable)
        assert isinstance(table, Container)
        assert isinstance(tv, TV)
    
    def test_main_room_object_parents(self):
        """Test that main room objects have correct parent."""
        main_room = self.apartment.main
        
        for obj in main_room.contents:
            assert obj.parent is main_room
    
    def test_openable_objects_start_closed(self):
        """Test that openable objects start in closed state."""
        main_room = self.apartment.main
        
        toolbox = main_room.GetFirstItemByName("toolbox")
        fridge = main_room.GetFirstItemByName("fridge")
        cabinet = main_room.GetFirstItemByName("cabinet")
        
        assert toolbox.isClosed()
        assert fridge.isClosed()
        assert cabinet.isClosed()
    
    def test_closet_initial_state(self):
        """Test that closet starts in ready state."""
        assert self.apartment.closet.state == Closet.CLOSET_READY
    
    def test_phone_configuration(self):
        """Test that phone is properly configured."""
        main_room = self.apartment.main
        phone = main_room.GetFirstItemByName("phone")
        
        assert phone.gamestate is self.state
        assert len(phone.phoneNumbers) == 3  # grocery, hardware, super
        
        # Check phone number names
        number_names = [pn.name for pn in phone.phoneNumbers]
        assert "Grocery" in number_names
        assert "Hardware Store" in number_names
        assert "The Super" in number_names
    
    def test_room_navigation_capability(self):
        """Test that rooms can be found by name for navigation."""
        # Test that apartment can find rooms by name
        main_room = self.apartment.GetFirstItemByName("main")
        bedroom = self.apartment.GetFirstItemByName("bedroom")
        bathroom = self.apartment.GetFirstItemByName("bathroom")
        closet = self.apartment.GetFirstItemByName("closet")
        
        assert main_room is self.apartment.main
        assert bedroom is self.apartment.bedroom
        assert bathroom is self.apartment.bathroom
        assert closet is self.apartment.closet
    
    def test_genfields_functionality(self):
        """Test that GenFields creates dynamic attributes."""
        # After GenFields(), rooms should be accessible as attributes
        assert self.apartment.main is not None
        assert self.apartment.bedroom is not None
        assert self.apartment.bathroom is not None
        assert self.apartment.closet is not None
        
        # Main room should also have GenFields() called
        main_room = self.apartment.main
        assert hasattr(main_room, 'phone')
        assert hasattr(main_room, 'toolbox')
        assert hasattr(main_room, 'fridge')
        assert hasattr(main_room, 'cabinet')
        assert hasattr(main_room, 'table')
        assert hasattr(main_room, 'tv')
    
    def test_empty_rooms_structure(self):
        """Test that other rooms are empty initially."""
        # Bedroom, bathroom should be empty
        assert len(self.apartment.bedroom.contents) == 0
        assert len(self.apartment.bathroom.contents) == 0
        assert len(self.apartment.closet.contents) == 0
    
    def test_apartment_object_access_patterns(self):
        """Test common object access patterns work correctly."""
        # Test accessing objects through different paths
        
        # Direct access through main room
        phone1 = self.apartment.main.GetFirstItemByName("phone")
        
        # Access through apartment navigation
        main_room = self.apartment.GetFirstItemByName("main")
        phone2 = main_room.GetFirstItemByName("phone")
        
        # Access through GenFields dynamic attributes
        phone3 = self.apartment.main.phone
        
        # All should reference the same object
        assert phone1 is phone2
        assert phone2 is phone3
    
    def test_apartment_weight_system(self):
        """Test that containers have appropriate weights."""
        # Containers should have high weight (can't be picked up)
        assert self.apartment.main.weight == 1000
        assert self.apartment.bedroom.weight == 1000
        assert self.apartment.bathroom.weight == 1000
        assert self.apartment.closet.weight == 1000
        
        # Main room objects
        toolbox = self.apartment.main.GetFirstItemByName("toolbox")
        fridge = self.apartment.main.GetFirstItemByName("fridge")
        cabinet = self.apartment.main.GetFirstItemByName("cabinet")
        table = self.apartment.main.GetFirstItemByName("table")
        
        assert toolbox.weight == 1000
        assert fridge.weight == 1000
        assert cabinet.weight == 1000
        assert table.weight == 1000


class TestApartmentIntegration:
    """Test apartment integration with game state."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_io = MockIO()
        self.state = GameState(self.mock_io)
        self.apartment = self.state.apartment
        self.hero = self.state.hero
    
    def test_hero_starts_in_main_room(self):
        """Test that hero starts in the main room."""
        assert self.hero.parent is self.apartment.main
        assert self.hero.GetRoom() is self.apartment.main
    
    def test_hero_can_interact_with_main_room_objects(self):
        """Test that hero can interact with objects in main room."""
        # Hero should be able to examine objects in same room
        phone = self.apartment.main.GetFirstItemByName("phone")
        tv = self.apartment.main.GetFirstItemByName("tv")
        
        # These should not raise exceptions (same room)
        assert self.hero.GetRoom() == phone.GetRoom()
        assert self.hero.GetRoom() == tv.GetRoom()
    
    def test_apartment_supports_room_transitions(self):
        """Test that apartment structure supports room navigation."""
        # Test that rooms can facilitate hero movement
        bedroom = self.apartment.bedroom
        
        # Hero should be able to enter bedroom (if navigation logic allows)
        assert bedroom.Enter is not None
        assert bedroom.Leave is not None
        
        # Bedroom should be a valid destination
        assert bedroom.parent is self.apartment


if __name__ == "__main__":
    pytest.main([__file__])