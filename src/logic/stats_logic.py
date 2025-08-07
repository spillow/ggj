"""
stats_logic.py

Pure business logic for feel/balance calculations and character state effects.
Contains character stat management rules and calculations.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.characters import Hero


class StatsRules:
    """
    Business rules for character stats and state management.
    """

    # Feel system constants
    INITIAL_FEEL = 50
    MINIMUM_FEEL = 0
    MAXIMUM_FEEL = 100

    # Balance system constants
    INITIAL_BALANCE = 100
    MINIMUM_BALANCE = 0

    # Feel changes for various actions
    GROCERY_ORDER_FEEL_COST = 2
    HARDWARE_ORDER_FEEL_COST = 10
    SUPER_CALL_FEEL_COST = 30

    @staticmethod
    def is_hero_conscious(hero: 'Hero') -> bool:
        """
        Check if hero is conscious (feel > 0).
        """
        return hero.feel > 0

    @staticmethod
    def is_hero_unconscious(hero: 'Hero') -> bool:
        """
        Check if hero is unconscious (feel <= 0).
        """
        return hero.feel <= 0

    @staticmethod
    def apply_feel_change(hero: 'Hero', feel_change: int) -> int:
        """
        Apply a feel change to the hero and return the new feel value.
        Ensures feel stays within valid bounds.
        """
        hero.feel += feel_change
        hero.feel = max(StatsRules.MINIMUM_FEEL, 
                       min(StatsRules.MAXIMUM_FEEL, hero.feel))
        return hero.feel

    @staticmethod
    def apply_balance_change(hero: 'Hero', balance_change: int) -> int:
        """
        Apply a balance change to the hero and return the new balance.
        Ensures balance doesn't go below minimum.
        """
        hero.curr_balance += balance_change
        hero.curr_balance = max(StatsRules.MINIMUM_BALANCE, hero.curr_balance)
        return hero.curr_balance

    @staticmethod
    def can_afford_item(hero: 'Hero', cost: int) -> bool:
        """
        Check if hero has enough money to afford an item.
        """
        return hero.curr_balance >= cost

    @staticmethod
    def purchase_item(hero: 'Hero', cost: int) -> tuple[bool, str]:
        """
        Attempt to purchase an item. Returns (success, message).
        """
        if not StatsRules.can_afford_item(hero, cost):
            return False, "Insufficient funds."
        
        hero.curr_balance -= cost
        return True, "Purchase successful."

    @staticmethod
    def reset_hero_feel(hero: 'Hero') -> None:
        """
        Reset hero's feel to initial value (after passing out).
        """
        hero.feel = StatsRules.INITIAL_FEEL

    @staticmethod
    def get_feel_status_description(hero: 'Hero') -> str:
        """
        Get a description of the hero's current feel status.
        """
        if hero.feel <= 10:
            return "exhausted"
        elif hero.feel <= 25:
            return "tired"
        elif hero.feel <= 40:
            return "weary"
        elif hero.feel <= 60:
            return "okay"
        elif hero.feel <= 80:
            return "good"
        else:
            return "great"

    @staticmethod
    def get_balance_status_description(hero: 'Hero') -> str:
        """
        Get a description of the hero's current financial status.
        """
        if hero.curr_balance <= 10:
            return "nearly broke"
        elif hero.curr_balance <= 50:
            return "low on funds"
        elif hero.curr_balance <= 100:
            return "modest savings"
        elif hero.curr_balance <= 200:
            return "comfortable"
        else:
            return "well-off"

    @staticmethod
    def calculate_food_boost(food_name: str) -> int:
        """
        Calculate the feel boost for a given food item.
        """
        food_boosts = {
            "spicy-food": 30,
            "caffeine": 20,
            "bananas": 5,
            "ice-cubes": 2
        }
        return food_boosts.get(food_name, 0)