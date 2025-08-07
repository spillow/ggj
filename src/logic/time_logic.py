"""
time_logic.py

Pure business logic for time advancement and scheduling mechanics.
Contains time calculations and time-based rule validation.
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.items import Watch


class TimeRules:
    """
    Business rules for time management and advancement.
    """

    # Time advancement amounts for different actions
    EATING_TIME = timedelta(minutes=20)
    PHONE_CALL_TIME = timedelta(minutes=20)
    SUPER_CALL_TIME = timedelta(minutes=20)
    GROCERY_ORDER_TIME = timedelta(minutes=30)
    HARDWARE_ORDER_TIME = timedelta(minutes=2)

    @staticmethod
    def advance_time(watch: 'Watch', time_delta: timedelta) -> None:
        """
        Advance the game time by the specified amount.
        """
        watch.curr_time += time_delta

    @staticmethod
    def advance_time_by_minutes(watch: 'Watch', minutes: int) -> None:
        """
        Advance the game time by the specified number of minutes.
        """
        TimeRules.advance_time(watch, timedelta(minutes=minutes))

    @staticmethod
    def advance_time_by_hours(watch: 'Watch', hours: int) -> None:
        """
        Advance the game time by the specified number of hours.
        """
        TimeRules.advance_time(watch, timedelta(hours=hours))

    @staticmethod
    def is_business_hours(current_time: datetime) -> bool:
        """
        Check if the current time is during business hours (9 AM - 5 PM).
        """
        return 9 <= current_time.hour < 17

    @staticmethod
    def is_daytime(current_time: datetime) -> bool:
        """
        Check if the current time is during daytime (6 AM - 6 PM).
        """
        return 6 <= current_time.hour < 18

    @staticmethod
    def is_nighttime(current_time: datetime) -> bool:
        """
        Check if the current time is during nighttime.
        """
        return not TimeRules.is_daytime(current_time)

    @staticmethod
    def get_next_day(current_time: datetime) -> datetime:
        """
        Get the datetime for the next day at the same time.
        """
        return current_time + timedelta(days=1)

    @staticmethod
    def get_time_in_days(current_time: datetime, days: int) -> datetime:
        """
        Get the datetime for a specified number of days in the future.
        """
        return current_time + timedelta(days=days)

    @staticmethod
    def format_time_duration(start_time: datetime, end_time: datetime) -> str:
        """
        Format the duration between two times as a readable string.
        """
        duration = end_time - start_time
        hours = duration.total_seconds() // 3600
        minutes = (duration.total_seconds() % 3600) // 60
        
        if hours > 0:
            return f"{int(hours)}h {int(minutes)}m"
        else:
            return f"{int(minutes)}m"

    @staticmethod
    def is_time_for_government_check(current_time: datetime, last_check: datetime | None) -> bool:
        """
        Check if it's time for the next government check (every 2 weeks).
        """
        if last_check is None:
            return True
        
        two_weeks = timedelta(days=14)
        return current_time >= last_check + two_weeks