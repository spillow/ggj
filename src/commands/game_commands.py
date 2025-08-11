"""
Game Commands module - Command Pattern implementation for all game actions.

Converts all action functions from the game_actions modules into Command objects,
enabling undo/redo, action replay, macros, and AI compatibility.
"""

from __future__ import annotations
from datetime import timedelta
from typing import TYPE_CHECKING, Optional

from .base_command import BaseCommand, CommandResult

if TYPE_CHECKING:
    from ..core.game_world import GameState
    from ..core.game_objects import Object
    from ..core.rooms import Room


# Movement Commands
class EnterRoomCommand(BaseCommand):
    """Command to move the hero to a different room."""
    
    def __init__(self, room_name: str):
        super().__init__(f"Enter room: {room_name}")
        self.room_name = room_name
        self.previous_room = None
    
    def can_execute(self, game_state: "GameState") -> bool:
        """Check if the room exists and is accessible."""
        from ..core.rooms import Room
        
        to_room = game_state.apartment.GetFirstItemByName(self.room_name)
        return to_room and isinstance(to_room, Room)
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Execute the room transition."""
        from ..core.rooms import Room
        from ..game_actions.action_decorators import attempt
        
        to_room = game_state.apartment.GetFirstItemByName(self.room_name)
        if not to_room or not isinstance(to_room, Room):
            return CommandResult(
                success=False, 
                message="I haven't built that wing yet."
            )
        
        from_room = game_state.hero.GetRoom()
        if to_room == from_room:
            # Store undo data even when already there (no-op undo)
            self.store_undo_data({"previous_room": from_room.name if from_room else None})
            self.mark_executed()
            return CommandResult(
                success=True,
                message="Already there."
            )
        
        # Store undo data
        self.store_undo_data({"previous_room": from_room.name if from_room else None})
        
        # Use existing attempt mechanism
        success = True
        try:
            to_room.Enter(from_room, game_state.hero)
        except Exception as e:
            success = False
            message = "I can't enter."
        
        if success:
            self.mark_executed()
            return CommandResult(success=True)
        else:
            return CommandResult(success=False, message="I can't enter.")
    
    def can_undo(self) -> bool:
        """Room transitions can be undone."""
        return True
    
    def undo(self, game_state: "GameState") -> CommandResult:
        """Return to the previous room."""
        undo_data = self.get_undo_data()
        if not undo_data or "previous_room" not in undo_data:
            return CommandResult(success=False, message="Cannot undo room transition")
        
        previous_room_name = undo_data["previous_room"]
        current_room = game_state.hero.GetRoom()
        
        # If we're already in the "previous" room (no-op case), undo is successful
        if current_room.name == previous_room_name:
            return CommandResult(success=True, message="Already in previous room")
        
        previous_room = game_state.apartment.GetFirstItemByName(previous_room_name)
        
        if previous_room:
            try:
                previous_room.Enter(current_room, game_state.hero)
                return CommandResult(success=True, message="Returned to previous room")
            except Exception:
                return CommandResult(success=False, message="Failed to return to previous room")
        
        return CommandResult(success=False, message="Previous room no longer exists")


class NailSelfInCommand(BaseCommand):
    """Command to nail yourself into the closet."""
    
    def __init__(self):
        super().__init__("Nail self into closet")
        self.items_consumed = []
        self.previous_closet_state = None
        self.previous_feel = None
        self.time_advanced = None
    
    def can_execute(self, game_state: "GameState") -> bool:
        """Check if hero is in closet with required items."""
        from ..core.rooms import Closet
        
        closet = game_state.apartment.closet
        if game_state.hero.GetRoom() != closet:
            return False
        
        if closet.state == Closet.State.NAILED:
            return False
        
        hero = game_state.hero
        hammer = hero.GetFirstItemByName('hammer')
        nails = hero.GetFirstItemByName('box-of-nails')
        plywood = hero.GetFirstItemByName('plywood-sheet')
        
        return bool(hammer and nails and plywood)
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Execute the nailing action."""
        from ..core.rooms import Closet
        
        closet = game_state.apartment.closet
        
        if game_state.hero.GetRoom() != closet:
            return CommandResult(
                success=False,
                message="Gotta be in the closet to start nailing!"
            )
        
        if closet.state == Closet.State.NAILED:
            return CommandResult(
                success=False,
                message="Wasn't once enough?"
            )
        
        hero = game_state.hero
        
        if not hero.contents:
            return CommandResult(
                success=False,
                message="You have no objects with which to do that"
            )
        
        hammer = hero.GetFirstItemByName('hammer')
        nails = hero.GetFirstItemByName('box-of-nails')
        plywood = hero.GetFirstItemByName('plywood-sheet')
        
        if not hammer or not nails or not plywood:
            missing_items = []
            if not plywood:
                missing_items.append("Perhaps some wood?")
            if not hammer:
                missing_items.append("Perhaps a hammer?")
            if not nails:
                missing_items.append("Perhaps some nails?")
            
            return CommandResult(
                success=False,
                message=f"You are missing something. {' '.join(missing_items)}"
            )
        
        # Store undo data
        self.store_undo_data({
            "items_consumed": [nails.name, plywood.name],
            "previous_closet_state": closet.state,
            "previous_feel": hero.feel,
            "previous_time": game_state.watch.curr_time
        })
        
        # Execute the action
        hero.Destroy([plywood, nails])
        closet.state = Closet.State.NAILED
        
        num_hours = 2
        game_state.watch.curr_time += timedelta(hours=num_hours)
        hero.feel -= 10 * num_hours
        
        self.mark_executed()
        return CommandResult(
            success=True,
            message="You have successfully nailed yourself into a rather small closet.",
            time_advanced=True
        )
    
    def can_undo(self) -> bool:
        """Nailing action cannot be easily undone."""
        return False


class InspectRoomCommand(BaseCommand):
    """Command to look around the current room."""
    
    def __init__(self):
        super().__init__("Inspect current room")
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """List all objects in the current room."""
        room = game_state.hero.GetRoom()
        hero = game_state.hero
        
        # Use the original output format by calling io.output directly
        hero.io.output("")
        hero.io.output("You look around the room.  You see:")
        hero.io.output("")

        if not room.contents:
            hero.io.output("Nothing!")
        else:
            for item in room.contents:
                hero.io.output(str(item))
        
        hero.io.output("")
        
        self.mark_executed()
        return CommandResult(success=True)  # Output handled directly


# Inventory Commands
class ExamineThingCommand(BaseCommand):
    """Command to examine an object."""
    
    def __init__(self, object_name: str):
        super().__init__(f"Examine {object_name}")
        self.object_name = object_name
    
    def can_execute(self, game_state: "GameState") -> bool:
        """Check if the object exists in the current room."""
        room_object = game_state.hero.GetRoom().GetFirstItemByName(self.object_name)
        return room_object is not None
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Execute the examine action."""
        from ..game_actions.action_decorators import attempt
        
        room_object = game_state.hero.GetRoom().GetFirstItemByName(self.object_name)
        if not room_object:
            return CommandResult(
                success=False,
                message="I don't see that in the room."
            )
        
        try:
            room_object.Examine(game_state.hero)
            self.mark_executed()
            return CommandResult(success=True)
        except Exception:
            return CommandResult(
                success=False,
                message="I can't examine that."
            )


class OpenThingCommand(BaseCommand):
    """Command to open a container."""
    
    def __init__(self, object_name: str):
        super().__init__(f"Open {object_name}")
        self.object_name = object_name
        self.previous_state = None
    
    def can_execute(self, game_state: "GameState") -> bool:
        """Check if the object exists and can be opened."""
        from ..core.game_objects import Openable
        
        room_object = game_state.hero.GetRoom().GetFirstItemByName(self.object_name)
        return room_object and isinstance(room_object, Openable)
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Execute the open action."""
        from ..core.game_objects import Openable
        
        room_object = game_state.hero.GetRoom().GetFirstItemByName(self.object_name)
        if not room_object:
            return CommandResult(
                success=False,
                message="I don't see that in the room."
            )
        
        if not isinstance(room_object, Openable):
            return CommandResult(
                success=False,
                message="I can't open that."
            )
        
        # Store undo data
        self.store_undo_data({"previous_state": room_object.state})
        
        try:
            room_object.Open(game_state.hero)
            self.mark_executed()
            return CommandResult(success=True)
        except Exception:
            return CommandResult(
                success=False,
                message="I can't open that."
            )
    
    def can_undo(self) -> bool:
        """Opening can be undone by closing."""
        return True
    
    def undo(self, game_state: "GameState") -> CommandResult:
        """Undo by closing the container."""
        from ..core.game_objects import Openable
        
        room_object = game_state.hero.GetRoom().GetFirstItemByName(self.object_name)
        if not room_object or not isinstance(room_object, Openable):
            return CommandResult(
                success=False,
                message="Cannot undo open action"
            )
        
        try:
            room_object.Close(game_state.hero)
            return CommandResult(success=True, message="Closed container")
        except Exception:
            return CommandResult(
                success=False,
                message="Failed to close container"
            )


class CloseThingCommand(BaseCommand):
    """Command to close a container."""
    
    def __init__(self, object_name: str):
        super().__init__(f"Close {object_name}")
        self.object_name = object_name
        self.previous_state = None
    
    def can_execute(self, game_state: "GameState") -> bool:
        """Check if the object exists and can be closed."""
        from ..core.game_objects import Openable
        
        room_object = game_state.hero.GetRoom().GetFirstItemByName(self.object_name)
        return room_object and isinstance(room_object, Openable)
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Execute the close action."""
        from ..core.game_objects import Openable
        
        room_object = game_state.hero.GetRoom().GetFirstItemByName(self.object_name)
        if not room_object:
            return CommandResult(
                success=False,
                message="I don't see that in the room."
            )
        
        if not isinstance(room_object, Openable):
            return CommandResult(
                success=False,
                message="I can't close that."
            )
        
        # Store undo data
        self.store_undo_data({"previous_state": room_object.state})
        
        try:
            room_object.Close(game_state.hero)
            self.mark_executed()
            return CommandResult(success=True)
        except Exception:
            return CommandResult(
                success=False,
                message="I can't close that."
            )
    
    def can_undo(self) -> bool:
        """Closing can be undone by opening."""
        return True
    
    def undo(self, game_state: "GameState") -> CommandResult:
        """Undo by opening the container."""
        from ..core.game_objects import Openable
        
        room_object = game_state.hero.GetRoom().GetFirstItemByName(self.object_name)
        if not room_object or not isinstance(room_object, Openable):
            return CommandResult(
                success=False,
                message="Cannot undo close action"
            )
        
        try:
            room_object.Open(game_state.hero)
            return CommandResult(success=True, message="Opened container")
        except Exception:
            return CommandResult(
                success=False,
                message="Failed to open container"
            )


class GetObjectCommand(BaseCommand):
    """Command to get an object from a container."""
    
    def __init__(self, obj_name: str, container_name: str):
        super().__init__(f"Get {obj_name} from {container_name}")
        self.obj_name = obj_name
        self.container_name = container_name
        self.retrieved_object = None
        self.original_container = None
    
    def can_execute(self, game_state: "GameState") -> bool:
        """Check if the container and object exist."""
        from ..core.game_objects import Container, Openable
        
        room_obj = game_state.hero.GetRoom().GetFirstItemByName(self.container_name)
        if not room_obj or not isinstance(room_obj, Container):
            return False
        
        if isinstance(room_obj, Openable) and room_obj.state != Openable.State.OPEN:
            return False
        
        thing = room_obj.GetFirstItemByName(self.obj_name)
        return thing is not None
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Execute the pickup action."""
        from ..core.game_objects import Container, Openable
        from ..game_actions.action_decorators import attempt
        
        room_obj = game_state.hero.GetRoom().GetFirstItemByName(self.container_name)
        if not room_obj:
            return CommandResult(
                success=False,
                message="I don't see that in the room."
            )
        
        if isinstance(room_obj, Openable):
            if room_obj.state != Openable.State.OPEN:
                return CommandResult(
                    success=False,
                    message="Try opening it first."
                )
            
            thing = room_obj.GetFirstItemByName(self.obj_name)
            if thing:
                # Store undo data
                self.store_undo_data({
                    "retrieved_object": thing,
                    "original_container": room_obj
                })
                
                try:
                    game_state.hero.Pickup(thing)
                    self.mark_executed()
                    return CommandResult(success=True)  # Hero.Pickup handles output directly
                except Exception as e:
                    return CommandResult(
                        success=False,
                        message=str(e) if str(e) else "Cannot pick up that item"
                    )
            else:
                return CommandResult(
                    success=False,
                    message=f"I don't see that in the {room_obj.name}."
                )
        
        elif isinstance(room_obj, Container):
            thing = room_obj.GetFirstItemByName(self.obj_name)
            if thing:
                # Store undo data
                self.store_undo_data({
                    "retrieved_object": thing,
                    "original_container": room_obj
                })
                
                try:
                    game_state.hero.Pickup(thing)
                    self.mark_executed()
                    return CommandResult(success=True)  # Hero.Pickup handles output directly
                except Exception as e:
                    return CommandResult(
                        success=False,
                        message=str(e) if str(e) else "Cannot pick up that item"
                    )
            else:
                return CommandResult(
                    success=False,
                    message=f"I don't see that in the {room_obj.name}."
                )
        
        return CommandResult(
            success=False,
            message="I can't get anything from that."
        )
    
    def can_undo(self) -> bool:
        """Pickup can be undone by returning the object."""
        return True
    
    def undo(self, game_state: "GameState") -> CommandResult:
        """Return the object to its original container."""
        undo_data = self.get_undo_data()
        if not undo_data:
            return CommandResult(
                success=False,
                message="Cannot undo pickup - no undo data"
            )
        
        retrieved_object = undo_data.get("retrieved_object")
        original_container = undo_data.get("original_container")
        
        if not retrieved_object or not original_container:
            return CommandResult(
                success=False,
                message="Cannot undo pickup - missing object or container"
            )
        
        # Check if hero still has the object
        if retrieved_object not in game_state.hero.contents:
            return CommandResult(
                success=False,
                message="Cannot undo pickup - object no longer in inventory"
            )
        
        try:
            # Remove from hero and return to container
            game_state.hero.contents.remove(retrieved_object)
            retrieved_object.parent = original_container
            original_container.contents.append(retrieved_object)
            
            return CommandResult(
                success=True,
                message=f"Returned {retrieved_object.name} to {original_container.name}"
            )
        except Exception:
            return CommandResult(
                success=False,
                message="Failed to return object to container"
            )


class InventoryCommand(BaseCommand):
    """Command to display current inventory."""
    
    def __init__(self):
        super().__init__("Show inventory")
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Display the hero's inventory."""
        hero = game_state.hero
        
        if not hero.contents:
            hero.io.output("\nYou have no objects in your inventory")
        else:
            hero.io.output("\nYou are carrying the following:")
            for obj in hero.contents:
                hero.io.output(f"     {obj}")
        
        hero.io.output("")
        self.mark_executed()
        return CommandResult(success=True)  # Output handled directly


# Utility Commands
class CheckBalanceCommand(BaseCommand):
    """Command to check current money balance."""
    
    def __init__(self):
        super().__init__("Check balance")
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Display the hero's current balance."""
        balance = game_state.hero.curr_balance
        self.mark_executed()
        return CommandResult(
            success=True,
            message=f"Current Balance: ${balance}"
        )


class CheckFeelCommand(BaseCommand):
    """Command to check current feel level."""
    
    def __init__(self):
        super().__init__("Check feel")
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Display the hero's current feel level."""
        feel = game_state.hero.feel
        self.mark_executed()
        
        if feel >= 40:
            message = "Feeling good"
        elif feel >= 20:
            message = "Feeling okay"
        else:
            message = "I'm about to hit the sheets!"
            
        return CommandResult(
            success=True,
            message=message
        )


class LookAtWatchCommand(BaseCommand):
    """Command to check the current time."""
    
    def __init__(self):
        super().__init__("Look at watch")
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Display the current game time."""
        time_str = game_state.watch.GetDateAsString()
        self.mark_executed()
        return CommandResult(
            success=True,
            message=f"The current time is {time_str}"
        )


class PonderCommand(BaseCommand):
    """Command to waste time pondering."""
    
    def __init__(self, hours: int = 1):
        super().__init__(f"Ponder for {hours} hours")
        self.hours = hours
        self.previous_time = None
        self.previous_feel = None
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Advance time and decrease feel."""
        # Store undo data
        self.store_undo_data({
            "previous_time": game_state.watch.curr_time,
            "previous_feel": game_state.hero.feel
        })
        
        # Advance time and affect stats
        game_state.watch.curr_time += timedelta(hours=self.hours)
        game_state.hero.feel -= 10 * self.hours
        
        self.mark_executed()
        return CommandResult(
            success=True,
            message=f"You ponder for {self.hours} hours.",
            time_advanced=True
        )
    
    def can_undo(self) -> bool:
        """Pondering can be undone by restoring time and feel."""
        return True
    
    def undo(self, game_state: "GameState") -> CommandResult:
        """Restore previous time and feel."""
        undo_data = self.get_undo_data()
        if not undo_data:
            return CommandResult(success=False, message="Cannot undo ponder")
        
        game_state.watch.curr_time = undo_data["previous_time"]
        game_state.hero.feel = undo_data["previous_feel"]
        
        return CommandResult(
            success=True,
            message="Undid pondering"
        )


class DebugItemsCommand(BaseCommand):
    """Debug command to give player hammer, nails, and plywood."""
    
    def __init__(self):
        super().__init__("Debug: Give hammer, nails, and plywood")
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Give debug items to the player."""
        from ..core.game_objects import Object
        
        # Create debug items
        hammer = Object("hammer", None)
        hammer.weight = 15
        nails = Object("box-of-nails", None)
        nails.weight = 10
        plywood = Object("plywood-sheet", None)
        plywood.weight = 25
        
        # Use pickup so we get the proper "Got it." messages
        try:
            # Place items in main room first
            hammer.parent = game_state.apartment.main
            nails.parent = game_state.apartment.main
            plywood.parent = game_state.apartment.main
            
            game_state.apartment.main.contents.extend([hammer, nails, plywood])
            
            # Now pick them up using the normal pickup method
            game_state.hero.Pickup(hammer)
            game_state.hero.Pickup(nails)
            game_state.hero.Pickup(plywood)
            
            self.mark_executed()
            return CommandResult(success=True)  # Hero.Pickup handles output
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Failed to add debug items: {str(e)}"
            )


# Interaction Commands
class CallPhoneCommand(BaseCommand):
    """Command to make a phone call."""
    
    def __init__(self):
        super().__init__("Make a phone call")
    
    def can_execute(self, game_state: "GameState") -> bool:
        """Check if hero is near the phone."""
        phone = game_state.apartment.main.phone
        return game_state.hero.GetRoom() == phone.GetRoom()
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Execute the phone call."""
        from ..game_actions.action_decorators import attempt
        
        phone = game_state.apartment.main.phone
        if game_state.hero.GetRoom() != phone.GetRoom():
            return CommandResult(
                success=False,
                message="I need to get close to the phone first."
            )
        
        try:
            phone.Interact(game_state.hero)
            self.mark_executed()
            return CommandResult(success=True)
        except Exception:
            return CommandResult(
                success=False,
                message="I can't call."
            )


class EatThingCommand(BaseCommand):
    """Command to eat food."""
    
    def __init__(self, food_name: str):
        super().__init__(f"Eat {food_name}")
        self.food_name = food_name
        self.previous_feel = None
    
    def can_execute(self, game_state: "GameState") -> bool:
        """Check if the food exists and can be eaten."""
        from ..core.items import Food
        
        # Check if food is in hero's inventory or in an open fridge
        food_item = game_state.hero.GetFirstItemByName(self.food_name)
        if not food_item:
            # Check fridge
            fridge = game_state.apartment.main.fridge
            if hasattr(fridge, 'state') and fridge.state == fridge.State.OPEN:
                food_item = fridge.GetFirstItemByName(self.food_name)
        
        return food_item and isinstance(food_item, Food)
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Execute the eating action."""
        from ..core.items import Food
        from ..game_actions.action_decorators import attempt
        
        fridge = game_state.apartment.main.fridge
        if game_state.hero.GetRoom() != fridge.GetRoom():
            return CommandResult(
                success=False,
                message="Step a little closer to the fridge."
            )

        if fridge.isClosed():
            return CommandResult(
                success=False,
                message="Right, I have to open the fridge first."
            )

        food_item = fridge.GetFirstItemByName(self.food_name)
        if isinstance(food_item, Food):
            # Store undo data
            self.store_undo_data({"previous_feel": game_state.hero.feel})
            
            try:
                food_item.Eat(game_state.hero)
                self.mark_executed()
                return CommandResult(success=True)
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=str(e) if str(e) else "I can't eat that."
                )
        else:
            return CommandResult(
                success=False,
                message="I don't see that food in there."
            )
    
    def can_undo(self) -> bool:
        """Eating cannot be undone."""
        return False


class WatchTvCommand(BaseCommand):
    """Command to watch TV."""
    
    def __init__(self):
        super().__init__("Watch TV")
    
    def can_execute(self, game_state: "GameState") -> bool:
        """Check if TV is accessible."""
        tv = game_state.apartment.main.tv
        return game_state.hero.GetRoom() == tv.GetRoom()
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Execute watching TV."""
        tv = game_state.apartment.main.tv
        if game_state.hero.GetRoom() != tv.GetRoom():
            return CommandResult(
                success=False,
                message="I need to be in the same room as the TV."
            )
        
        try:
            tv.Examine(game_state.hero)
            self.mark_executed()
            return CommandResult(success=True)
        except Exception:
            return CommandResult(
                success=False,
                message="I can't watch the TV."
            )


class MailCheckCommand(BaseCommand):
    """Command to mail a government check."""
    
    def __init__(self):
        super().__init__("Mail government check")
        self.check = None
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Execute mailing a check for money."""
        from datetime import timedelta
        
        check = game_state.hero.GetFirstItemByName("check")
        if check:
            # Store undo data
            self.check = check
            self.store_undo_data({"check": check})
            
            tomorrow = game_state.watch.curr_time + timedelta(days=1)

            def mail(_curr_time, _event_time) -> None:
                game_state.hero.io.output("new bank deposit!")
                game_state.hero.curr_balance += 100
                
            if game_state.event_queue is not None:
                game_state.event_queue.AddEvent(mail, tomorrow)
            
            game_state.hero.Destroy([check])
            
            self.mark_executed()
            return CommandResult(
                success=True,
                message="Check is out.  Big money tomorrow!"
            )
        else:
            return CommandResult(
                success=False,
                message="You're not holding a check.  How's the cabinet looking?"
            )
    
    def can_undo(self) -> bool:
        """Mailing check can be undone by removing the money."""
        return True
    
    def undo(self, game_state: "GameState") -> CommandResult:
        """Undo by restoring previous balance."""
        undo_data = self.get_undo_data()
        if not undo_data:
            return CommandResult(success=False, message="Cannot undo mail check")
        
        game_state.hero.curr_balance = undo_data["previous_balance"]
        return CommandResult(success=True, message="Undid check mailing")


class RolodexCommand(BaseCommand):
    """Command to show available phone numbers."""
    
    def __init__(self):
        super().__init__("Show phone numbers")
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Display available phone numbers."""
        phone = game_state.apartment.main.phone
        hero = game_state.hero
        
        if hero.GetRoom() != phone.GetRoom():
            return CommandResult(
                success=False,
                message="I need to get close to the phone first."
            )
        
        try:
            phone.Rolodex(hero)
            self.mark_executed()
            return CommandResult(success=True)  # Phone.Rolodex handles output directly
        except Exception:
            return CommandResult(
                success=False,
                message="No numbers."
            )


# Command factory functions for easy creation
def create_enter_room_command(room_name: str) -> BaseCommand:
    """Create an EnterRoomCommand."""
    return EnterRoomCommand(room_name)


def create_examine_command(object_name: str) -> BaseCommand:
    """Create an ExamineThingCommand."""
    return ExamineThingCommand(object_name)


def create_get_object_command(obj_name: str, container_name: str) -> BaseCommand:
    """Create a GetObjectCommand."""
    return GetObjectCommand(obj_name, container_name)


def create_call_phone_command() -> BaseCommand:
    """Create a CallPhoneCommand."""
    return CallPhoneCommand()


def create_eat_command(food_name: str) -> BaseCommand:
    """Create an EatThingCommand."""
    return EatThingCommand(food_name)


class TakeIceBathCommand(BaseCommand):
    """Command to take an ice bath in the bathroom using ice cubes."""
    
    def __init__(self):
        super().__init__("Take ice bath")
        self.previous_feel = None
        self.previous_time = None
        self.ice_cubes = None
    
    def can_execute(self, game_state: "GameState") -> bool:
        """Check if hero is in bathroom with ice cubes."""
        # Check if hero is in bathroom
        if game_state.hero.GetRoom() != game_state.apartment.bathroom:
            return False
        
        # Check if hero has ice cubes
        ice_cubes = game_state.hero.GetFirstItemByName("ice-cubes")
        return ice_cubes is not None
    
    def execute(self, game_state: "GameState") -> CommandResult:
        """Execute the ice bath action."""
        # Check if hero is in bathroom
        if game_state.hero.GetRoom() != game_state.apartment.bathroom:
            return CommandResult(
                success=False,
                message="I need to be in the bathroom to take an ice bath."
            )
        
        # Check if hero has ice cubes
        ice_cubes = game_state.hero.GetFirstItemByName("ice-cubes")
        if not ice_cubes:
            return CommandResult(
                success=False,
                message="I need ice cubes to take an ice bath."
            )
        
        # Store undo data
        self.store_undo_data({
            "previous_feel": game_state.hero.feel,
            "previous_time": game_state.watch.curr_time,
            "ice_cubes": ice_cubes
        })
        
        # Consume the ice cubes
        game_state.hero.Destroy([ice_cubes])
        
        # Boost feel by 40
        game_state.hero.feel += 40
        
        # Advance time by 1 hour
        game_state.watch.curr_time += timedelta(hours=1)
        
        self.mark_executed()
        return CommandResult(
            success=True,
            message="You fill the tub with cold water and add the ice cubes.\nThe shock of the cold water makes you incredibly alert!\nTime passes as you endure the ice bath...",
            time_advanced=True
        )
    
    def can_undo(self) -> bool:
        """Ice bath can be undone by restoring previous state."""
        return True
    
    def undo(self, game_state: "GameState") -> CommandResult:
        """Restore previous feel, time, and ice cubes."""
        undo_data = self.get_undo_data()
        if not undo_data:
            return CommandResult(success=False, message="Cannot undo ice bath")
        
        # Restore previous state
        game_state.hero.feel = undo_data["previous_feel"]
        game_state.watch.curr_time = undo_data["previous_time"]
        
        # Restore ice cubes to hero's inventory
        ice_cubes = undo_data["ice_cubes"]
        if ice_cubes:
            ice_cubes.parent = game_state.hero
            game_state.hero.contents.append(ice_cubes)
        
        return CommandResult(
            success=True,
            message="Undid ice bath - restored time, feel, and ice cubes"
        )


def create_ice_bath_command() -> BaseCommand:
    """Create a TakeIceBathCommand."""
    return TakeIceBathCommand()