"""
gamestate.py

Legacy gamestate module - now re-exports all classes from the new modular structure.
This file maintains backward compatibility while using the new architecture.
"""

# Re-export all classes from the new modular structure for backward compatibility
from .core.game_objects import Object, Container, Openable, sameroom
from .core.characters import Hero
from .core.rooms import Room, MainRoom, Bedroom, Bathroom, Closet, Apartment
from .core.items import (
    Food, Phone, TV, Watch, PhoneNumber, StoreNumber,
    GroceryNumber, HardwareNumber, ElectronicsNumber, SuperNumber,
    Journal, Mirror
)
from .core.game_world import GameState

# Make sure all the original classes are available
__all__ = [
    'Object', 'Container', 'Openable', 'Hero', 'Room', 'MainRoom',
    'Bedroom', 'Bathroom', 'Closet', 'Apartment', 'Food', 'Phone',
    'TV', 'Watch', 'PhoneNumber', 'StoreNumber', 'GroceryNumber',
    'HardwareNumber', 'ElectronicsNumber', 'SuperNumber',
    'Journal', 'Mirror', 'GameState', 'sameroom'
]