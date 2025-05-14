from .script_parsing import parse

class LevelDetail:
    def __init__(self, game, xp_cost, features, abilities):
        self.xp_cost = xp_cost
        self.features = [parse(feature_data, game) for feature_data in features]
        self.abilities = abilities
    
    def applyTo(self, apply_to, ability_types):
        """Apply level details to an entity.
        """
        for feature in self.features:
            feature([apply_to])
        for ability in self.abilities:
            behavior = ability["type"]
            if behavior == "add":
                ability_instance = ability_types[ability["ability"]]
                if not apply_to.hasAction(ability_instance):
                    apply_to.addAction(ability_instance)
    
    @classmethod
    def fromDict(cls, game, data):
        """Load level details from a dictionary.
        """
        level_detail = cls(game, data["xp_cost"], data["features"], data["abilities"])

        return level_detail

class ClassType:
    def __init__(self, id, name, description, level_data):
        self.id = id
        self.name = name
        self.description = description
        self.level_data = level_data

    def maxLevel(self):
        """Get the max level of the class.
        """
        return len(self.level_data)
    
    def __repr__(self):
        return self.description
    
    @classmethod
    def fromDict(cls, game, id, data):
        """Load classes from a dictionary.
        """
        class_type = cls(id, data["name"], data["description"], [LevelDetail.fromDict(game, level_data) for level_data in data["level_data"]])
        
        return class_type
    
class ClassInstance:
    def __init__(self, class_type, level):
        self.__class_type = class_type
        self.level = level
    
    def getType(self):
        """Get the class type of the class instance.
        """
        return self.__class_type
    
    @classmethod
    def fromDict(cls, data, class_types):
        """Load a class instance from a dictionary.
        """
        return cls(class_types[data["type"]], data["level"])
    
    def toDict(self):
        """Convert the class instance to a dictionary.
        """
        return {
            "type": self.__class_type.id,
            "level": self.level
        }
