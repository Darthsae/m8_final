from .script_parsing import parse

class AbilityType:
    def __init__(self, id, name, description, effects, targets, requirements):
        self.id = id
        self.name = name
        self.description = description
        self.effects = [parse(effect) for effect in effects]
        self.targets = targets
        self.requirements = [parse(requirement) for requirement in requirements]

    @classmethod
    def fromDict(cls, id, data):
        ability = cls(id, data["name"], data["description"], data["effects"], data["targets"], data["requirements"])
        return ability

class AbilityInstance:
    def __init__(self, ability_type):
        self.__ability_type = ability_type
    
    def getType(self):
        return self.__ability_type
    
    def canApply(self, targets):
        if len(targets) != len(self.__ability_type.targets):
            return False
        
        # Validate Target Types maybe?

        for req in self.__ability_type.requirements:
            if not req(targets):
                return False
            
        return True
    
    def apply(self, targets):
        for effect in self.__ability_type.effects:
            effect(targets)

    @classmethod
    def fromDict(cls, data, ability_types):
        ability = cls(ability_types[data["type"]])
        return ability
    
    def toDict(self):
        return {
            "type": self.__ability_type.id,
        }
