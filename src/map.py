class RoomType:
    def __init__(self):
        self.name = ""
        self.description = ""
        
    @classmethod
    def fromDict(cls, data):
        return cls(**data)
        
class RoomInstance:
    def __init__(self, room_type):
        self.__room_type = room_type
    
    def getType(self):
        return self.__room_type

    @classmethod
    def fromDict(cls, data):
        return cls(**data)
    
    def toDict(self):
        return {}
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
        return cls(**data)
    
    def toDict(self):
        return {}