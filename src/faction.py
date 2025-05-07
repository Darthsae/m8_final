faction_names = ["A", "B", "C", "D"]

class Faction:
    def __init__(self, id, name, hostile):
        self.id = id
        self.name = name
        self.hostile = hostile
        
    @classmethod
    def fromDict(cls, id, data):
        faction = cls(id, data["name"], data["hostile"])
        return faction
    
    def toDict(self):
        return {
            "name": self.name,
            "hostile": self.hostile
        }