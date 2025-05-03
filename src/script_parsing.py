import random

def parse(data):
    data_type = data["type"]

    if data_type == "change_hp":
        respect_cap = data["respect_cap"]
        target = data["target"]
        amount = data["amount"]
        def toReturn(targets):
            targets[target].changeHP(amount, respect_cap)
    elif data_type == "check_data":
        present = data["present"]
        key = data["data"]
        target = data["target"]
        def toReturn(targets):
            return targets[target].hasData(key) if present else not targets[target].hasData(key)
    elif data_type == "add_data":
        decay = data["decay"]
        key = data["data"]
        value = parseValue(data["value"])
        target = data["target"]
        def toReturn(targets):
            targets[target].addData(key, value(targets), decay)
    elif data_type == "flee":
        target = data["target"]
        def toReturn(targets):
            targets[target].flee()
    elif data_type == "change_room":
        x_min = data["x_min"]
        x_max = data["x_max"]
        y_min = data["y_min"]
        y_max = data["y_max"]
        target = data["target"]
        def toReturn(targets):
            targets[target].changeRoom(random.randint(x_min, x_max), random.randint(y_min, y_max))
    
    return toReturn

def parseValue(data):
    if data is dict and "type" in data:
        data_type = data["type"]
        if data_type == "target":
            target = data["target"]
            def toReturn(targets):
                return targets[target]
        else:
            def toReturn(targets):
                return data
    else:
        def toReturn(targets):
            return data

    return toReturn