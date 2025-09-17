from typing import Callable, Any, Self, cast
from ..util import Restrictions, adjacentPositions
from ..script_parsing import parse
from .RoomInstance import RoomInstance
import random

class RoomPool:
    def __init__(self, id: str, name: str, rooms, tags: list[str], restrictions: Restrictions):
        self.id: str = id
        self.name: str = name
        self.rooms = rooms
        self.tags: list[str] = tags
        self.conditions: list[Callable[[list[Any]], bool]] = []
        self.restrictions: Restrictions = restrictions

    def getScore(self, map, position) -> int:
        """Get the score for this 
        """
        for condition in self.conditions:
            if not condition([map, position]):
                return 0
        tags: list[str] = []
        for position in adjacentPositions(position):
            if position in map.getRooms():
                tags.extend(cast(RoomInstance, map.getRoom(position[0], position[1])).tags)
        return self.restrictions.score(tags)

    def generate(self, map) -> RoomInstance:
        """Generate a roompool and return the selected room with properly applied spawn pools.
        """
        room: RoomInstance = RoomInstance(map.room_types[random.choice(self.rooms)])
        room.tags.extend(self.tags)

        # This is where spawn pools will be applied.
        options = [
            (spawn_pool, spawn_pool.getScore(room))
            for spawn_pool in map.spawn_pool_types.values()
            if spawn_pool.getScore(room) > 0
        ]
        option = random.choice(options)[0]
        option.applyTo(room)

        return room

    @classmethod
    def fromDict(cls, game, id: str, data: dict[str, Any]) -> Self:
        """Load a room pool from a dict.
        """
        room_pool: RoomPool = cls(
            id,
            data["name"],
            data["rooms"],
            data["tags"],
            Restrictions.fromDict(data["restrictions"]),
        )
        room_pool.conditions = [
            parse(condition, game) for condition in data["conditions"]
        ]
        return room_pool