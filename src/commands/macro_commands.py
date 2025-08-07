"""
Macro Commands module - Pre-defined and custom macro commands for complex sequences.

This module provides common macro commands that combine multiple actions
into single, reusable commands for convenience and efficiency.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List

from .base_command import BaseCommand, MacroCommand
from .game_commands import (
    EnterRoomCommand, OpenThingCommand, GetObjectCommand, 
    ExamineThingCommand, CloseThingCommand, InventoryCommand
)

if TYPE_CHECKING:
    from ..core.game_world import GameState


class ExploreRoomMacro(MacroCommand):
    """
    Macro command to thoroughly explore a room.
    
    Sequence:
    1. Enter the specified room
    2. Inspect the room
    3. Examine each major object
    """
    
    def __init__(self, room_name: str, objects_to_examine: List[str] = None):
        """
        Initialize the explore room macro.
        
        Args:
            room_name: Name of the room to explore
            objects_to_examine: Optional list of specific objects to examine
        """
        from .game_commands import InspectRoomCommand
        
        commands = [
            EnterRoomCommand(room_name),
            InspectRoomCommand()
        ]
        
        # Add examine commands for specified objects
        if objects_to_examine:
            for obj_name in objects_to_examine:
                commands.append(ExamineThingCommand(obj_name))
        
        super().__init__(
            commands=commands,
            description=f"Explore room: {room_name}"
        )
        
        self.room_name = room_name
        self.objects_to_examine = objects_to_examine or []


class GetFromContainerMacro(MacroCommand):
    """
    Macro command to get an item from a container.
    
    Sequence:
    1. Open the container (if it's openable)
    2. Get the item from the container
    3. Optionally close the container
    """
    
    def __init__(self, item_name: str, container_name: str, close_after: bool = False):
        """
        Initialize the get from container macro.
        
        Args:
            item_name: Name of the item to retrieve
            container_name: Name of the container
            close_after: Whether to close the container after getting the item
        """
        commands = [
            OpenThingCommand(container_name),
            GetObjectCommand(item_name, container_name)
        ]
        
        if close_after:
            commands.append(CloseThingCommand(container_name))
        
        super().__init__(
            commands=commands,
            description=f"Get {item_name} from {container_name}"
        )
        
        self.item_name = item_name
        self.container_name = container_name
        self.close_after = close_after


class GatherToolsMacro(MacroCommand):
    """
    Macro command to gather the tools needed for nailing into the closet.
    
    Sequence:
    1. Enter main room
    2. Open toolbox
    3. Get hammer from toolbox
    4. Get box-of-nails from toolbox
    5. Get plywood-sheet from toolbox (if available)
    6. Show inventory
    """
    
    def __init__(self):
        """Initialize the gather tools macro."""
        commands = [
            EnterRoomCommand("main"),
            OpenThingCommand("toolbox"),
            GetObjectCommand("hammer", "toolbox"),
            GetObjectCommand("box-of-nails", "toolbox"),
            # Note: plywood might not be in toolbox by default
            InventoryCommand()
        ]
        
        super().__init__(
            commands=commands,
            description="Gather tools for closet nailing"
        )


class PrepareClosetNailingMacro(MacroCommand):
    """
    Macro command to prepare for and execute closet nailing.
    
    This is a complex macro that handles the entire nailing sequence,
    including gathering tools and entering the closet.
    """
    
    def __init__(self):
        """Initialize the prepare closet nailing macro."""
        from .game_commands import NailSelfInCommand, DebugItemsCommand
        
        commands = [
            # Give debug items to ensure we have everything
            DebugItemsCommand(),
            # Enter the closet
            EnterRoomCommand("closet"),
            # Execute the nailing
            NailSelfInCommand()
        ]
        
        super().__init__(
            commands=commands,
            description="Complete closet nailing sequence (with debug items)"
        )


class InventoryManagementMacro(MacroCommand):
    """
    Macro command for common inventory management tasks.
    
    Sequence:
    1. Show current inventory
    2. Examine each item in inventory (optional)
    """
    
    def __init__(self, examine_items: bool = False):
        """
        Initialize the inventory management macro.
        
        Args:
            examine_items: Whether to examine each item in inventory
        """
        commands = [InventoryCommand()]
        
        # Note: We can't examine items by name without knowing what's in inventory
        # This would require a more dynamic approach
        
        super().__init__(
            commands=commands,
            description="Manage inventory"
        )
        
        self.examine_items = examine_items


class PhoneOrderMacro(MacroCommand):
    """
    Macro command to make a phone order.
    
    Sequence:
    1. Enter main room
    2. Call phone
    3. Show inventory after ordering
    """
    
    def __init__(self):
        """Initialize the phone order macro."""
        from .game_commands import CallPhoneCommand, CheckBalanceCommand
        
        commands = [
            EnterRoomCommand("main"),
            CallPhoneCommand(),
            CheckBalanceCommand(),
            InventoryCommand()
        ]
        
        super().__init__(
            commands=commands,
            description="Make a phone order"
        )


class StatusCheckMacro(MacroCommand):
    """
    Macro command to check all player status indicators.
    
    Sequence:
    1. Check current time
    2. Check balance
    3. Check feel level
    4. Show inventory
    """
    
    def __init__(self):
        """Initialize the status check macro."""
        from .game_commands import (
            LookAtWatchCommand, CheckBalanceCommand, 
            CheckFeelCommand, InventoryCommand
        )
        
        commands = [
            LookAtWatchCommand(),
            CheckBalanceCommand(),
            CheckFeelCommand(),
            InventoryCommand()
        ]
        
        super().__init__(
            commands=commands,
            description="Check all player status"
        )


class MacroBuilder:
    """
    Builder class for creating custom macro commands dynamically.
    
    Provides a fluent interface for building complex macro sequences.
    """
    
    def __init__(self, description: str = "Custom macro"):
        """
        Initialize the macro builder.
        
        Args:
            description: Description of the macro being built
        """
        self.description = description
        self.commands: List[BaseCommand] = []
    
    def enter_room(self, room_name: str) -> "MacroBuilder":
        """Add an enter room command."""
        self.commands.append(EnterRoomCommand(room_name))
        return self
    
    def examine(self, object_name: str) -> "MacroBuilder":
        """Add an examine command."""
        self.commands.append(ExamineThingCommand(object_name))
        return self
    
    def open(self, object_name: str) -> "MacroBuilder":
        """Add an open command."""
        self.commands.append(OpenThingCommand(object_name))
        return self
    
    def close(self, object_name: str) -> "MacroBuilder":
        """Add a close command."""
        self.commands.append(CloseThingCommand(object_name))
        return self
    
    def get_item(self, item_name: str, container_name: str) -> "MacroBuilder":
        """Add a get item command."""
        self.commands.append(GetObjectCommand(item_name, container_name))
        return self
    
    def show_inventory(self) -> "MacroBuilder":
        """Add an inventory command."""
        self.commands.append(InventoryCommand())
        return self
    
    def check_status(self) -> "MacroBuilder":
        """Add all status check commands."""
        from .game_commands import (
            LookAtWatchCommand, CheckBalanceCommand, CheckFeelCommand
        )
        
        self.commands.extend([
            LookAtWatchCommand(),
            CheckBalanceCommand(),
            CheckFeelCommand()
        ])
        return self
    
    def add_command(self, command: BaseCommand) -> "MacroBuilder":
        """Add a custom command."""
        self.commands.append(command)
        return self
    
    def build(self) -> MacroCommand:
        """Build the final macro command."""
        return MacroCommand(
            commands=self.commands.copy(),
            description=self.description
        )
    
    def clear(self) -> "MacroBuilder":
        """Clear all commands and start fresh."""
        self.commands.clear()
        return self
    
    def set_description(self, description: str) -> "MacroBuilder":
        """Set the macro description."""
        self.description = description
        return self


# Factory functions for common macros
def create_explore_room_macro(room_name: str, 
                             objects_to_examine: List[str] = None) -> MacroCommand:
    """Create an explore room macro."""
    return ExploreRoomMacro(room_name, objects_to_examine)


def create_get_from_container_macro(item_name: str, container_name: str, 
                                   close_after: bool = False) -> MacroCommand:
    """Create a get from container macro."""
    return GetFromContainerMacro(item_name, container_name, close_after)


def create_gather_tools_macro() -> MacroCommand:
    """Create a gather tools macro."""
    return GatherToolsMacro()


def create_status_check_macro() -> MacroCommand:
    """Create a status check macro."""
    return StatusCheckMacro()


def create_custom_macro(description: str = "Custom macro") -> MacroBuilder:
    """Create a macro builder for custom macros."""
    return MacroBuilder(description)