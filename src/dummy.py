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
        self.components = entity_instance.components.copy()
        self.actions = entity_instance.actions
        self.xp = entity_instance.xp
        self.speed = entity_instance.speed
        self.faction = entity_instance.faction
        self.data = entity_instance.data.copy()

    def hasFaction(self):
        """Check if dummy has a faction.
        """
        return self.faction != ""

    def getFaction(self):
        """Get the faction of the dummy.
        """
        return self.game.factions[self.faction]

    def isHostile(self, target):
        """Check if dummy is hostile to another.
        """
        if self.hasFaction() and target.hasFaction():
            return target.faction in self.getFaction().hostile
        else:
            return False

    def update(self, room):
        """Handle game update for dummy.
        """
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
        """Handle battle update for dummy.
        """
        for component in self.components:
            component.battle(battle, self, opponents)

    def changeHP(self, amount, respect_cap):
        """Change the dummies hp, respecting cap if specified.
        """
        pre_hp = max(self.hp, self.max_hp)
        self.hp = max(self.hp + amount, 0)
        if respect_cap:
            self.hp = min(self.hp, pre_hp)
        if self.hp == 0:
            del self

    def addAction(self, action_type):
        """Add an action to the dummy.
        """
        from .ability import AbilityInstance
        self.actions.append(AbilityInstance(action_type))

    def hasData(self, key):
        """Check if dummy has data of a key.
        """
        return key in self.data

    def getData(self, key):
        """Get data from the dummy.
        """
        return self.data[key][0]

    def addData(self, key, value, decay):
        """Add data to the dummy with decay, -1 for no decay.
        """
        self.data[key] = (value, decay)

    def removeData(self, key):
        """Remove data from the dummy.
        """
        self.data.pop(key)

def dummyFindActionType(entity, action):
    """Determine the type of action.
    """
    from .entity import EntityInstance
    targets = action.getType().targets
    if "consumer" in targets:
        if "creature" not in targets:
            return "self_heal"
        else:
            dummy_self = DummyEntity(entity)
            dummy_friendly = DummyEntity(EntityInstance(entity.game, EntityInstance.NULL_ENTITY_TYPE))
            dummy_friendly.max_hp = 100
            dummy_friendly.hp = 90
            dummy_friendly.faction = entity.faction
            old_hp_friendly = dummy_friendly.hp
            action.apply([dummy_self, dummy_friendly])
            dummy_hostile = DummyEntity(EntityInstance(entity.game, EntityInstance.NULL_ENTITY_TYPE))
            dummy_hostile.max_hp = 100
            dummy_hostile.hp = 100
            dummy_hostile.faction = random.choice(entity.game.factions[entity.faction].hostile)
            old_hp_hostile = dummy_hostile.hp
            action.apply([dummy_self, dummy_hostile])
            if old_hp_friendly < dummy_friendly.hp:
                return "other_heal"
            elif old_hp_hostile > dummy_hostile.hp:
                return "other_damage"

def dummyTestDeep(entity, action, targets):
    """Deprecated"""
    from .entity import EntityInstance
    new_targets = [DummyEntity(entity_data) if isinstance(entity_data, EntityInstance) else entity_data for entity_data in targets]
    action.apply(new_targets)

def dummyTestSelfHeal(entity, action):
    """Test the healing effects of an action.
    """
    targets = [DummyEntity(entity)]
    pre_hp = targets[0].hp
    action.apply(targets)
    post_hp = targets[0].hp
    return post_hp - pre_hp
    
def dummyTestHurt(targets, action, target):
    """Test the harming effects of an action."""
    from .entity import EntityInstance
    new_targets = [DummyEntity(entity_data) if isinstance(entity_data, EntityInstance) else entity_data for entity_data in targets]
    pre_hp = new_targets[target].hp
    action.apply(new_targets)
    post_hp = new_targets[target].hp
    return pre_hp - post_hp
    