"""
interaction_logic.py

Pure business logic for object interaction rules and validations.
Contains interaction constraints and object state management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.game_objects import Object, Container, Openable
    from ..core.characters import Hero


class InteractionRules:
    """
    Business rules for object interactions and validations.
    """

    @staticmethod
    def can_interact_with_object(hero: 'Hero', obj: 'Object') -> tuple[bool, str]:
        """
        Check if hero can interact with an object. Returns (can_interact, reason).
        """
        if hero.GetRoom() != obj.GetRoom():
            return False, f"Must be in the same room as the {obj.name}"
        return True, ""

    @staticmethod
    def can_examine_container(container: 'Container') -> tuple[bool, str]:
        """
        Check if a container can be examined. Returns (can_examine, reason).
        """
        # Import here to avoid circular imports
        from ..core.game_objects import Openable
        
        if isinstance(container, Openable):
            if container.state != Openable.State.OPEN:
                return False, f"The {container.name} must be opened first."
        
        return True, ""

    @staticmethod
    def can_open_container(container: 'Openable') -> tuple[bool, str]:
        """
        Check if an openable container can be opened. Returns (can_open, reason).
        """
        if container.state == container.State.OPEN:
            return False, f"The {container.name} is already open."
        return True, ""

    @staticmethod
    def can_close_container(container: 'Openable') -> tuple[bool, str]:
        """
        Check if an openable container can be closed. Returns (can_close, reason).
        """
        if container.state == container.State.CLOSED:
            return False, f"The {container.name} is already closed."
        return True, ""

    @staticmethod
    def get_container_contents_description(container: 'Container') -> str:
        """
        Get a description of the container's contents.
        """
        if not container.contents:
            return f"nothing to see for the {container.name}"
        
        description = f"{container.name} contains:\n"
        for item in container.contents:
            description += f"    {item}\n"
        return description.rstrip()

    @staticmethod
    def get_openable_contents_description(container: 'Openable') -> str:
        """
        Get a description of the openable container's contents.
        """
        if not container.contents:
            return f"nothing in the {container.name}."
        
        description = f"{container.name} contains:\n"
        for item in container.contents:
            description += f"    {item}\n"
        return description.rstrip()

    @staticmethod
    def is_container_accessible(container: 'Container') -> bool:
        """
        Check if a container is accessible for item retrieval.
        """
        # Import here to avoid circular imports
        from ..core.game_objects import Openable
        
        if isinstance(container, Openable):
            return container.state == Openable.State.OPEN
        return True