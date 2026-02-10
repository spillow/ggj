from __future__ import annotations

from collections.abc import Callable
from typing import Any, TYPE_CHECKING
from . import actions
from .gamestate import GameState
from .commands.base_command import BaseCommand
from .commands.game_commands import *

if TYPE_CHECKING:
    from .io_interface import IOInterface

# Command factory functions that return Command objects
def create_debug_items_command() -> BaseCommand:
    return DebugItemsCommand()

def create_call_phone_command() -> BaseCommand:
    return CallPhoneCommand()

def create_rolodex_command() -> BaseCommand:
    return RolodexCommand()

def create_look_at_watch_command() -> BaseCommand:
    return LookAtWatchCommand()

def create_ponder_command(io: 'IOInterface') -> BaseCommand:
    # Ponder needs to ask for hours, keep asking until valid input
    while True:
        hours_str = io.get_input("How many hours?: ")
        try:
            hours = int(hours_str)
            if hours <= 0:
                raise ValueError()
            return PonderCommand(hours)
        except (ValueError, TypeError):
            io.output("What? Give me a number.")
            # Continue the loop to ask again

def create_balance_command() -> BaseCommand:
    return CheckBalanceCommand()

def create_feel_command() -> BaseCommand:
    return CheckFeelCommand()

def create_eat_command(food_name: str) -> BaseCommand:
    return EatThingCommand(food_name)

def create_examine_command(object_name: str) -> BaseCommand:
    return ExamineThingCommand(object_name)

def create_watch_tv_command(object_name: str) -> BaseCommand:
    # The original command expects a specific object name but mainly works with "tv"
    # We'll create a command that checks if the object is "tv"
    class WatchObjectCommand(BaseCommand):
        def __init__(self, obj_name: str):
            super().__init__(f"Watch {obj_name}")
            self.obj_name = obj_name
        
        def execute(self, game_state: 'GameState') -> 'CommandResult':
            from .commands.base_command import CommandResult
            if self.obj_name.lower() != 'tv':
                return CommandResult(
                    success=False,
                    message="I don't know how to watch that!  Not for very long, at least."
                )
            # Use the WatchTvCommand for TV
            from .commands.game_commands import WatchTvCommand
            tv_cmd = WatchTvCommand()
            return tv_cmd.execute(game_state)
    
    return WatchObjectCommand(object_name)

def create_open_command(object_name: str) -> BaseCommand:
    return OpenThingCommand(object_name)

def create_close_command(object_name: str) -> BaseCommand:
    return CloseThingCommand(object_name)

def create_get_object_command(obj_name: str, container_name: str) -> BaseCommand:
    return GetObjectCommand(obj_name, container_name)

def create_inventory_command() -> BaseCommand:
    return InventoryCommand()

def create_enter_room_command(room_name: str) -> BaseCommand:
    return EnterRoomCommand(room_name)

def create_nail_self_in_command() -> BaseCommand:
    return NailSelfInCommand()

def create_inspect_room_command() -> BaseCommand:
    return InspectRoomCommand()

def create_mail_check_command() -> BaseCommand:
    return MailCheckCommand()

def create_undo_command() -> BaseCommand:
    from .commands.command_history import UndoCommand
    # Return a command that will get the history from the game state during execution
    class DeferredUndoCommand(BaseCommand):
        def __init__(self):
            super().__init__("Undo last command")
        
        def execute(self, game_state: 'GameState') -> 'CommandResult':
            from .commands.base_command import CommandResult
            return game_state.command_history.undo(game_state)
    
    return DeferredUndoCommand()

def create_redo_command() -> BaseCommand:
    from .commands.command_history import RedoCommand
    # Return a command that will get the history from the game state during execution
    class DeferredRedoCommand(BaseCommand):
        def __init__(self):
            super().__init__("Redo last undone command")
        
        def execute(self, game_state: 'GameState') -> 'CommandResult':
            from .commands.base_command import CommandResult
            return game_state.command_history.redo(game_state)
    
    return DeferredRedoCommand()

def create_ice_bath_command() -> BaseCommand:
    return TakeIceBathCommand()

def create_disassemble_frame_command() -> BaseCommand:
    return DisassembleFrameCommand()

def create_cut_wires_command() -> BaseCommand:
    return CutWiresCommand()

def create_remove_battery_command() -> BaseCommand:
    return RemoveBatteryCommand()

def create_remove_crystal_command() -> BaseCommand:
    return RemoveCrystalCommand()

def create_barricade_bedroom_command() -> BaseCommand:
    return BarricadeBedroomCommand()

def create_read_journal_command() -> BaseCommand:
    return ReadJournalCommand()

def create_let_go_command() -> BaseCommand:
    return LetGoCommand()

def create_hold_on_command() -> BaseCommand:
    return HoldOnCommand()

# Map commands to their factory functions
COMMANDS: dict[str, Callable[..., BaseCommand]] = {
    "debug items": create_debug_items_command,
    "call phone": create_call_phone_command,
    "rolodex": create_rolodex_command,
    "look at watch": create_look_at_watch_command,
    "ponder": create_ponder_command,
    "balance": create_balance_command,
    "feel": create_feel_command,
    "eat {a}": create_eat_command,
    "examine {a}": create_examine_command,
    "watch {a}": create_watch_tv_command,
    "look in {a}": create_examine_command,
    "open {a}": create_open_command,
    "close {a}": create_close_command,
    "pick up {a} from {b}": create_get_object_command,
    "get {a} from {b}": create_get_object_command,
    "inventory": create_inventory_command,
    "go in {a}": create_enter_room_command,
    "go to {a}": create_enter_room_command,
    "enter {a}": create_enter_room_command,
    "enter the {a}": create_enter_room_command,
    "nail wood to exit": create_nail_self_in_command,
    "nail wood to door": create_nail_self_in_command,
    "nail self in": create_nail_self_in_command,
    "nail self in closet": create_nail_self_in_command,
    "inspect room": create_inspect_room_command,
    "view room": create_inspect_room_command,
    "look around room": create_inspect_room_command,
    "mail check": create_mail_check_command,
    "take an ice bath": create_ice_bath_command,
    "take ice bath": create_ice_bath_command,
    "ice bath": create_ice_bath_command,
    "disassemble frame": create_disassemble_frame_command,
    "cut wires": create_cut_wires_command,
    "remove battery": create_remove_battery_command,
    "remove crystal": create_remove_crystal_command,
    "barricade bedroom": create_barricade_bedroom_command,
    "read journal": create_read_journal_command,
    "let go": create_let_go_command,
    "hold on": create_hold_on_command,
    "undo": create_undo_command,
    "redo": create_redo_command
}


class PatVar:
    def __init__(self, s: str) -> None:
        self.s = s

    def __bool__(self) -> bool:
        return bool(self.s and self.s[0] == '{' and self.s[-1] == '}')


def unify(commandTokens: list[str], inputTokens: list[str]) -> tuple[bool, list[str]]:
    bindings: list[str] = []
    for ct, it in zip(commandTokens, inputTokens):
        if PatVar(ct):
            bindings.append(it)
        elif ct != it:
            return (False, [])

    return (True, bindings)


def expand(command: str, userInput: str) -> tuple[bool, list[str]]:
    commandTokens = command.split()
    inputTokens = userInput.split()

    if len(commandTokens) != len(inputTokens):
        return (False, [])

    return unify(commandTokens, inputTokens)

# returns a two tuple
# (ok, errorMessage)
# or
# (ok, action)
# ok whether the parse succeeded
# errorMessage on fail or action on success


def parse(userInput: str, io: 'IOInterface' = None) -> tuple[bool, BaseCommand | str]:
    """
    Parse user input and return a Command object or error message.
    
    Returns:
        - (True, Command) if parsing succeeded
        - (False, error_message) if parsing failed
    """
    for command, factory in COMMANDS.items():
        ok, args = expand(command, userInput)
        if ok:
            try:
                # Handle special case for ponder command that needs IO
                if factory == create_ponder_command and io:
                    cmd = factory(io)
                else:
                    cmd = factory(*args)
                return (True, cmd)
            except Exception as e:
                return (False, f"Error creating command: {str(e)}")

    return (False, "Don't understand command.")


# Legacy compatibility function for tests that expect the old interface
def parse_legacy(userInput: str) -> tuple[bool, Callable[..., Any] | str, list[str]]:
    """
    Legacy parse function that returns the old format for backward compatibility.
    
    Returns:
        - (True, action_function, args) if parsing succeeded
        - (False, error_message, []) if parsing failed
    """
    from . import actions
    
    # Legacy command mapping
    legacy_commands = {
        "debug items": actions.debug_items,
        "call phone": actions.call_phone,
        "rolodex": actions.rolodex,
        "look at watch": actions.look_at_watch,
        "ponder": actions.ponder,
        "balance": actions.check_balance,
        "feel": actions.check_feel,
        "eat {a}": actions.eat_thing,
        "examine {a}": actions.examine_thing,
        "watch {a}": actions.watch_tv,
        "look in {a}": actions.examine_thing,
        "open {a}": actions.open_thing,
        "close {a}": actions.close_thing,
        "pick up {a} from {b}": actions.get_object,
        "get {a} from {b}": actions.get_object,
        "inventory": actions.inventory,
        "go in {a}": actions.enter_room,
        "go to {a}": actions.enter_room,
        "enter {a}": actions.enter_room,
        "enter the {a}": actions.enter_room,
        "nail wood to exit": actions.nail_self_in,
        "nail wood to door": actions.nail_self_in,
        "nail self in": actions.nail_self_in,
        "nail self in closet": actions.nail_self_in,
        "inspect room": actions.inspect_room,
        "view room": actions.inspect_room,
        "look around room": actions.inspect_room,
        "mail check": actions.mail_check,
        "take an ice bath": actions.take_ice_bath,
        "take ice bath": actions.take_ice_bath,
        "ice bath": actions.take_ice_bath
    }
    
    for command, action in legacy_commands.items():
        ok, args = expand(command, userInput)
        if ok:
            return (True, action, args)

    return (False, "Don't understand command.", [])
