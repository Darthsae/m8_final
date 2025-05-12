def floatput(prompt):
    """Get a float as input

    Args:
        prompt (str): the prompt to display

    Returns:
        float: value of input as float
    """
    return float(input(prompt))

def intput(prompt):
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

def boolput(prompt, case_sensitive, true_values):
    """Get a bool as input
    
    Args:
        prompt (str): the prompt to display
        case_sensitive (bool): whether to be case sensitive with the input
        true_values (set[str]): the values to consider true

    Returns:
        bool: value of input as bool
    """
    answer = input(prompt)
    return answer.lower() if case_sensitive else answer in true_values

class DoubleValue:
    def __init__(self, value_one, value_two):
        self.value_one = value_one
        self.value_two = value_two

class Restrictions:
    def __init__(self, required, allowed, excluded):
        self.required = required
        self.allowed = allowed
        self.excluded = excluded
    
    def score(self, tags):
        """Scores a set of tags validity for the set of restrictions.
        """
        requirements = set(self.required)
        score = 1
        for tag in tags:
            if tag in self.excluded:
                return 0
            elif tag in requirements:
                requirements.remove(tag)
            elif tag in self.allowed:
                score += 1
        return 0 if len(requirements) > 0 else score
    
    @classmethod
    def fromDict(cls, data):
        return cls(data["required"], data["allowed"], data["excluded"])

def adjacentPositions(position):
    return [
        (position[0] + 1, position[1]    ),
        (position[0] - 1, position[1]    ),
        (position[0]    , position[1] + 1),
        (position[0]    , position[1] - 1)
    ]

def indexOfIndexable(index):
    def toReturn(indexable):
        return indexable[index]
    return toReturn

def longToString(long):
    return chr(long >> 56 & 0xFF) + chr(long >> 48 & 0xFF) + chr(long >> 40 & 0xFF) + chr(long >> 32 & 0xFF) + chr(long >> 24 & 0xFF) + chr(long >> 16 & 0xFF) + chr(long >> 8 & 0xFF) + chr(long & 0xFF)