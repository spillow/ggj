"""Actions module for the text-based adventure game.

Legacy actions module - now re-exports all action functions from the new modular structure.
This file maintains backward compatibility while using the new architecture.
"""

# Re-export all action functions from the new modular structure
from .game_actions.movement_actions import enter_room, nail_self_in, inspect_room
from .game_actions.inventory_actions import (
    examine_thing, open_thing, close_thing, get_object, inventory
)
from .game_actions.interaction_actions import (
    call_phone, rolodex, eat_thing, watch_tv, mail_check, take_ice_bath
)
from .game_actions.utility_actions import (
    debug_items, look_at_watch, ponder, check_balance, check_feel
)
from .game_actions.action_decorators import attempt, thingify

# Make sure all the original functions are available
__all__ = [
    # Movement actions
    'enter_room', 'nail_self_in', 'inspect_room',
    # Inventory actions
    'examine_thing', 'open_thing', 'close_thing', 'get_object', 'inventory',
    # Interaction actions
    'call_phone', 'rolodex', 'eat_thing', 'watch_tv', 'mail_check', 'take_ice_bath',
    # Utility actions
    'debug_items', 'look_at_watch', 'ponder', 'check_balance', 'check_feel',
    # Decorators
    'attempt', 'thingify'
]