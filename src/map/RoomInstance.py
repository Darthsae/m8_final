from .RoomType import RoomType
from .Interactable import Interactable
from ..entity import EntityInstance
from typing import Any

class RoomInstance:
    def __init__(self, room_type: RoomType):
        self.__room_type: RoomType = room_type
        self.tags: list[str] = self.__room_type.tags
        self.interactables: list[Interactable] = []
        self.entities: list[EntityInstance] = []
        self.position_x: int = 0
        self.position_y: int = 0

    def getType(self) -> RoomType:
        """Get the RoomType that this RoomInstance is.
        """
        return self.__room_type

    def battleLoad(self) -> None:
        """Called after the battle_manager has been loaded.
        """
        for entity in self.entities:
            entity.battleLoad()

    def getDescription(self) -> str:
        """Get the description of the room for display.
        """
        to_return: str = f"{self.__room_type.name}\n{self.__room_type.description}\n"
        if len(self.interactables) > 0:
            to_return += (
                " ".join(
                    [
                        interactable.getDescription()
                        for interactable in self.interactables
                    ]
                )
                + "\n"
            )
        if len(self.entities) > 0:
            to_return += (
                " ".join([entity.getDescription() for entity in self.entities]) + "\n"
            )
        return to_return

    def addEntity(self, entity) -> None:
        """Add an entity to the room.
        """
        self.entities.append(entity)

    def addInteractable(self, interactable) -> None:
        """Add an interactable to the room.
        """
        self.interactables.append(interactable)

    def removeInteractable(self, interactable) -> None:
        """Remove an interactable from the room.
        """
        self.interactables.remove(interactable)

    def update(self) -> None:
        """Update the room instance.
        """
        to_kill: list[EntityInstance] = [participant for participant in self.entities if participant.to_die]
        for dead in to_kill:
            if dead.hasData("in_battle"):
                dead.flee()
            dead.death(self)
            self.entities.remove(dead)
        for entity in self.entities:
            entity.update(self)

    @classmethod
    def fromDict(cls, data: dict[str, Any], game):
        """Create a room instance from a dictionary.
        """
        room_instance: RoomInstance = cls(game.map.room_types[data["type"]])
        if "interactables" in data:
            room_instance.interactables = [
                Interactable.fromDict(interactable)
                for interactable in data["interactables"]
            ]
        if "entities" in data:
            room_instance.entities = [
                EntityInstance.fromDict(entity, game)
                for entity in data["entities"]
            ]
        if "position_x" in data:
            room_instance.position_x = data["position_x"]
        if "position_y" in data:
            room_instance.position_y = data["position_y"]
        return room_instance

    def toDict(self):
        """Get the dictionary representing this room instance.
        """
        return {
            "type": self.__room_type.id,
            "interactables": [
                interactable.toDict() for interactable in self.interactables
            ],
            "entities": [entity.toDict() for entity in self.entities],
            "position_x": self.position_x,
            "position_y": self.position_y
        }
