from .classes import ClassInstance
from .components import componentFromData
from .util import DoubleValue
from .ability import AbilityInstance

class EntityType:
    def __init__(self, id, name, description, tags, hp, xp, speed):
        self.id = id
        self.name = name
        self.description = description
        self.tags = tags
        self.hp = hp
        self.components = []
        self.actions = []
        self.classes = []
        self.xp = xp
        self.speed = speed
        
    @classmethod
    def fromDict(cls, id, data):
        entity_type = cls(id, data["name"], data["description"], data["tags"], data["hp"], data["xp"], data["speed"])

        return entity_type

class EntityInstance:
    NULL_ENTITY_TYPE = EntityType("", "", "", [], 1, 0, 0)

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
        self.speed = self.__entity_type.speed
        self.data = {}

    def getClassesDisplayString(self):
        string = ""
        for class_data in self.__classes:
            string += class_data.getType().name + " " + str(class_data.level) + "\n"
        return string
    
    def update(self):
        for key in self.data:
            value = self.data.pop(key)
            if value[1] == 0:
                pass
            elif value[1] == -1:
                self.data[key] = value
            else:
                self.data[key] = (value[0], value[1] - 1)
    
    def gainClassLevel(self, class_type, ability_types):
        for class_instance in self.__classes:
            if class_instance.getType() == class_type:
                level = class_instance.level + 1
                if level == class_type.maxLevel():
                    return
                else:
                    class_type.level_data[level].applyTo(self, ability_types)
                    class_instance.level += 1
                    return
        class_instance = ClassInstance(class_type, 0)
        class_type.level_data[0].applyTo(self, ability_types)
        self.__classes.append(class_instance)

    def changeHP(self, amount, respect_cap):
        pre_hp = max(self.hp, self.max_hp)
        self.hp = max(self.hp + amount, 0)
        if respect_cap:
            self.hp = min(self.hp, pre_hp)
        if self.hp == 0:
            ...
    
    def addAction(self, action_type):
        self.actions.append(AbilityInstance(action_type))

    def flee(self):
        ...

    def changeRoom(self, x, y):
        ...
    
    def hasData(self, key):
        return key in self.data

    def addData(self, key, value, decay):
        self.data[key] = (value, decay)
    
    @classmethod
    def fromDict(cls, data, entity_types):
        entity = cls(entity_types[data["type"]])
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
        if "speed" in data:
            entity.speed = data["speed"]
        if "components" in data:
            entity.components = [componentFromData(component_data) for component_data in data["components"]]
        if "classes" in data:
            entity.__classes = [ClassInstance.fromDict(class_data) for class_data in data["classes"]]
        if "data" in data:
            entity.data = data["data"]
        return entity
    
    def toDict(self):
        return {
            "type": self.__entity_type.id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "hp": self.hp,
            "xp": self.xp,
            "speed": self.speed,
            "components": [component_data.toDict() for component_data in self.components],
            "classes": [class_data.toDict() for class_data in self.__classes],
            "data": self.data
        }
