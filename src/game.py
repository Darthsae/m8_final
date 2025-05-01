from .entity import EntityInstance

class Game:
    def __init__(self):
        self.player = EntityInstance()
    
    def newGame(self):
        ...
    
    @classmethod
    def fromDict(cls, data):
        return cls(**data)
    
    def toDict(self):
        return {}