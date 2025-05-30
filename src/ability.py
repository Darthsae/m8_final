from .script_parsing import parse

class AbilityType:
    def __init__(self, game, id, name, description, effects, targets, requirements):
        self.id = id
        self.name = name
        self.description = description
        self.effects = [parse(effect, game) for effect in effects]
        self.targets = targets
        self.requirements = [parse(requirement, game) for requirement in requirements]

    @classmethod
    def fromDict(cls, game, id, data):
        """Load an ability type from a dictionary.
        """
        ability = cls(game, id, data["name"], data["description"], data["effects"], data["targets"], data["requirements"])
        return ability

class AbilityInstance:
    def __init__(self, ability_type):
        self.__ability_type = ability_type
    
    def getType(self):
        """Get the type of ability this ability is.
        """
        return self.__ability_type
    
    def canApply(self, targets):
        """Return if ability can be applied to selected targets.
        """
        if len(targets) != len(self.__ability_type.targets):
            return False
        
        # Validate Target Types maybe?

        for req in self.__ability_type.requirements:
            if not req(targets):
                return False
            
        return True
    
    def apply(self, targets):
        """Apply ability to targets.
        """
        for effect in self.__ability_type.effects:
            effect(targets)

    def __repr__(self):
        return self.__ability_type.name

    @classmethod
    def fromDict(cls, data, ability_types):
        """Get ability from a dictionary.
        """
        ability = cls(ability_types[data["type"]])
        return ability
    
    def toDict(self):
        """Convert an ability to a dictionary.
        """
        return {
            "type": self.__ability_type.id,
        }
