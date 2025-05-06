from .util import Restrictions, adjacentPositions
from .script_parsing import parse
import random

class Interactable:
    def __init__(self, name, description, tags, data):
        self.name = name
        self.description = description
        self.tags = tags
        self.uses = []
        self.data = data

    @classmethod
    def fromDict(cls, data):
        interactable = cls(data["name"], data["descriptions"], data["tags"], data["data"])
        return interactable
    
    def toDict(self):
        return {}

class RoomType:
    def __init__(self, id, name, description, tags):
        self.id = id
        self.name = name
        self.description = description
        self.tags = tags
        
    @classmethod
    def fromDict(cls, id, data):
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
        for condition in self.conditions:
            if not condition([map, position]):
                return 0
        tags = []
        for position in adjacentPositions(position):
            if position in map.getRooms():
                tags.extend(map.getRoom(position[0], position[1]).getType().tags)
        return self.restrictions.score(tags)


    def generate(self, map):
        room = map.room_types[random.choice(self.rooms)]

        # This is where spawn pools will be applied.
        for spawn_pool in map.spawn_pool_types:
            ...

        return room

    @classmethod
    def fromDict(cls, id, data):
        room_pool = cls(id, data["name"], data["rooms"], data["tags"], Restrictions.fromDict(data["restrictions"]))
        room_pool.conditions = [parse(condition) for condition in data["conditions"]]
        return room_pool

class SpawnPool:
    def __init__(self, id, name, restrictions):
        self.id = id
        self.name = name
        self.effects = []
        self.conditions = []
        self.restrictions = restrictions
    
    @classmethod
    def fromDict(cls, id, data):
        spawn_pool = cls(id, data["name"], Restrictions.fromDict(data["restrictions"]))
        spawn_pool.effects = [parse(effect) for effect in data["effects"]]
        spawn_pool.conditions = [parse(condition) for condition in data["conditions"]]
        return spawn_pool

class RoomInstance:
    def __init__(self, room_type):
        self.__room_type = room_type
        self.interactables = []
        self.entities = []
    
    def getType(self):
        return self.__room_type

    @classmethod
    def fromDict(cls, data, room_types):
        room_instance = cls(room_types[data["type"]])
        if "interactable" in data:
            room_instance = [Interactable.fromDict(interactable) for interactable in data["interactable"]]
        return room_instance
    
    def toDict(self):
        return {
            "type": self.__room_type.id,
            "interactables": [interactable.toDict() for interactable in self.interactables],
            "entities": [entity.toDict() for entity in self.entities]
        }
    
class Map:
    def __init__(self):
        self.__rooms = {}
        self.room_pool_types = {}
        self.spawn_pool_types = {}
        self.room_types = {}
    
    def addRoomPool(self, room_pool):
        self.room_pool_types[room_pool.id] = (room_pool, 0)
    
    def setRoom(self, x, y, room_pool):
        self.__assignRoom((x, y), room_pool.generate(self, (x, y)), room_pool.id)

    def getRoom(self, x, y):
        if not (x, y) in self.__rooms:
            # Generate Room
            room_pool = ...
            room = room_pool.generate(self, (x, y))
            self.__assignRoom((x, y), room, room_pool.id)
        
        return self.__rooms[(x, y)][0]
    
    def __assignRoom(self, position, room, room_pool):
        self.__rooms[position] = (room, room_pool)
        self.room_pool_types[room_pool] = (self.room_pool_types[room_pool][0], self.room_pool_types[room_pool][1] + 1)

    def roomChain(self, position, room_pool):
        count = 0
        searched = set()
        to_search = set(adjacentPositions(position))
        while len(to_search) > 0:
            search_position = to_search.pop()
            searched.add(search_position)
            possible_positions = set(adjacentPositions(search_position)) - searched
            for possible_position in possible_positions:
                searched.add(possible_position)
                if possible_position in self.__rooms and self.__rooms[possible_position][1] == room_pool:
                    count += 1
                    to_search.add(adjacentPositions(possible_position - searched))
        return count

    def roomPoolCount(self, room_pool):
        return self.room_pool_types[room_pool][1]

    def getRooms(self):
        return self.__rooms
    
    def reset(self):
        self.__rooms = {}
        for key in self.room_pool_types:
            self.room_pool_types[key] = (self.room_pool_types[key][0], 0)

    @classmethod
    def fromDict(cls, data):
        map = cls()

        return map
    
    def toDict(self):
        return {}