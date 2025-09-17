from typing import Any, Self

class RoomType:
    def __init__(self, id: str, name: str, description: str, tags: list[str]):
        self.id: str = id
        self.name: str = name
        self.description: str = description
        self.tags: list[str] = tags

    @classmethod
    def fromDict(cls, id: str, data: dict[str, Any]) -> Self:
        """
        """
        room_type: RoomType = cls(id, data["name"], data["description"], data["tags"])

        return room_type
