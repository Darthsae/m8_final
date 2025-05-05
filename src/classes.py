class LevelDetail:
    def __init__(self, xp_cost, features, abilities):
        self.xp_cost = xp_cost
        self.features = features
        self.abilities = abilities
    
    def applyTo(self, apply_to, ability_types):
        for feature in self.features:
            ...
        for ability in self.abilities:
            behavior = ability["type"]
            if behavior == "add":
                apply_to.addAction(ability_types[ability["ability"]])
    
    @classmethod
    def fromDict(cls, data):
        level_detail = cls(data["xp_cost"], data["features"], data["abilities"])

        return level_detail

class ClassType:
    def __init__(self, id, name, description, level_data):
        self.id = id
        self.name = name
        self.description = description
        self.level_data = level_data

    def maxLevel(self):
        return len(self.level_data)
    
    @classmethod
    def fromDict(cls, id, data):
        class_type = cls(id, data["name"], data["description"], [LevelDetail.fromDict(level_data) for level_data in data["level_data"]])
        
        return class_type
    
class ClassInstance:
    def __init__(self, class_type, level):
        self.__class_type = class_type
        self.level = level
    
    def getType(self):
        return self.__class_type
    
    @classmethod
    def fromDict(cls, data, class_types):
        return cls(class_types[data["type"]], data["level"])
    
    def toDict(self):
        return {
            "type": self.__class_type.id,
            "level": self.level
        }
