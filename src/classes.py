class ClassType:
    def __init__(self, name, description, level_data):
        self.name = name
        self.description = description
        self.level_data = level_data
        
    @classmethod
    def fromDict(cls, data):
        return cls(**data)
    
class ClassInstance:
    def __init__(self, class_type, level):
        self.__class_type = class_type
        self.level = level
    
    def getType(self):
        return self.__class_type
    
    @classmethod
    def fromDict(cls, data):
        return cls(**data)
    
    def toDict(self):
        return {}