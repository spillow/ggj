"""
time_system.py

Time management utilities and the Watch class for tracking game time.
Contains time-related functionality and game timing mechanics.
"""

from datetime import datetime


class TimeUtils:
    """
    Utility functions for time management in the game.
    """

    @staticmethod
    def get_initial_time() -> datetime:
        """
        Return the initial game time: March 15, 1982 at 3:14 AM.
        """
        return datetime(1982, 3, 15, 3, 14)

    @staticmethod
    def format_time(time: datetime) -> str:
        """
        Format a datetime object as a readable game time string.
        """
        return time.strftime("%A %B %d, %Y at %I:%M %p")

    @staticmethod
    def is_daytime(time: datetime) -> bool:
        """
        Check if the given time is during daytime hours (6 AM - 6 PM).
        """
        return 6 <= time.hour < 18

    @staticmethod
    def is_nighttime(time: datetime) -> bool:
        """
        Check if the given time is during nighttime hours.
        """
        return not TimeUtils.is_daytime(time)


# Re-export Watch from items for convenience
from .items import Watch

__all__ = ['TimeUtils', 'Watch']