class Interactable:
    def __init__(self):
        ...

    @classmethod
    def fromDict(cls, data):
        interactable = cls()
        return interactable
    
    def toDict(self):
        return {}

class RoomType:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
    @classmethod
    def fromDict(cls, data):
        room_type = cls(data["name"], data["description"])

        return room_type
        
class RoomInstance:
    def __init__(self, room_type):
        self.__room_type = room_type
        self.interactables = []
        self.entities = []
    
    def getType(self):
        return self.__room_type

    @classmethod
    def fromDict(cls, data):
        room_instance = cls(data["type"])
        if "interactable" in data:
            room_instance = [Interactable.fromDict(interactable) for interactable in data["interactable"]]
        return room_instance
    
    def toDict(self):
        return {
            "type": self.__room_type,
            "interactables": [interactable.toDict() for interactable in self.interactables],
            "entities": [entity.toDict() for entity in self.entities]
        }
    
class Map:
    def __init__(self):
        self.__rooms = {}
    
    def getRoom(self, x, y):
        if not (x, y) in self.__rooms:
            # Generate Room
            room = ...
            self.__rooms[(x, y)] = room
        
        return self.__rooms[(x, y)]
    
    @classmethod
    def fromDict(cls, data):
        map = cls()

        return map
    
    def toDict(self):
        return {}