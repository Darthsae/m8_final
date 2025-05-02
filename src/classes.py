class LevelDetail:
    def __init__(self):
        ...
    
    @classmethod
    def fromDict(cls, data):
        level_detail = cls()

        return level_detail

class ClassType:
    def __init__(self, name, description, level_data):
        self.name = name
        self.description = description
        self.level_data = level_data
        
    @classmethod
    def fromDict(cls, data):
        class_type = cls(data["name"], data["description"], data["level_data"])
        
        return class_type
    
class ClassInstance:
    def __init__(self, class_type, level):
        self.__class_type = class_type
        self.level = level
    
    def getType(self):
        return self.__class_type
    
    @classmethod
    def fromDict(cls, data):
        return cls(data["type"], data["level"])
    
    def toDict(self):
        return {
            "type": self.__class_type,
            "level": self.level
        }