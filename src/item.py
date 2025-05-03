class ItemType:
    def __init__(self, name, description, tags, stack):
        self.name = name
        self.description = description
        self.tags = tags
        self.stack = stack
        self.uses = []
        
    @classmethod
    def fromDict(cls, data):
        item = cls(data["name"], data["description"], data["tags"], data["stack"])
        return item

class ItemInstance:
    def __init__(self, item_type):
        self.__item_type = item_type
        self.name = self.__item_type.name
        self.description = self.__item_type.description
        self.tags = self.__item_type.tags
        self.max_stack = self.__item_type.stack
        self.stack = 1
        self.data = {}
    
    def __repr__(self):
        return f"{self.stack}x {self.name}"
    
    def getType(self):
        return self.__item_type
    
    @classmethod
    def fromDict(cls, data):
        item = cls(data["type"])
        if "name" in data:
            item.name = data["name"]
        if "description" in data:
            item.description = data["description"]
        if "tags" in data:
            item.tags = data["tags"]
        if "stack" in data:
            item.stack = data["stack"]
        if "data" in data:
            item.data = data["data"]
        return item
    
    def toDict(self):
        return {
            "type": self.__item_type,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "stack": self.stack,
            "data": self.data
        }
