from ..util import Restrictions, adjacentPositions, indexOfIndexable, positionToString, stringToPosition
from ..script_parsing import parse
from .RoomInstance import RoomInstance
from .RoomPool import RoomPool
from .SpawnPool import SpawnPool
from .RoomType import RoomType
from typing import Any, Optional, Self, cast, Callable
import random

class Map:
    def __init__(self):
        self.__rooms: dict[tuple[int, int], tuple[RoomInstance, str]] = {}
        self.room_pool_types: dict[str, tuple[RoomPool, int]] = {}
        self.spawn_pool_types: dict[str, SpawnPool]= {}
        self.room_types: dict[str, RoomType] = {}

    def addRoomPool(self, room_pool: RoomPool) -> None:
        """Add a room pool to the map's selections.
        """
        self.room_pool_types[room_pool.id] = (room_pool, 0)

    def setRoom(self, x: int, y: int, room_pool: str) -> None:
        """Public method to set a room_pool at a room."""
        self.__assignRoom((x, y), self.room_pool_types[room_pool][0].generate(self), room_pool)

    def getRoom(self, x: int, y: int) -> Optional[RoomInstance]:
        """Returns the room at the position or None if there isn't one.
        """
        if not (x, y) in self.__rooms:
            # Generate Room
            options: list[tuple[RoomPool, Any]] = [
                (room_pool, room_pool.getScore(self, (x, y)))
                for room_pool in map(indexOfIndexable(0), self.room_pool_types.values())
                if room_pool.getScore(self, (x, y)) > 0
            ]
            if len(options) == 0:
                print("There is a wall there.")
                return None
            room_pool = random.choice(options)[0]
            room = room_pool.generate(self)
            self.__assignRoom((x, y), room, room_pool.id)

        return self.__rooms[(x, y)][0]

    def __assignRoom(self, position: tuple[int, int], room: RoomInstance, room_pool: str) -> None:
        """Used to set a room at a position, for internal use only.
        """
        room.position_x = position[0]
        room.position_y = position[1]
        self.__rooms[position] = (room, room_pool)
        self.room_pool_types[room_pool] = (
            self.room_pool_types[room_pool][0],
            self.room_pool_types[room_pool][1] + 1
        )

    def roomChain(self, position: tuple[int, int], room_pool: str) -> int:
        """Gets all chained rooms of a room_pool type connected to a point.
        """
        count: int = 0
        searched: set[tuple[int, int]] = set()
        to_search: set[tuple[int, int]] = set(adjacentPositions(position))
        while len(to_search) > 0:
            search_position: tuple[int, int] = to_search.pop()
            searched.add(search_position)
            if search_position in self.__rooms and self.__rooms[search_position][1] == room_pool:
                count += 1
                to_search |= set(adjacentPositions(search_position)) - searched
        return count

    def roomPoolCount(self, room_pool: str) -> int:
        """Get the number of room_pools for a sepcific room_pool in the map.
        """
        return self.room_pool_types[room_pool][1]

    def getRooms(self) -> dict[tuple[int, int], tuple[RoomInstance, str]]:
        """Returns the rooms in the map.
        """
        return self.__rooms
    
    def battleLoad(self) -> None:
        """Called to make battles loaded properly. Do after loading the battle manager.
        """
        for room, _ in self.__rooms.values():
            room.battleLoad()

    def reset(self) -> None:
        """Reset all of the instance data.
        """
        self.__rooms = {}
        for key in self.room_pool_types:
            self.room_pool_types[key] = (self.room_pool_types[key][0], 0)

    def loadFromDict(self, data: dict[str, Any], game) -> None:
        """Load the map from a dictionary.
        """
        for key, value in cast(dict[str, tuple[dict[str, Any], str]], data["rooms"]).items():
            self.__assignRoom(stringToPosition(key), RoomInstance.fromDict(value[0], game), value[1])

    def toDict(self) -> dict[str, dict[str, tuple[dict[str, Any], str]]]:
        """Creates a dict from the state of the map.
        """
        return {
            "rooms": {positionToString(key): (value[0].toDict(), value[1]) for key, value in self.__rooms.items()},
        }
