class ItemType:
    def __init__(self, id, name, description, tags, stack, uses):
        self.id = id
        self.name = name
        self.description = description
        self.tags = tags
        self.stack = stack
        self.uses = uses
        
    @classmethod
    def fromDict(cls, id, data):
        """Make an item from a dictionary.
        """
        item = cls(id, data["name"], data["description"], data["tags"], data["stack"], data["uses"])
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
        """Gets the item's type.
        """
        return self.__item_type
    
    def changeStack(self, amount):
        """Add a stack to the item.
        """
        self.stack = min(max(self.stack + amount, 0), self.max_stack)
        if self.stack == 0:
            self = None
    
    def canAddStack(self, item):
        """If you can add a stack to an item.
        """
        return self.stack < self.max_stack
    
    @classmethod
    def fromDict(cls, data, item_types):
        """Makes an item instance from a dict.
        """
        item = cls(item_types[data["type"]])
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
        """Turns an item instance into a dictionary representation.
        """
        return {
            "type": self.__item_type.id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "stack": self.stack,
            "data": self.data
        }
