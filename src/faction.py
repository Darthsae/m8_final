faction_names = ["A", "B", "C", "D"]

class Faction:
    def __init__(self, name, hostile):
        self.name = name
        self.hostile = hostile
        
    @classmethod
    def fromDict(cls, data):
        faction = cls(data["name"], data["hostile"])
        return faction
    
    def toDict(self):
        return {
            "name": self.name,
            "hostile": self.hostile
        }