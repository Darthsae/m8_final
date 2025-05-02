from .classes import ClassInstance

class EntityType:
    def __init__(self, name, description, hp):
        self.name = name
        self.description = description
        self.hp = hp
        self.components = []
        
    @classmethod
    def fromDict(cls, data):
        entity_type = cls(data["name"], data["description"], data["hp"])

        return entity_type

class EntityInstance:
    NULL_ENTITY_TYPE = EntityType("", "", 1)

    def __init__(self, entity_type):
        self.__entity_type = entity_type
        self.name = self.__entity_type.name
        self.description = self.__entity_type.description
        self.max_hp = self.__entity_type.hp
        self.hp = self.__entity_type.hp
        self.components = self.__entity_type.components
        self.actions = []
        self.__classes = []
        self.xp = 0
        
    @classmethod
    def fromDict(cls, data):
        entity = cls(data["type"])
        if "name" in data:
            entity.name = data["name"]
        if "description" in data:
            entity.description = data["description"]
        if "hp" in data:
            entity.hp = data["hp"]
        if "xp" in data:
            entity.xp = data["xp"]
        if "classes" in data:
            entity.__classes = [ClassInstance.fromDict(class_data) for class_data in data["classes"]]
        return entity
    
    def toDict(self):
        return {
            "type": self.__entity_type,
            "name": self.name,
            "description": self.description,
            "hp": self.hp,
            "xp": self.xp,
            "classes": [class_data.toDict() for class_data in self.__classes]
        }