from typing import Any, Self

class ItemType:
    def __init__(self, id: str, name: str, description: str, tags: list[str], stack: int, uses):
        self.id: str = id
        self.name: str = name
        self.description: str = description
        self.tags: list[str] = tags
        self.stack: int = stack
        self.uses = uses
        
    @classmethod
    def fromDict(cls, id: str, data: dict[str, Any]) -> Self:
        """Make an item from a dictionary.
        """
        item: ItemType = cls(id, data["name"], data["description"], data["tags"], data["stack"], data["uses"])
        return item

class ItemInstance:
    def __init__(self, item_type: ItemType):
        self.__item_type: ItemType = item_type
        self.name: str = self.__item_type.name
        self.description: str = self.__item_type.description
        self.tags: list[str] = self.__item_type.tags
        self.max_stack: int = self.__item_type.stack
        self.stack: int = 1
        self.data: dict[str, Any] = {}
    
    def __repr__(self) -> str:
        return f"{self.stack}x {self.name}"
    
    def getType(self) -> ItemType:
        """Gets the item's type.
        """
        return self.__item_type
    
    def changeStack(self, amount: int) -> None:
        """Add a stack to the item.
        """
        self.stack = min(max(self.stack + amount, 0), self.max_stack)
        if self.stack == 0:
            self = None
    
    def canAddStack(self, item) -> bool:
        """If you can add a stack to an item.
        """
        return self.stack < self.max_stack
    
    @classmethod
    def fromDict(cls, data: dict[str, Any], item_types: dict[str, ItemType]):
        """Makes an item instance from a dict.
        """
        item: ItemInstance = cls(item_types[data["type"]])
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
    
    def toDict(self) -> dict[str, Any]:
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
