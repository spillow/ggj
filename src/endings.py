"""
endings.py

Game ending logic and text constants for the four endings:
Victory, Partial Victory, Defeat, and Secret Ending.

Also handles the dream confrontation sequence that gates the secret ending.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core.game_world import GameState
    from .io_interface import IOInterface


# ------------------------------------------------------------------ #
#                         Ending text constants                       #
# ------------------------------------------------------------------ #

VICTORY_TEXT: str = (
    'The TV flickers to life with the morning news. "THE ANOMALY HAS CLOSED," '
    "the anchor announces, barely containing their relief. "
    '"Scientists confirm the rift in spacetime has sealed completely."'
    "\n\n"
    "You look toward the bedroom. The half-built device sits there -- "
    "an ugly tangle of wire and plywood, inert and harmless. Just junk."
    "\n\n"
    "Something shifts inside you. A pressure you've felt for years -- "
    "behind your eyes, at the base of your skull -- simply... stops. "
    "Like a hand releasing its grip. The apartment is quiet. Really quiet. "
    "For the first time in months, the silence feels peaceful rather than "
    "oppressive."
    "\n\n"
    "You look at the front door. Maybe tomorrow."
)

PARTIAL_VICTORY_TEXT: str = (
    'The TV crackles: "THE ANOMALY HAS CLOSED."'
    "\n\n"
    "But in the bedroom, the nearly-complete device doesn't agree. "
    "It shudders. The hum rises to a shriek. A blinding flash erupts "
    "from the crystalline array, and for a split second you see "
    "*through* the walls -- a landscape that is not your city, "
    "colors that don't belong to your spectrum."
    "\n\n"
    "Then silence. The device collapses in on itself, a smoking ruin. "
    "The bedroom wall is scorched black."
    "\n\n"
    "You're alive. You're shaking, but alive. The TV returns: "
    '"...worldwide celebrations as the event concludes..."'
    "\n\n"
    "But you can still feel it. Faint, like a whisper at the edge of "
    "hearing. A presence. Not gone. Just dormant. Again."
    "\n\n"
    "You look at the scorched wall and start planning."
)

DEFEAT_TEXT: str = (
    "You wake to a sound you've never heard before -- a deep, resonant "
    "hum that seems to come from everywhere and nowhere. The bedroom is "
    "filled with light. Not lamp light. Not sunlight. Something older. "
    "Something wrong."
    "\n\n"
    "The device is active. It pulses with energy that makes your teeth "
    "ache and your vision swim. Through the light, you see... the other "
    "side. A landscape of impossible geometry, layered over your bedroom "
    "like a double exposure. The walls are dissolving."
    "\n\n"
    "The rift widens."
    "\n\n"
    "From the other room, the TV blares: \"BREAKING: The anomaly is "
    "expanding rapidly. This is not a drill. All residents are advised "
    'to seek shelter immed--"'
    "\n\n"
    "Static."
    "\n\n"
    "GAME OVER"
)

DREAM_CONFRONTATION_TEXT: str = (
    "Darkness. But not sleep. You're aware. More aware than you've ever been."
    "\n\n"
    "A voice. Your voice, but not your voice."
    "\n\n"
    '"You think you\'ve won? I\'ve been here since you were a child. '
    "The fear. The walls. The locked door. The reasons you never leave. "
    'That was all me. You *needed* me."'
    "\n\n"
    "A pause."
    "\n\n"
    '"You still need me."'
)

SECRET_ENDING_TEXT: str = (
    '"No," you say. And you mean it.'
    "\n\n"
    "The voice fractures. Splinters. Like glass breaking in slow motion."
    "\n\n"
    '"You can\'t -- I\'m part of --"'
    "\n\n"
    '"No. You\'re not."'
    "\n\n"
    "Silence. Real silence. The kind you haven't heard since you were "
    "eight years old."
    "\n\n"
    "You wake up."
    "\n\n"
    "The apartment is still. The device sits in the bedroom, dead and "
    "harmless. The TV murmurs about the anomaly closing. But something "
    "is different. The door. The front door of your apartment. It doesn't "
    "look like a wall anymore. It looks like a door."
    "\n\n"
    "You walk to it. Put your hand on the knob. Turn it."
    "\n\n"
    "The sunlight is blinding after so many months indoors. The air "
    "smells like spring. Your legs carry you over the threshold without "
    "hesitation."
    "\n\n"
    "You take a step. Then another."
    "\n\n"
    "Your legs work fine. They always did."
)


# ------------------------------------------------------------------ #
#                         GameEndings class                           #
# ------------------------------------------------------------------ #

class GameEndings:
    """Static methods for checking and displaying game endings."""

    @staticmethod
    def check_ending(gamestate: GameState) -> str | None:
        """
        Check whether an ending condition has been reached.

        Returns:
            "defeat" if device activated,
            "victory" if Day 7+ with 2+ missing components,
            "partial_victory" if Day 7+ with exactly 1 missing,
            "defeat" if Day 7+ with 0 missing,
            None if no ending yet.
        """
        if gamestate.device_activated:
            return "defeat"

        day = gamestate.get_current_day()
        if day >= 7:
            missing = gamestate.device_state.count_missing_components()
            if missing >= 2:
                return "victory"
            if missing == 1:
                return "partial_victory"
            return "defeat"

        return None

    @staticmethod
    def check_secret_ending(gamestate: GameState) -> bool:
        """
        Check whether the secret ending conditions are all met.

        Requires:
            1. journal_read is True
            2. mirror_seen is True
            3. 2+ device components are missing (victory condition)
            4. Day 6 or later
        """
        return (
            gamestate.journal_read
            and gamestate.mirror_seen
            and gamestate.device_state.count_missing_components() >= 2
            and gamestate.get_current_day() >= 6
        )

    @staticmethod
    def display_victory(io: IOInterface) -> None:
        """Display the victory ending."""
        io.output("")
        io.output(VICTORY_TEXT)
        io.output("")

    @staticmethod
    def display_partial_victory(io: IOInterface) -> None:
        """Display the partial victory ending."""
        io.output("")
        io.output(PARTIAL_VICTORY_TEXT)
        io.output("")

    @staticmethod
    def display_defeat(io: IOInterface) -> None:
        """Display the defeat ending."""
        io.output("")
        io.output(DEFEAT_TEXT)
        io.output("")

    @staticmethod
    def display_dream_confrontation(io: IOInterface) -> None:
        """Display the dream confrontation sequence."""
        io.output("")
        io.output(DREAM_CONFRONTATION_TEXT)
        io.output("")

    @staticmethod
    def display_secret_ending(io: IOInterface) -> None:
        """Display the secret ending."""
        io.output("")
        io.output(SECRET_ENDING_TEXT)
        io.output("")
