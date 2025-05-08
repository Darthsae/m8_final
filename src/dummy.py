import random

class DummyEntity:
    def __init__(self, entity_instance):
        self.game = entity_instance.game
        self.__entity_type = entity_instance.getType()
        self.name = entity_instance.name
        self.description = entity_instance.description
        self.tags = entity_instance.tags
        self.max_hp = entity_instance.max_hp
        self.hp = entity_instance.hp
        self.components = entity_instance.components
        self.actions = entity_instance.actions
        self.xp = entity_instance.xp
        self.speed = entity_instance.speed
        self.faction = entity_instance.faction
        self.data = entity_instance.data

    def hasFaction(self):
        return self.faction != ""

    def getFaction(self):
        return self.game.factions[self.faction]

    def isHostile(self, target):
        if self.hasFaction() and target.hasFaction():
            return target.faction in self.getFaction().hostile
        else:
            return False

    def update(self, room):
        for key in self.data:
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
        for component in self.components:
            component.battle(battle, self, opponents)

    def changeHP(self, amount, respect_cap):
        pre_hp = max(self.hp, self.max_hp)
        self.hp = max(self.hp + amount, 0)
        if respect_cap:
            self.hp = min(self.hp, pre_hp)
        if self.hp == 0:
            del self

    def addAction(self, action_type):
        from .ability import AbilityInstance
        self.actions.append(AbilityInstance(action_type))

    def hasData(self, key):
        return key in self.data

    def getData(self, key):
        return self.data[key][0]

    def addData(self, key, value, decay):
        self.data[key] = (value, decay)

    def removeData(self, key):
        self.data.pop(key)

def dummyFindActionType(entity, action):
    from .entity import EntityInstance
    targets = action.getType().targets
    if "consumer" in targets:
        if "creature" not in targets:
            return "self_heal"
        else:
            dummy_friendly = DummyEntity(EntityInstance(entity.game, EntityInstance.NULL_ENTITY_TYPE))
            dummy_friendly.faction = entity.faction
            dummy_friendly.hp -= 10
            old_hp_friendly = dummy_friendly.hp
            action.apply([entity, dummy_friendly])
            dummy_hostile = DummyEntity(EntityInstance(entity.game, EntityInstance.NULL_ENTITY_TYPE))
            dummy_hostile.faction = random.choice(entity.game.factions[entity.faction].hostile)
            old_hp_hostile = dummy_hostile.hp
            action.apply([entity, dummy_hostile])
            if old_hp_friendly < dummy_friendly.hp:
                return "other_heal"
            elif old_hp_hostile > dummy_hostile.hp:
                return "other_damage"

def dummyTestDeep(entity, action, targets):
    from .entity import EntityInstance
    new_targets = [DummyEntity(entity_data) if isinstance(entity_data, EntityInstance) else entity_data for entity_data in targets]
    action.apply(new_targets)
    