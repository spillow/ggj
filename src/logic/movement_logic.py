"""
movement_logic.py

Pure business logic for room transitions and navigation rules.
Contains movement validation and room state management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.characters import Hero
    from ..core.rooms import Room, Closet


class MovementRules:
    """
    Business rules for room navigation and movement.
    """

    @staticmethod
    def can_leave_room(room: 'Room', hero: 'Hero') -> tuple[bool, str]:
        """
        Check if hero can leave the given room. Returns (can_leave, reason).
        """
        # Import here to avoid circular imports
        from ..core.rooms import Closet
        
        if isinstance(room, Closet):
            if room.state == Closet.State.NAILED:
                return False, "Perhaps you should ponder exactly how you'll do that?"
            elif room.state == Closet.State.READY:
                return True, ""
            else:
                raise ValueError('unknown closet state!')
        
        # Default behavior for regular rooms
        return True, ""

    @staticmethod
    def can_enter_room(target_room: 'Room', from_room: 'Room', hero: 'Hero') -> tuple[bool, str]:
        """
        Check if hero can enter the target room from the current room.
        Returns (can_enter, reason).
        """
        # First check if we can leave the current room
        can_leave, leave_reason = MovementRules.can_leave_room(from_room, hero)
        if not can_leave:
            return False, leave_reason
        
        # Add any target room entry restrictions here
        # For now, all rooms can be entered if you can leave the current room
        return True, ""

    @staticmethod
    def get_room_description(room: 'Room') -> str:
        """
        Get the description message when entering a room.
        """
        return f"You are now in the {room.name}"

    @staticmethod
    def is_same_room(hero: 'Hero', target_room: 'Room') -> bool:
        """
        Check if hero is already in the target room.
        """
        return hero.parent == target_room

    @staticmethod
    def get_hero_current_room(hero: 'Hero') -> 'Room':
        """
        Get the hero's current room.
        """
        return hero.GetRoom()