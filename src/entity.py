from .classes import ClassInstance
from .components import componentFromData
from .ability import AbilityInstance


class EntityType:
    def __init__(self, id, name, description, tags, hp, xp, speed):
        self.id = id
        self.name = name
        self.description = description
        self.tags = tags
        self.hp = hp
        self.components = []
        self.actions = []
        self.classes = []
        self.xp = xp
        self.speed = speed

    @classmethod
    def fromDict(cls, id, data):
        """Load an entity type from a dictionary.
        """
        entity_type = cls(
            id,
            data["name"],
            data["description"],
            data["tags"],
            data["hp"],
            data["xp"],
            data["speed"],
        )
        return entity_type


class EntityInstance:
    NULL_ENTITY_TYPE = EntityType("", "", "", [], 1, 0, 0)

    def __init__(self, game, entity_type):
        self.game = game
        self.__entity_type = entity_type
        self.name = self.__entity_type.name
        self.description = self.__entity_type.description
        self.tags = self.__entity_type.tags
        self.max_hp = self.__entity_type.hp
        self.hp = self.__entity_type.hp
        self.components = self.__entity_type.components.copy()
        self.actions = []
        self.__classes = []
        self.xp = self.__entity_type.xp
        self.speed = self.__entity_type.speed
        self.faction = ""
        self.data = {}
        self.to_die = False

    def getDescription(self):
        """Return the description of the entity.
        """
        return " ".join(["There is a", self.name, "in the room."])

    def getClassesDisplayString(self):
        """Return classes display string.
        """
        string = ""
        for class_data in self.__classes:
            string += class_data.getType().name + " " + str(class_data.level + 1) + "\n"
        return string
    
    def getClassesLineString(self):
        """Return classes display string for inline display.
        """
        string = ", ".join([f"{class_data.getType().name} {class_data.level + 1}" for class_data in self.__classes])
        return string

    def hasFaction(self):
        """Check if entity has a faction.
        """
        return self.faction != ""

    def getFaction(self):
        """Get the faction of the entity.
        """
        return self.game.factions[self.faction]

    def isHostile(self, target):
        """Check if entity is hostile to another.
        """
        if self.hasFaction() and target.hasFaction():
            return target.faction in self.getFaction().hostile
        else:
            return False

    def addXP(self, amount):
        """Add xp to the entity.
        """
        self.xp += amount

    def update(self, room):
        """Handle game update for entity.
        """
        for key in list(self.data.keys()):
            value = self.data.pop(key)
            if value[1] == 0:
                pass
            elif value[1] == -1:
                self.data[key] = value
            else:
                self.data[key] = (value[0], value[1] - 1)
        for component in self.components:
            component.update(room, self)

    def battleUpdate(self, battle, opponents):
        """Handle battle update for entity.
        """
        for component in self.components:
            component.battle(battle, self, opponents)

    def levelInClass(self, class_type):
        """Get entities current level in a class type, -1 for none.
        """
        for class_instance in self.__classes:
            if class_instance.getType() == class_type:
                return class_instance.level
        return -1
    
    def nextXPInClass(self, class_type):
        """Get the next amount of xp to get another level in a class.
        """
        for class_instance in self.__classes:
            if class_instance.getType() == class_type:
                return class_type.level_data[class_instance.level + 1].xp_cost if class_instance.level + 1 < class_type.maxLevel() else -1
        return class_type.level_data[0].xp_cost

    def gainClassLevel(self, class_type, ability_types):
        """Gain one leve in a class for the entity.
        """
        for class_instance in self.__classes:
            if class_instance.getType() == class_type:
                level = class_instance.level + 1
                if level == class_type.maxLevel():
                    return
                else:
                    class_type.level_data[level].applyTo(self, ability_types)
                    class_instance.level += 1
                    return
        class_instance = ClassInstance(class_type, 0)
        class_type.level_data[0].applyTo(self, ability_types)
        self.__classes.append(class_instance)

    def changeHP(self, amount, respect_cap):
        """Change the entities hp, respecting cap if specified.
        """
        pre_hp = max(self.hp, self.max_hp)
        self.hp = max(self.hp + amount, 0)
        if respect_cap:
            self.hp = min(self.hp, pre_hp)
        if self.hp == 0:
            self.to_die = True
            return True

    def addAction(self, action_type):
        """Add an action to the entity.
        """
        self.actions.append(AbilityInstance(action_type))
    
    def hasAction(self, action_type):
        """Check if entity has an action of a type.
        """
        for action in self.actions:
            if action.getType() == action_type:
                return True
        return False
    
    def battleLoad(self):
        """Battle load, called after loading battle manager to prevent crashes.
        """
        if self.hasData("in_battle"):
            self.game.battle_manager.joinBattle(self, self.getData("in_battle"))

    def flee(self):
        """Have the entity leave a battle if it is in one.
        """
        if self.hasData("in_battle"):
            self.game.battle_manager.leaveBattle(self, self.getData("in_battle"))

    def changeRoom(self, x, y): 
        """Deprecated.
        """
        ...

    def death(self, room):
        """Handles the entity dying in a room.
        """
        for component in self.components:
            component.death(room, self)

    def hasData(self, key):
        """Check if entity has data of a key.
        """
        return key in self.data

    def getData(self, key):
        """Get data from the entity.
        """
        return self.data[key][0]

    def addData(self, key, value, decay):
        """Add data to the entity with decay, -1 for no decay.
        """
        self.data[key] = (value, decay)

    def removeData(self, key):
        """Remove data from the entity.
        """
        self.data.pop(key)

    def detailedBattleDescription(self):
        """Return the detailed battle description of the entity.
        """
        to_return = f"{self.name} ({self.faction}) - {self.getClassesLineString()}\n"
        to_return += f"HP: {self.hp}/{self.max_hp}\n"
        to_return += f"XP: {self.xp}\n"
        to_return += f"SPEED: {self.speed}\n"
        to_return += self.description
        return to_return
    
    def getType(self):
        """Get the entity type of the entity.
        """
        return self.__entity_type

    @classmethod
    def fromDict(cls, data, game):
        """Deserialize an entity from a dictionary and create an instance.
        """
        entity = cls(game, game.entity_types[data["type"]] if data["type"] != "" else EntityInstance.NULL_ENTITY_TYPE)
        if "name" in data:
            entity.name = data["name"]
        if "description" in data:
            entity.description = data["description"]
        if "tags" in data:
            entity.tags = data["tags"]
        if "max_hp" in data:
            entity.max_hp = data["max_hp"]
        if "hp" in data:
            entity.hp = data["hp"]
        if "xp" in data:
            entity.xp = data["xp"]
        if "speed" in data:
            entity.speed = data["speed"]
        if "components" in data:
            entity.components = [
                componentFromData(component_data, game)
                for component_data in data["components"]
            ]
        if "actions" in data:
            for action in data["actions"]:
                entity.addAction(game.ability_types[action])
        if "classes" in data:
            entity.__classes = [
                ClassInstance.fromDict(class_data, game.class_types) for class_data in data["classes"]
            ]
        if "faction" in data:
            entity.faction = data["faction"]
        if "data" in data:
            entity.data = data["data"]
        return entity

    def toDict(self):
        """Serialize entity to dictionary.
        """
        return {
            "type": self.__entity_type.id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "max_hp": self.max_hp,
            "hp": self.hp,
            "xp": self.xp,
            "speed": self.speed,
            "components": [
                component_data.toDict() for component_data in self.components
            ],
            "actions": [action_data.getType().id for action_data in self.actions],
            "classes": [class_data.toDict() for class_data in self.__classes],
            "faction": self.faction,
            "data": self.data,
        }

