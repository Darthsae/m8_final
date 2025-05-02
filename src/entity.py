from .classes import ClassInstance

class EntityType:
    def __init__(self, name, description, tags, hp, xp):
        self.name = name
        self.description = description
        self.tags = tags
        self.hp = hp
        self.components = []
        self.actions = []
        self.classes = []
        self.xp = xp
        
    @classmethod
    def fromDict(cls, data):
        entity_type = cls(data["name"], data["description"], data["tags"], data["hp"], data["xp"])

        return entity_type

class EntityInstance:
    NULL_ENTITY_TYPE = EntityType("", "", [], 1, 0)

    def __init__(self, entity_type):
        self.__entity_type = entity_type
        self.name = self.__entity_type.name
        self.description = self.__entity_type.description
        self.tags = self.__entity_type.tags
        self.max_hp = self.__entity_type.hp
        self.hp = self.__entity_type.hp
        self.components = self.__entity_type.components
        self.actions = []
        self.__classes = []
        self.xp = self.__entity_type.xp
        self.data = {}
        
    @classmethod
    def fromDict(cls, data):
        entity = cls(data["type"])
        if "name" in data:
            entity.name = data["name"]
        if "description" in data:
            entity.description = data["description"]
        if "tags" in data:
            entity.tags = data["tags"]
        if "hp" in data:
            entity.hp = data["hp"]
        if "xp" in data:
            entity.xp = data["xp"]
        if "components" in data:
            entity.components = [componentFromDict(component_data) for component_data in data["components"]]
        if "classes" in data:
            entity.__classes = [ClassInstance.fromDict(class_data) for class_data in data["classes"]]
        if "data" in data:
            entity.data = data["data"]
        return entity
    
    def toDict(self):
        return {
            "type": self.__entity_type,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "hp": self.hp,
            "xp": self.xp,
            "components": [component_data.toDict() for component_data in self.components],
            "classes": [class_data.toDict() for class_data in self.__classes],
            "data": self.data
        }
