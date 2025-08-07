"""
inventory_logic.py

Pure business logic for inventory management, pickup rules, and container operations.
Contains no I/O dependencies - only game rules and validations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.game_objects import Object, Container, Openable
    from ..core.characters import Hero


class InventoryRules:
    """
    Business rules for inventory management and item pickup.
    """

    @staticmethod
    def can_pickup_item(hero: 'Hero', item: 'Object') -> tuple[bool, str]:
        """
        Check if hero can pick up an item. Returns (can_pickup, reason).
        """
        # Check room proximity
        if hero.GetRoom() != item.GetRoom():
            return False, "I can't pick up something in a different room."
        
        # Check if path is clear
        if not InventoryRules.has_clear_path(hero, item):
            return False, "Got to dig a little deeper."
        
        # Check weight limit
        if item.weight > 100:
            return False, "I can't pick this up."
        
        # Check if already have it
        if item in hero.contents:
            return False, "Yup, already got that."
        
        return True, "Got it."

    @staticmethod
    def has_clear_path(hero: 'Hero', item: 'Object') -> bool:
        """
        Check if there is a clear path to pick up an object
        (i.e., not blocked by closed containers).
        """
        if hero.parent == item.parent:
            return True

        # Import here to avoid circular imports
        from ..core.game_objects import Openable
        
        if isinstance(item.parent, Openable):
            if item.parent.state == Openable.State.CLOSED:
                return False

        if item.parent is not None:
            return InventoryRules.has_clear_path(hero, item.parent)
        return False

    @staticmethod
    def calculate_total_weight(container: 'Container') -> int:
        """
        Calculate the total weight of all items in a container.
        """
        total = 0
        for item in container.contents:
            total += item.weight
        return total

    @staticmethod
    def can_carry_weight(hero: 'Hero', additional_weight: int) -> bool:
        """
        Check if hero can carry additional weight (100 unit limit).
        """
        current_weight = InventoryRules.calculate_total_weight(hero)
        return current_weight + additional_weight <= 100

    @staticmethod
    def find_items_by_name(container: 'Container', name: str) -> list['Object']:
        """
        Find all items in a container with the given name.
        """
        return [x for x in container.contents if x.name == name]

    @staticmethod
    def find_first_item_by_name(container: 'Container', name: str) -> 'Object' | None:
        """
        Find the first item in a container with the given name.
        """
        items = InventoryRules.find_items_by_name(container, name)
        return items[0] if items else None