from .script_parsing import parse
from typing import Any, Self

class AbilityType:
    def __init__(self, game, id: str, name: str, description: str, effects, targets, requirements):
        self.id: str = id
        self.name: str = name
        self.description: str = description
        self.effects = [parse(effect, game) for effect in effects]
        self.targets = targets
        self.requirements = [parse(requirement, game) for requirement in requirements]

    @classmethod
    def fromDict(cls, game, id: str, data: dict[str, Any]) -> Self:
        """Load an ability type from a dictionary.
        """
        ability: AbilityType = cls(game, id, data["name"], data["description"], data["effects"], data["targets"], data["requirements"])
        return ability

class AbilityInstance:
    def __init__(self, ability_type: AbilityType):
        self.__ability_type: AbilityType = ability_type
    
    def getType(self) -> AbilityType:
        """Get the type of ability this ability is.
        """
        return self.__ability_type
    
    def canApply(self, targets: list[Any]) -> bool:
        """Return if ability can be applied to selected targets.
        """
        if len(targets) != len(self.__ability_type.targets):
            return False
        
        # Validate Target Types maybe?

        for req in self.__ability_type.requirements:
            if not req(targets):
                return False
            
        return True
    
    def apply(self, targets: list[Any]) -> None:
        """Apply ability to targets.
        """
        for effect in self.__ability_type.effects:
            effect(targets)

    def __repr__(self) -> str:
        return self.__ability_type.name

    @classmethod
    def fromDict(cls, data: dict[str, Any], ability_types) -> Self:
        """Get ability from a dictionary.
        """
        ability: AbilityInstance = cls(ability_types[data["type"]])
        return ability
    
    def toDict(self) -> dict[str, str]:
        """Convert an ability to a dictionary.
        """
        return {
            "type": self.__ability_type.id,
        }
