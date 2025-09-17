from typing import Any, Self, Callable

def floatput(prompt: str) -> float:
    """Get a float as input

    Args:
        prompt (str): the prompt to display

    Returns:
        float: value of input as float
    """
    try:
        return float(input(prompt))
    except:
        return floatput(prompt)

def intput(prompt: str) -> int:
    """Get an int as input
    
    Args:
        prompt (str): the prompt to display

    Returns:
        int: value of input as int
    """
    try:
        return int(input(prompt))
    except:
        return intput(prompt)

def boolput(prompt: str, case_sensitive: bool, true_values: set[str]) -> bool:
    """Get a bool as input
    
    Args:
        prompt (str): the prompt to display
        case_sensitive (bool): whether to be case sensitive with the input
        true_values (set[str]): the values to consider true

    Returns:
        bool: value of input as bool
    """
    answer: str = input(prompt)
    return (answer.lower() if case_sensitive else answer) in true_values

class DoubleValue:
    def __init__(self, value_one: Any, value_two: Any):
        self.value_one: Any = value_one
        self.value_two: Any = value_two

class Restrictions:
    def __init__(self, required: list[str], allowed: list[str], excluded: list[str]):
        self.required: list[str] = required
        self.allowed:  list[str] = allowed
        self.excluded: list[str] = excluded
    
    def score(self, tags: list[str]) -> int:
        """Scores a set of tags validity for the set of restrictions.
        """
        requirements: set[str] = set(self.required)
        score: int = 1
        for tag in tags:
            if tag in self.excluded:
                return 0
            elif tag in requirements:
                requirements.remove(tag)
            elif tag in self.allowed:
                score += 1
        return 0 if len(requirements) > 0 else score
    
    @classmethod
    def fromDict(cls, data: dict[str, Any]) -> Self:
        """Creates a restriction set from a dictionary.
        """
        return cls(data["required"], data["allowed"], data["excluded"])

def adjacentPositions(position: tuple[int, int]) -> list[tuple[int, int]]:
    """Returns a list of adjacent positions to the position.
    """
    return [
        (position[0] + 1, position[1]    ),
        (position[0] - 1, position[1]    ),
        (position[0]    , position[1] + 1),
        (position[0]    , position[1] - 1)
    ]

def indexOfIndexable(index: Any) -> Callable[[Any], Any]:
    """Returns a function which gives the item at an index of an indexable.
    """
    def toReturn(indexable: Any) -> Any:
        return indexable[index]
    return toReturn

def longToString(long: int) -> str:
    """Converts a long to a string of characters.
    """
    return chr(long >> 56 & 0xFF) + chr(long >> 48 & 0xFF) + chr(long >> 40 & 0xFF) + chr(long >> 32 & 0xFF) + chr(long >> 24 & 0xFF) + chr(long >> 16 & 0xFF) + chr(long >> 8 & 0xFF) + chr(long & 0xFF)


def positionToString(position: tuple[int, int]) -> str:
    """Converts a position to a string.
    """
    return f"{position[0]},{position[1]}"

def stringToPosition(string: str) -> tuple[int, int]:
    """Converts a string to a position.
    """
    data: list[str] = string.split(",")
    return (int(data[0]), int(data[1]))