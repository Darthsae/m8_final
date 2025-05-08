from .item import ItemInstance
from .dummy import dummyFindActionType

class Component:
    def __init__(self):
        pass

    def update(self, room, entity):
        pass

    def battle(self, battle, entity, opponents):
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
            if (
                isinstance(item, ItemInstance)
                and item.getType() == itemToAdd.getType()
                and item.canAddStack(itemToAdd.stack)
            ):
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
            inventory.items = [
                ItemInstance.fromDict(item_instance) for item_instance in data["items"]
            ]
        return inventory

    def toDict(self):
        return {"type": "inventory", "items": [ItemInstance.fromDict()]}


class AI(Component):
    def __init__(self, personality):
        self.personality = personality

    def evaluateOpponents(self, opponents): ...

    def evaluateOptions(self, entity): ...

    def update(self, room, entity):
        in_battle = entity.hasData("in_battle")
        if not in_battle:
            entities_in_room = (set(room.entities) - {entity}) | {entity.game.player}
            hostile = [
                entity_room
                for entity_room in entities_in_room
                if entity.isHostile(entity_room)
            ]
            if len(hostile) > 0:
                id = entity.game.battle_manager.startBattle(room)
                entity.game.battle_manager.joinBattle(entity, id)
                for hostile_creature in hostile:
                    if hostile_creature == entity.game.player:
                        entity.game.addMenu("dungeon_combat")()
                    entity.game.battle_manager.joinBattle(hostile_creature, id)
        else:
            ...

    def battle(self, battle, entity, participants):
        opponents = [
            participant for participant in participants if entity.isHostile(participant)
        ]
        allies = list(set(participants) - set(opponents))
        if len(opponents) == 0:
            entity.game.battle_manager.leaveBattle(entity, battle.id)
        else:
            # Complicated Evaluation stuff.
            flee_value = self.personality["flee"]["percent_of_missing_hp"] * (1 - entity.hp / entity.max_hp)
            for action in entity.actions:
                # Catagorize Action Type
                action_type = dummyFindActionType(entity, action)
                if action_type == "self_heal":
                    ...
                elif action_type == "other_heal":
                    ...
                elif action_type == "other_damage":
                    ...

    @classmethod
    def fromDict(cls, data):
        ai = cls(data["personality"])
        return ai

    def toDict(self):
        return {
            "type": "ai",
            "personality": {
                "attack": {
                    "damage_to_target": {
                        "overtime": {
                            "number_of_targets": 1.0,
                            "kills": 1.0,
                            "percent_of_total_hp": 1.0,
                            "percent_of_remaining_hp": 1.0,
                        },
                        "instant": {
                            "number_of_targets": 1.0,
                            "kills": 1.0,
                            "percent_of_total_hp": 1.0,
                            "percent_of_remaining_hp": 1.0,
                        },
                    },
                    "damage_target_can_do": {
                        "overtime": {
                            "number_of_targets": 1.0,
                            "kills": 1.0,
                            "percent_of_total_hp": 1.0,
                            "percent_of_remaining_hp": 1.0,
                        },
                        "instant": {
                            "number_of_targets": 1.0,
                            "kills": 1.0,
                            "percent_of_total_hp": 1.0,
                            "percent_of_remaining_hp": 1.0,
                        },
                    },
                    "healing_target_can_do": {
                        "others": {
                            "overtime": {
                                "number_of_targets": 1.0,
                                "percent_of_total_hp": 1.0,
                                "percent_of_missing_hp": 1.0,
                                "percent_of_remaining_hp": 1.0,
                                "percent_of_max_hp": 1.0,
                            },
                            "instant": {
                                "number_of_targets": 1.0,
                                "percent_of_total_hp": 1.0,
                                "percent_of_missing_hp": 1.0,
                                "percent_of_remaining_hp": 1.0,
                                "percent_of_max_hp": 1.0,
                            },
                        },
                        "self": {
                            "overtime": {
                                "percent_of_total_hp": 1.0,
                                "percent_of_missing_hp": 1.0,
                                "percent_of_remaining_hp": 1.0,
                                "percent_of_max_hp": 1.0,
                            },
                            "instant": {
                                "percent_of_total_hp": 1.0,
                                "percent_of_missing_hp": 1.0,
                                "percent_of_remaining_hp": 1.0,
                                "percent_of_max_hp": 1.0,
                            },
                        },
                    },
                },
                "heal": {
                    "others": {
                        "overtime": {
                            "number_of_targets": 1.0,
                            "percent_of_total_hp": 1.0,
                            "percent_of_missing_hp": 1.0,
                            "percent_of_remaining_hp": 1.0,
                            "percent_of_max_hp": 1.0,
                        },
                        "instant": {
                            "number_of_targets": 1.0,
                            "percent_of_total_hp": 1.0,
                            "percent_of_missing_hp": 1.0,
                            "percent_of_remaining_hp": 1.0,
                            "percent_of_max_hp": 1.0,
                        },
                    },
                    "self": {
                        "overtime": {
                            "percent_of_total_hp": 1.0,
                            "percent_of_missing_hp": 1.0,
                            "percent_of_remaining_hp": 1.0,
                            "percent_of_max_hp": 1.0,
                        },
                        "instant": {
                            "percent_of_total_hp": 1.0,
                            "percent_of_missing_hp": 1.0,
                            "percent_of_remaining_hp": 1.0,
                            "percent_of_max_hp": 1.0,
                        },
                    },
                },
                "flee": {"percent_of_missing_hp": 1.0},
            },
        }


def componentFromData(data):
    type = data["type"]
    if type == "inventory":
        return Inventory.fromDict(data)
    elif type == "ai":
        return AI.fromDict(data)
