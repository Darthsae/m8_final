from typing import Any

class Interactable:
    def __init__(self, name: str, description: str, tags: list[str], uses, data: dict[str, Any]):
        self.name: str = name
        self.description: str = description
        self.tags: list[str] = tags
        self.uses = uses
        self.data: dict[str, Any] = data

    def hasData(self, key: str) -> Any:
        """Checks if the key is in the interactables data.
        """
        return key in self.data

    def getData(self, key: str) -> Any:
        """Returns the value of the key in the interactables data.
        """
        return self.data[key]

    def addData(self, key: str, value: Any, _ = None) -> None:
        """Add data with a key of value to the interactable.
        """
        self.data[key] = value

    def removeData(self, key: str) -> None:
        """Remove data from the interactable.
        """
        self.data.pop(key)

    def getDescription(self) -> str:
        """Return the display description of the interactable.
        """
        return f"There is a {self.name} in the room."

    @classmethod
    def fromDict(cls, data):
        """Create an interactable from a dictionary.
        """
        interactable = cls(
            data["name"], data["description"], data["tags"], data["uses"], data["data"]
        )
        return interactable

    def toDict(self) -> dict[str, Any]:
        """Convert the interactable to a dictionary.
        """
        return {
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "uses": self.uses,
            "data": self.data
        }