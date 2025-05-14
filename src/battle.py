from .util import longToString
import time

class BattleManager:
    def __init__(self):
        self.battles = {}
    
    def startBattle(self, room):
        """Starts a battle in a room.
        """
        id = longToString(time.time_ns())
        self.battles[id] = BattleInstance(id, room)
        return id
    
    def joinBattle(self, entity, id):
        """Join a battle with an entity by the battles id.
        """
        if id in self.battles:
            self.battles[id].participants.append(entity)
            entity.addData("in_battle", id, -1)

    def leaveBattle(self, entity, id):
        """Leave the battle for an entity with the battle id.
        """
        if id in self.battles and entity in self.battles[id].participants:
            self.battles[id].participants.remove(entity)
            entity.removeData("in_battle")
    
    def updateBattles(self, game):
        """Update all battles in the game.
        """
        to_nuke = set()
        for key, battle in self.battles.items():
            battle.runUpdate()

            if battle.isOver():
                to_nuke.add(key)

        # TODO: Check for any invalid battles and end them.
        for key in to_nuke:
            self.battles.pop(key)
    
    @classmethod
    def fromDict(cls, data, game):
        """Get the state of the battle manager from a dictionary.
        """
        battle_manager = cls()
        battle_manager.battles = {key: BattleInstance.fromDict(value, game) for key, value in data["battles"].items()}
        return battle_manager

    def toDict(self):
        """Turn the state of the battle manager into a dictionary.
        """
        return {
            "battles": {key: battle.toDict() for key, battle in self.battles.items()}
        }

class BattleInstance:
    def __init__(self, id, room):
        self.id = id
        self.room = room
        self.participants = []
    
    def runUpdate(self):
        """Run the update for the battle.
        """
        def idk(entity):
            """I just needed a wrapper for this since I couldn't use lambdas. This returns the speed of an entity.
            """
            return entity.speed
        organized_participants = sorted(self.participants, key=idk, reverse=True)
        for participant in organized_participants:
            if participant in self.participants:
                participant.battleUpdate(self, [participant_thing for participant_thing in self.participants if not participant_thing is participant])
    
    def isOver(self):
        """Returns if the battle is over.
        """
        return len(self.participants) == 0
    
    @classmethod
    def fromDict(cls, data, game):
        """Create a battle from a dictionary.
        """
        battle = cls(data["id"], game.map.getRoom(data["room_x"], data["room_y"]))
        return battle
    
    def toDict(self):
        """Turns a battle into a dictionary.
        """
        return {
            "id": self.id,
            "room_x": self.room.position_x,
            "room_y": self.room.position_y
        }
