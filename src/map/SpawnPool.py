from typing import Callable, Any, Self
from ..util import Restrictions
from ..script_parsing import parse
from .RoomInstance import RoomInstance

class SpawnPool:
    def __init__(self, id: str, name: str, restrictions):
        self.id: str = id
        self.name: str = name
        self.effects: list[Callable[[list[Any]], None]] = []
        self.conditions: list[Callable[[list[Any]], bool]] = []
        self.restrictions: Restrictions = restrictions

    def getScore(self, room: RoomInstance) -> int:
        """Get the validation score for this spawnpool.
        """
        for condition in self.conditions:
            if not condition([room]):
                return 0
        return self.restrictions.score(room.tags)

    def applyTo(self, room: RoomInstance) -> None:
        """Apply the spawnpool to a room.
        """
        for effect in self.effects:
            effect([room])

    @classmethod
    def fromDict(cls, game, id: str, data) -> Self:
        """Load a SpawnPool from a dictionary.
        """
        spawn_pool: SpawnPool = cls(id, data["name"], Restrictions.fromDict(data["restrictions"]))
        spawn_pool.effects = [parse(effect, game) for effect in data["effects"]]
        spawn_pool.conditions = [
            parse(condition, game) for condition in data["conditions"]
        ]
        return spawn_pool