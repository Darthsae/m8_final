from .item import ItemInstance

class Component:
    def __init__(self):
        pass

    def update(self, game, room, entity):
        pass

    def battle(self, game, battle, entity, opponents):
        pass

    @classmethod
    def fromDict(cls, data):
        return cls(**data)
    
    def toDict(self):
        return {}

class Inventory(Component):
    def __init__(self, size):
        self.items = [None for _ in range(size)]
        
    def getItem(self, index):
        return self.items[index]
    
    def addItem(self, itemToAdd):
        for i, item in enumerate(self.items):
            if isinstance(item, ItemInstance) and item.getType() == itemToAdd.getType() and item.canAddStack(itemToAdd.stack):
                item.addStack(itemToAdd.stack)
                return True
            elif isinstance(item, None):
                self.items[i] = itemToAdd
                return True
        return False

    @classmethod
    def fromDict(cls, data):
        inventory = cls(0)
        if "items" in data:
            inventory.items = [ItemInstance.fromDict(item_instance) for item_instance in data["items"]]
        return inventory

    def toDict(self):
        return {
            "type": "inventory",
            "items": [ItemInstance.fromDict()]
        }

class AI(Component):
    def __init__(self):
        ...
    
    def evaluateOpponents(self, opponents):
        ...
    
    def evaluateOptions(self, entity):
        ...
    
    def update(self, game, room, entity):
        in_battle = entity.hasData("in_battle")
        if not in_battle:
            entities_in_room = (set(room.entities) - {entity}) | {game.player}
            hostile = [entity_room for entity_room in entities_in_room if entity.isHostile(game, entity_room)]
            if len(hostile) > 0:
                id = game.battle_manager.startBattle(room)
                game.battle_manager.joinBattle(entity, id)
                for hostile_creature in hostile:
                    game.battle_manager.joinBattle(hostile_creature, id)

    def battle(self, game, battle, entity, participants):
        opponents = [participant for participant in participants if entity.isHostile(game, participant)]
        allies = list(set(participants) - set(opponents))
        if len(opponents) == 0:
            game.battle_manager.leaveBattle(entity, battle.id)
        
    @classmethod
    def fromDict(cls, data):
        ai = cls()
        return ai

    def toDict(self):
        return {
            "type": "ai"
        }

def componentFromData(data):
    type = data["type"]
    if type == "inventory":
        return Inventory.fromDict(data)
    elif type == "ai":
        return AI.fromDict(data)
