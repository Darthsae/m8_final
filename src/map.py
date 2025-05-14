from .util import Restrictions, adjacentPositions, indexOfIndexable
from .script_parsing import parse
import random


class Interactable:
    def __init__(self, name, description, tags, uses, data):
        self.name = name
        self.description = description
        self.tags = tags
        self.uses = uses
        self.data = data

    def hasData(self, key):
        """Checks if the key is in the interactables data.
        """
        return key in self.data

    def getData(self, key):
        """Returns the value of the key in the interactables data.
        """
        return self.data[key]

    def addData(self, key, value, _ = None):
        """Add data with a key of value to the interactable.
        """
        self.data[key] = value

    def removeData(self, key):
        """Remove data from the interactable.
        """
        self.data.pop(key)

    def getDescription(self):
        """Return the display description of the interactable.
        """
        return " ".join(["There is a", self.name, "in the room."])

    @classmethod
    def fromDict(cls, data):
        """Create an interactable from a dictionary.
        """
        interactable = cls(
            data["name"], data["description"], data["tags"], data["uses"], data["data"]
        )
        return interactable

    def toDict(self):
        """Convert the interactable to a dictionary.
        """
        return {
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "uses": self.uses,
            "data": self.data
        }


class RoomType:
    def __init__(self, id, name, description, tags):
        self.id = id
        self.name = name
        self.description = description
        self.tags = tags

    @classmethod
    def fromDict(cls, id, data):
        """
        """
        room_type = cls(id, data["name"], data["description"], data["tags"])

        return room_type


class RoomPool:
    def __init__(self, id, name, rooms, tags, restrictions):
        self.id = id
        self.name = name
        self.rooms = rooms
        self.tags = tags
        self.conditions = []
        self.restrictions = restrictions

    def getScore(self, map, position):
        """Get the score for this 
        """
        for condition in self.conditions:
            if not condition([map, position]):
                return 0
        tags = []
        for position in adjacentPositions(position):
            if position in map.getRooms():
                tags.extend(map.getRoom(position[0], position[1]).tags)
        return self.restrictions.score(tags)

    def generate(self, map):
        """Generate a roompool and return the selected room with properly applied spawn pools.
        """
        room = RoomInstance(map.room_types[random.choice(self.rooms)])
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
    def fromDict(cls, game, id, data):
        """Load a room pool from a dict.
        """
        room_pool = cls(
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


class SpawnPool:
    def __init__(self, id, name, restrictions):
        self.id = id
        self.name = name
        self.effects = []
        self.conditions = []
        self.restrictions = restrictions

    def getScore(self, room):
        """Get the validation score for this spawnpool.
        """
        for condition in self.conditions:
            if not condition([room]):
                return 0
        return self.restrictions.score(room.tags)

    def applyTo(self, room):
        """Apply the spawnpool to a room.
        """
        for effect in self.effects:
            effect([room])

    @classmethod
    def fromDict(cls, game, id, data):
        """Load a SpawnPool from a dictionary.
        """
        spawn_pool = cls(id, data["name"], Restrictions.fromDict(data["restrictions"]))
        spawn_pool.effects = [parse(effect, game) for effect in data["effects"]]
        spawn_pool.conditions = [
            parse(condition, game) for condition in data["conditions"]
        ]
        return spawn_pool


class RoomInstance:
    def __init__(self, room_type):
        self.__room_type = room_type
        self.tags = self.__room_type.tags
        self.interactables = []
        self.entities = []
        self.position_x = 0
        self.position_y = 0

    def getType(self):
        """Get the RoomType that this RoomInstance is.
        """
        return self.__room_type

    def battleLoad(self):
        """Called after the battle_manager has been loaded.
        """
        for entity in self.entities:
            entity.battleLoad()

    def getDescription(self):
        """Get the description of the room for display.
        """
        to_return = f"{self.__room_type.name}\n{self.__room_type.description}\n"
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

    def addEntity(self, entity):
        """Add an entity to the room.
        """
        self.entities.append(entity)

    def addInteractable(self, interactable):
        """Add an interactable to the room.
        """
        self.interactables.append(interactable)

    def removeInteractable(self, interactable):
        """Remove an interactable from the room.
        """
        self.interactables.remove(interactable)

    def update(self):
        """Update the room instance.
        """
        to_kill = [participant for participant in self.entities if participant.to_die]
        for dead in to_kill:
            if dead.hasData("in_battle"):
                dead.flee()
            dead.death(self)
            self.entities.remove(dead)
        for entity in self.entities:
            entity.update(self)

    @classmethod
    def fromDict(cls, data, game):
        """Create a room instance from a dictionary.
        """
        from .entity import EntityInstance
        room_instance = cls(game.map.room_types[data["type"]])
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

class Map:
    def __init__(self):
        self.__rooms = {}
        self.room_pool_types = {}
        self.spawn_pool_types = {}
        self.room_types = {}

    def addRoomPool(self, room_pool):
        """Add a room pool to the map's selections.
        """
        self.room_pool_types[room_pool.id] = (room_pool, 0)

    def setRoom(self, x, y, room_pool):
        """Public method to set a room_pool at a room."""
        self.__assignRoom(
            (x, y), self.room_pool_types[room_pool][0].generate(self), room_pool
        )

    def getRoom(self, x, y):
        """Returns the room at the position or None if there isn't one.
        """
        if not (x, y) in self.__rooms:
            # Generate Room
            options = [
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

    def __assignRoom(self, position, room, room_pool):
        """Used to set a room at a position, for internal use only.
        """
        room.position_x = position[0]
        room.position_y = position[1]
        self.__rooms[position] = (room, room_pool)
        self.room_pool_types[room_pool] = (
            self.room_pool_types[room_pool][0],
            self.room_pool_types[room_pool][1] + 1,
        )

    def roomChain(self, position, room_pool):
        """Gets all chained rooms of a room_pool type connected to a point.
        """
        count = 0
        searched = set()
        to_search = set(adjacentPositions(position))
        while len(to_search) > 0:
            search_position = to_search.pop()
            searched.add(search_position)
            if (
                search_position in self.__rooms
                and self.__rooms[search_position][1] == room_pool
            ):
                count += 1
                to_search |= set(adjacentPositions(search_position)) - searched
        return count

    def roomPoolCount(self, room_pool):
        """Get the number of room_pools for a sepcific room_pool in the map.
        """
        return self.room_pool_types[room_pool][1]

    def getRooms(self):
        """Returns the rooms in the map.
        """
        return self.__rooms
    
    def battleLoad(self):
        """Called to make battles loaded properly. Do after loading the battle manager.
        """
        for room, _ in self.__rooms.values():
            room.battleLoad()

    def reset(self):
        """Reset all of the instance data.
        """
        self.__rooms = {}
        for key in self.room_pool_types:
            self.room_pool_types[key] = (self.room_pool_types[key][0], 0)

    def loadFromDict(self, data, game):
        """Load the map from a dictionary.
        """
        for key, value in data["rooms"].items():
            self.__assignRoom(stringToPosition(key), RoomInstance.fromDict(value[0], game), value[1])

    def toDict(self):
        """Creates a dict from the state of the map.
        """
        return {
            "rooms": {positionToString(key): [value[0].toDict(), value[1]] for key, value in self.__rooms.items()},
        }

def positionToString(position):
    """Converts a position to a string.
    """
    return f"{position[0]},{position[1]}"

def stringToPosition(string):
    """Converts a string to a position.
    """
    data = string.split(",")
    return (int(data[0]), int(data[1]))