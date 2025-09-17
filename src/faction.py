from typing import Any, Self

faction_names = ["A", "B", "C", "D"]

class Faction:
    def __init__(self, id: str, name: str, hostile: list[str]):
        self.id: str = id
        self.name: str = name
        self.hostile: list[str] = hostile
        
    @classmethod
    def fromDict(cls, id: str, data: dict[str, Any]) -> Self:
        """Creates faction from a dictionary.
        """
        faction: Faction = cls(id, data["name"], data["hostile"])
        return faction
    
    def toDict(self) -> dict[str, Any]:
        """Creates a dictonary from the faction.
        """
        return {
            "name": self.name,
            "hostile": self.hostile
        }