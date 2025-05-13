from .util import indexOfIndexable
import random


def parse(data, game):
    data_type = data["type"]

    if data_type == "change_hp":
        respect_cap = data["respect_cap"]
        xp_target = data["xp_target"]
        target = data["target"]
        amount = parseValue(data["amount"])

        def toReturn(targets):
            if targets[target].changeHP(amount(targets), respect_cap) and xp_target != -1:
                targets[xp_target].addXP(targets[target].xp)
    elif data_type == "change_xp":
        target = data["target"]
        amount = parseValue(data["amount"])

        def toReturn(targets):
            targets[target].addXP(amount(targets))
    elif data_type == "check_data":
        present = data["present"]
        key = data["data"]
        target = data["target"]

        def toReturn(targets):
            return (
                targets[target].hasData(key)
                if present
                else not targets[target].hasData(key)
            )
    elif data_type == "add_data":
        decay = parseValue(data["decay"])
        key = data["data"]
        value = parseValue(data["value"])
        target = data["target"]

        def toReturn(targets):
            targets[target].addData(key, value(targets), decay(targets))
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
            targets[target].changeRoom(
                random.randint(x_min, x_max), random.randint(y_min, y_max)
            )
    elif data_type == "room_chain":
        room_pool = data["room_pool"]
        min = data["min"]
        max = data["max"]
        position = parseValue(data["position"])
        target = data["target"]

        def toReturn(targets):
            return min <= targets[target].roomChain(position(targets), room_pool) <= max
    elif data_type == "room_pool_count":
        room_pool = data["room_pool"]
        min = parseValue(data["min"])
        max = parseValue(data["max"])
        target = data["target"]

        def toReturn(targets):
            return min(targets) <= targets[target].roomPoolCount(room_pool) <= max(targets)
    elif data_type == "add_entities":
        entities = [
            parseEntityEntry(entity_data, game) for entity_data in data["entities"]
        ]
        cap = sum(map(indexOfIndexable(0), entities))
        amount = parseValue(data["amount"])
        target = data["target"]

        def toReturn(targets):
            temp = random.random() * cap
            for weight, entity_function in entities:
                temp -= weight
                if temp <= 0:
                    for _ in range(amount(targets)):
                        targets[target].addEntity(entity_function())
                    return
    elif data_type == "change_max_hp":
        target = data["target"]
        amount = parseValue(data["amount"])

        def toReturn(targets):
            targets[target].max_hp += amount(targets)
            targets[target].hp += amount(targets)
    elif data_type == "change_stack":
        target = data["target"]
        amount = parseValue(data["amount"])

        def toReturn(targets):
            targets[target].changeStack(amount(targets))
    elif data_type == "add_interactable":
        info = data["interactable"]
        amount = parseValue(data["amount"])
        target = data["target"]
        from .map import Interactable
        def toReturn(targets):
            for _ in range(amount(targets)):
                targets[target].addInteractable(Interactable.fromDict(info))
    elif data_type == "add_item":
        target = data["target"]
        amount = parseValue(data["amount"])
        item_type = parseValue(data["item"])
        from .components import Inventory
        def toReturn(targets):
            for component in targets[target].components:
                if isinstance(component, Inventory):
                    for _ in range(amount(targets)):
                        component.addItem(game.item_types[item_type(targets)])
    elif data_type == "remove_interactable":
        interactable = data["interactable"]
        room = data["room"]
        def toReturn(targets):
            room_room = targets[room]
            room_room.removeInteractable(targets[interactable])
    elif data_type == "greater_than":
        value_one = parseValue(data["value_one"])
        value_two = parseValue(data["value_two"])
        def toReturn(targets):
            return value_one(targets) > value_two(targets)


    return toReturn


def parseValue(data):
    if isinstance(data, dict) and "type" in data:
        data_type = data["type"]
        if data_type == "target":
            target = data["target"]

            def toReturn(targets):
                return targets[target]
        elif data_type == "get_data":
            data_key = data["data"]
            target = data["target"]

            def toReturn(targets):
                return targets[target].getData(data_key)
        elif data_type == "random_int":
            lower = parseValue(data["lower"])
            upper = parseValue(data["upper"])
            
            def toReturn(targets):
                return random.randint(lower(targets), upper(targets))
        elif data_type == "random_uniform":
            lower = parseValue(data["lower"])
            upper = parseValue(data["upper"])

            def toReturn(targets):
                return random.uniform(lower(targets), upper(targets))
        elif data_type == "add":
            value_one = parseValue(data["value_one"])
            value_two = parseValue(data["value_two"])

            def toReturn(targets):
                return value_one(targets) + value_two(targets)
        else:
            def toReturn(targets):
                return data
    else:

        def toReturn(targets):
            return data

    return toReturn


def parseEntityEntry(data, game):
    weight = data["weight"]
    entity_type = game.entity_types[data["type"]]
    overrides = data["overrides"]

    from .entity import EntityInstance
    from .components import componentFromData

    def createEntity():
        entity = EntityInstance(game, entity_type)
        if "name" in overrides:
            entity.name = overrides["name"]
        if "description" in overrides:
            entity.description = overrides["description"]
        if "tags" in overrides:
            for tag in overrides["tags"]:
                tag_type = tag["type"]
                value = tag["value"]
                if tag_type == "add":
                    if value not in entity.tags:
                        entity.tags.append(value)
                elif tag_type == "remove":
                    if value in entity.tags:
                        entity.tags.remove(value)
        if "components" in overrides:
            entity.components.extend(
                [
                    componentFromData(component_data, game)
                    for component_data in overrides["components"]
                ]
            )
        if "actions" in overrides:
            for action in overrides["actions"]:
                entity.addAction(game.ability_types[action])
        if "classes" in overrides:
            for class_data in overrides["classes"]:
                class_type = game.class_types[class_data["class"]]
                for _ in range(class_data["level"]):
                    entity.gainClassLevel(class_type, game.ability_types)
        if "faction" in overrides:
            entity.faction = overrides["faction"]
        return entity

    return weight, createEntity
