class Faction:
    def __init__(self):
        self.name = ""
        self.hostile = []
        
    @classmethod
    def fromDict(cls, data):
        return cls(**data)
    
    def toDict(self):
        return {}