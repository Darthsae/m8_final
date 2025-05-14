faction_names = ["A", "B", "C", "D"]

class Faction:
    def __init__(self, id, name, hostile):
        self.id = id
        self.name = name
        self.hostile = hostile
        
    @classmethod
    def fromDict(cls, id, data):
        """Creates faction from a dictionary.
        """
        faction = cls(id, data["name"], data["hostile"])
        return faction
    
    def toDict(self):
        """Creates a dictonary from the faction.
        """
        return {
            "name": self.name,
            "hostile": self.hostile
        }