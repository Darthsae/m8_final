class ItemType:
    def __init__(self):
        self.name = ""
        self.description = ""
        
    @classmethod
    def fromDict(cls, data):
        return cls(**data)

class ItemInstance:
    def __init__(self, item_type):
        self.__item_type = item_type
    
    def getType(self):
        return self.__item_type
    
    @classmethod
    def fromDict(cls, data):
        return cls(**data)
    
    def toDict(self):
        return {}