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
    return int(input(prompt))

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