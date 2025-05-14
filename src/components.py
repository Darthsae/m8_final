from .item import ItemInstance
from .dummy import dummyFindActionType, dummyTestSelfHeal, dummyTestHurt

# Tada, inheritance.
# Technically.

class Component:
    def __init__(self):
        pass

    def update(self, room, entity):
        """Game update virtual function.
        """
        pass

    def battle(self, battle, entity, opponents):
        """Battle update virtual function.
        """
        pass

    def death(self, room, entity):
        """Death virtual function.
        """
        pass

    @classmethod
    def fromDict(cls, data):
        """From dict virtual function."""
        return cls(**data)

    def toDict(self):
        """To dict virtual function."""
        return {}


class FunctionHolder(Component):
    def __init__(self, update, battle):
        self.update_callback = update
        self.battle_callback = battle
    
    def update(self, room, entity):
        """Handle the game update for the FunctionHolder component.
        """
        if self.update_callback != None:
            self.update_callback()
    
    def battle(self, battle, entity, opponents):
        """Handle battle update for the FunctionHolder component.
        """
        if self.battle_callback != None:
            self.battle_callback()

class Inventory(Component):
    def __init__(self, size):
        self.items = [None for _ in range(size)]

    def getItem(self, index):
        """Get item from inventory.
        """
        return self.items[index]

    def addItem(self, itemToAdd):
        """Adds an item to the inventory.
        """
        for i, item in enumerate(self.items):
            if (isinstance(item, ItemInstance) and item.getType() == itemToAdd and item.canAddStack(itemToAdd)):
                item.changeStack(1)
                return True
            elif item == None:
                self.items[i] = ItemInstance(itemToAdd)
                return True
        return False
    
    def displayInventory(self):
        """Returns the display for the inventory.
        """
        to_return = ""
        for i, item in enumerate(self.items):
            if item != None:
                to_return += f"{i + 1}. {item.name} - {item.description}\n"
        return to_return
    
    def update(self, room, entity):
        """Handle the game update for the inventory component.
        """
        for i in range(len(self.items)):
            if isinstance(self.items[i], ItemInstance) and self.items[i].stack == 0:
                self.items[i] = None
    
    def death(self, room, entity):
        """Handle the entity death for the inventory component."""
        from .map import Interactable
        for item in self.items:
            if isinstance(item, ItemInstance):
                drop = Interactable(str(item), item.description, ["item"], ["get_item"], {
                    "item_type": item.getType().id,
                    "item_amount": item.stack
                })
                room.addInteractable(drop)

    @classmethod
    def fromDict(cls, data, game):
        """Create an Inventory component from a dictionary.
        """
        inventory = cls(0)
        if "items" in data:
            inventory.items = [
                ItemInstance.fromDict(item_instance, game.item_types) if item_instance != None else None for item_instance in data["items"]
            ]
        return inventory

    def toDict(self):
        """Convert an Inventory component to a dictionary.
        """
        return {"type": "inventory", "items": [item.toDict() if item != None else None for item in self.items]}


class AI(Component):
    def __init__(self, personality):
        self.personality = personality

    def update(self, room, entity):
        """Handle the game update for the AI component.
        """
        in_battle = entity.hasData("in_battle")
        if not in_battle:
            entities_in_room = (set(room.entities) - {entity}) | {entity.game.player}
            hostile = [
                entity_room
                for entity_room in entities_in_room
                if entity.isHostile(entity_room)
            ]
            priority_target = -1

            for i, hostile_creature in enumerate(hostile):
                if hostile_creature == entity.game.player:
                    priority_target = i
                    break
                else: 
                    priority_target = i

            if priority_target > -1:
                target = hostile[priority_target]
                if target.hasData("in_battle"):
                    entity.game.battle_manager.joinBattle(entity, target.getData("in_battle"))
                else:
                    id = entity.game.battle_manager.startBattle(room)
                    entity.game.battle_manager.joinBattle(entity, id)
                    if target == entity.game.player:
                        entity.game.addMenu("dungeon_combat")()
                    entity.game.battle_manager.joinBattle(target, id)
                    
        else:
            ...

    def battle(self, battle, entity, participants):
        """Handle battle update for the AI component.
        """
        #print("Battle Was Called")
        opponents = [
            participant for participant in participants if entity.isHostile(participant) and not participant.to_die
        ]
        allies = list(set(participants) - set(opponents))
        if len(opponents) == 0:
            entity.flee()
        else:
            # Complicated Evaluation stuff.
            flee_value = self.personality["flee"]["percent_of_missing_hp"] * (1 - entity.hp / entity.max_hp)
            self_heal_value = 0
            other_damage_value = 0
            heal_action = None
            damage_action = None
            target_index = 0
            for action in entity.actions:
                # Catagorize Action Type
                action_type = dummyFindActionType(entity, action)
                if action_type == "self_heal":
                    if not action.canApply([entity]):
                        continue
                    relevant_section = self.personality["heal"]["self"]["instant"]
                    heal_amount = dummyTestSelfHeal(entity, action)
                    self_heal_value += relevant_section["percent_of_total_hp"] * (heal_amount / entity.max_hp)
                    self_heal_value += relevant_section["percent_of_missing_hp"] * (heal_amount / (entity.max_hp - entity.hp)) if entity.max_hp != entity.hp else 0
                    self_heal_value += relevant_section["percent_of_remaining_hp"] * (heal_amount / entity.hp)
                    heal_action = action
                elif action_type == "other_heal":
                    ...
                elif action_type == "other_damage":
                    relevant_section = self.personality["attack"]["damage_to_target"]["instant"]
                    for i, opponent in enumerate(opponents):
                        if not action.canApply([entity, opponent]):
                            continue
                        cache = 0
                        damage_amount = dummyTestHurt([entity, opponent], action, 1)
                        cache += relevant_section["percent_of_total_hp"] * (damage_amount / opponent.max_hp)
                        cache += relevant_section["percent_of_remaining_hp"] * (damage_amount / opponent.hp)
                        if cache > other_damage_value:
                            damage_action = action
                            other_damage_value = cache
                            target_index = i
            greatest = max(flee_value, self_heal_value, other_damage_value)
            if greatest == flee_value:
                entity.flee()
                print(f"{entity.name} fled!")
            elif greatest == self_heal_value and heal_action != None:
                print(f"{entity.name} used {heal_action} and healed itself!")
                heal_action.apply([entity])
            elif greatest == other_damage_value and damage_action != None:
                print(f"{entity.name} used {damage_action} on {opponents[target_index].name} for {damage_amount} damage!")
                damage_action.apply([entity, opponents[target_index]])
            else:
                print("No actions?")

    @classmethod
    def fromDict(cls, data):
        """Create an AI component from a dictionary.
        """
        ai = cls(data["personality"])
        return ai

    def toDict(self):
        """Convert an AI component to a dictionary.
        """
        return {
            "type": "ai",
            "personality": self.personality
        }


def componentFromData(data, game):
    """Deserialize a component from a dictionary.
    """
    if "type" not in data:
        return None
    type = data["type"]
    if type == "inventory":
        return Inventory.fromDict(data, game)
    elif type == "ai":
        return AI.fromDict(data)
