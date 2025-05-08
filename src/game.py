from .entity import EntityInstance, EntityType
from .faction import Faction
from .map import Map, RoomType, RoomPool, SpawnPool
from .util import intput
from .menu import MenuType, MenuInstance
from .components import Inventory
from .classes import ClassType
from .item import ItemType
from .ability import AbilityType
from .battle import BattleManager
import os, json


# region Menu Callbacks
def noFunction():
    pass


def mainMenuDisplay():
    width = min(os.get_terminal_size().columns, 64)
    print("--==::<[Dungeon Crawler]>::==--".center(width) + "\n")
    print("A CLI Roguelike by D.O.".center(width) + "\n\n\n")


def concatenateFunctions(functions):
    def toReturn():
        for function in functions:
            function()

    return toReturn


def generateDisplayString(to_print):
    def toReturn():
        print(to_print)

    return toReturn


def generateDisplayDict(iterable):
    def toReturn():
        for i, (key, value) in enumerate(iterable().items()):
            print(f"{i + 1} - {key}: {value}")

    return toReturn


def generateDisplayIterable(iterable):
    def toReturn():
        for value in iterable():
            print(f"{value}")

    return toReturn


def generateOptionMenuDisplay(options):
    def toReturn():
        for i, option in enumerate(options):
            print(f"{i + 1}) {option}")

    return toReturn


def generateOptionMenuInput(options):
    def toReturn():
        choice = intput("Choice: ") - 1
        if 0 <= choice < len(options):
            options[choice]()
        else:
            print("Invalid Selection")

    return toReturn


def passAddedValueToCallback(modifier, callback):
    def toReturn(value):
        callback(value + modifier)

    return toReturn


def passInputToCallback(prompt, type, callback):
    def toReturn():
        callback(type(input(prompt)))

    return toReturn


def remapValueToAnother(key_value_map, default):
    def toReturn(key):
        return key_value_map.get(key, default)

    return toReturn


def remapAndCallback(remap_function, callback):
    def toReturn(key):
        callback(remap_function(key))

    return toReturn


# endregion


class Game:
    def __init__(self):
        self.player = EntityInstance(self, EntityInstance.NULL_ENTITY_TYPE)
        self.__mods = {}
        self.factions = {"player": Faction("player", "Player", [])}
        self.entity_types = {}
        self.item_types = {}
        self.class_types = {}
        self.ability_types = {}
        self.map = Map()
        self.battle_manager = BattleManager()
        self.menu_stack = []
        self.menu_cache = {}

        self.menus = {}
        self.rebuildMenus()

        self.addMenu("main_menu")()

        self.getMods()
        self.player_x = 0
        self.player_y = 0

    def rebuildMenus(self):
        self.menus = {
            "main_menu": MenuType(
                concatenateFunctions(
                    [
                        mainMenuDisplay,
                        generateOptionMenuDisplay(
                            ["New Game", "Saves", "Mods", "Exit"]
                        ),
                    ]
                ),
                generateOptionMenuInput(
                    [self.newGame, self.addMenu("saves"), self.addMenu("mods"), quit]
                ),
            ),
            "name_character": MenuType(
                noFunction,
                concatenateFunctions(
                    [
                        passInputToCallback(
                            "Name of Character: ",
                            str,
                            self.saveDataToCache("character_name"),
                        ),
                        self.popMenu,
                        self.addMenu("choose_class"),
                    ]
                ),
            ),
            "choose_class": MenuType(
                concatenateFunctions(
                    [
                        generateDisplayString("\nClasses"),
                        generateDisplayDict(self.getClassTypes),
                    ]
                ),
                concatenateFunctions(
                    [
                        passInputToCallback(
                            "Class of Character: ",
                            int,
                            remapAndCallback(
                                remapValueToAnother(
                                    {
                                        i + 1: class_type
                                        for i, class_type in enumerate(
                                            list(self.class_types)
                                        )
                                    },
                                    -1,
                                ),
                                self.saveDataToCache("character_class"),
                            ),
                        ),
                        self.createCharacter,
                        self.popMenu,
                        self.addMenu("dungeon_exploration"),
                    ]
                ),
            ),
            "mods": MenuType(
                concatenateFunctions(
                    [
                        generateDisplayString("\nMods"),
                        generateDisplayDict(self.mods),
                        generateDisplayString(""),
                        generateOptionMenuDisplay(["Enable/Disable", "Back"]),
                    ]
                ),
                generateOptionMenuInput(
                    [
                        passInputToCallback(
                            "Mod: ", int, passAddedValueToCallback(-1, self.swapEnable)
                        ),
                        concatenateFunctions([self.reloadWithActiveMods, self.popMenu]),
                    ]
                ),
            ),
            "dungeon_exploration": MenuType(
                self.displayDungeonExploration, self.inputDungeonExploration
            ),
            "dungeon_combat": MenuType(
                self.displayDungeonCombat, 
                self.inputDungeonCombat
            ),
            "creature_inspect": MenuType(
                self.displayListCreatures, 
                self.inputListCreatures
            ),
            "action_select": MenuType(
                self.displayListActions, 
                self.inputListActions
            ),
            "item_select": MenuType(
                self.displayListItems, 
                self.inputListItems
            ),
        }

    def createCharacter(self):
        self.player.name = self.popDataFromCache("character_name")()
        self.player.max_hp = 100
        self.player.hp = 100
        self.player.components.append(Inventory(12))
        self.player.gainClassLevel(
            self.class_types[self.popDataFromCache("character_class")()],
            self.ability_types,
        )
        self.player.faction = "player"
        self.map.setRoom(0, 0, "starting_room")

    def mods(self):
        return self.__mods

    def update(self):
        self.menu_stack[-1].displayMenu()
        self.menu_stack[-1].inputMenu()

    def newGame(self):
        self.addMenu("name_character")()

    def getClassTypes(self):
        return self.class_types

    def getMods(self):
        for file in os.scandir("mods"):
            if file.is_dir() and os.path.exists(file.path + "/mod.json"):
                self.__mods[file.name] = False

    def reloadWithActiveMods(self):
        mods = [f"mods/{key}" for key, value in self.__mods.items() if value]
        for mod in mods:
            self.loadMod(mod)
        self.rebuildMenus()

    def loadMod(self, path):
        for file in os.scandir(path):
            if file.is_dir and file.name in [
                "classes",
                "entities",
                "items",
                "rooms",
                "abilities",
                "spawn_pools",
                "room_pools",
                "factions",
            ]:
                if file.name == "classes":
                    print("Classes is present.")
                    for class_json in os.scandir(path + "/classes"):
                        if class_json.is_file() and class_json.name[-5:] == ".json":
                            with open(class_json.path, "r") as f:
                                self.class_types[class_json.name[:-5]] = (
                                    ClassType.fromDict(self, class_json.name[:-5], json.load(f))
                                )
                elif file.name == "entities":
                    print("Entities is present.")
                    for entity_json in os.scandir(path + "/entities"):
                        if entity_json.is_file() and entity_json.name[-5:] == ".json":
                            with open(entity_json.path, "r") as f:
                                self.entity_types[entity_json.name[:-5]] = (
                                    EntityType.fromDict(
                                        entity_json.name[:-5], json.load(f)
                                    )
                                )
                elif file.name == "items":
                    print("Items is present.")
                    for item_json in os.scandir(path + "/items"):
                        if item_json.is_file() and item_json.name[-5:] == ".json":
                            with open(item_json.path, "r") as f:
                                self.item_types[item_json.name[:-5]] = (
                                    ItemType.fromDict(item_json.name[:-5], json.load(f))
                                )
                elif file.name == "rooms":
                    print("Rooms is present.")
                    for room_json in os.scandir(path + "/rooms"):
                        if room_json.is_file() and room_json.name[-5:] == ".json":
                            with open(room_json.path, "r") as f:
                                self.map.room_types[room_json.name[:-5]] = (
                                    RoomType.fromDict(room_json.name[:-5], json.load(f))
                                )
                elif file.name == "abilities":
                    print("Abilities is present.")
                    for ability_json in os.scandir(path + "/abilities"):
                        if ability_json.is_file() and ability_json.name[-5:] == ".json":
                            with open(ability_json.path, "r") as f:
                                self.ability_types[ability_json.name[:-5]] = (
                                    AbilityType.fromDict(
                                        self, ability_json.name[:-5], json.load(f)
                                    )
                                )
                elif file.name == "room_pools":
                    print("Room Pools is present.")
                    for room_pool_json in os.scandir(path + "/room_pools"):
                        if (
                            room_pool_json.is_file()
                            and room_pool_json.name[-5:] == ".json"
                        ):
                            with open(room_pool_json.path, "r") as f:
                                self.map.addRoomPool(
                                    RoomPool.fromDict(
                                        self, room_pool_json.name[:-5], json.load(f)
                                    )
                                )
                elif file.name == "factions":
                    print("Factions is present.")
                    for faction_json in os.scandir(path + "/factions"):
                        if faction_json.is_file() and faction_json.name[-5:] == ".json":
                            with open(faction_json.path, "r") as f:
                                self.factions[faction_json.name[:-5]] = (
                                    Faction.fromDict(
                                        faction_json.name[:-5], json.load(f)
                                    )
                                )
                elif file.name == "spawn_pools":
                    print("Spawn Pools is present.")
                    for spawn_pool_json in os.scandir(path + "/spawn_pools"):
                        if (
                            spawn_pool_json.is_file()
                            and spawn_pool_json.name[-5:] == ".json"
                        ):
                            with open(spawn_pool_json.path, "r") as f:
                                self.map.spawn_pool_types[spawn_pool_json.name[:-5]] = (
                                    SpawnPool.fromDict(
                                        self, spawn_pool_json.name[:-5], json.load(f)
                                    )
                                )

    def swapEnable(self, index):
        key = list(self.__mods.keys())[index]
        self.__mods[key] = not self.__mods[key]

    def addMenu(self, menu_name):
        def toReturn():
            self.menu_stack.append(MenuInstance(self.menus[menu_name]))

        return toReturn

    def saveDataToCache(self, name):
        def toReturn(value):
            self.menu_cache[name] = value

        return toReturn

    def retrieveDataFromCache(self, name):
        def toReturn():
            return self.menu_cache[name]

        return toReturn

    def popDataFromCache(self, name):
        def toReturn():
            return self.menu_cache.pop(name)

        return toReturn
    
    def hasDataInCache(self, name):
        def toReturn():
            return name in self.menu_cache
        
        return toReturn

    def clearData(self):
        self.player = EntityInstance(self, EntityInstance.NULL_ENTITY_TYPE)
        self.map.reset()

    def popMenu(self):
        self.menu_stack.pop()

    def displayDungeonCombat(self):
        if not self.hasDataInCache("waiting_for_turn")() or not self.retrieveDataFromCache("waiting_for_turn")():
            self.battle_manager.updateBattles(self)
        self.saveDataToCache("waiting_for_turn")(True)
        print("1) Inspect Creature")
        print("2) Take Action")
        print("3) Use Item")

    def inputDungeonCombat(self): 
        option = intput("Option: ") - 1
        if option == 0:
            self.addMenu("creature_inspect")()
        elif option == 1:
            self.addMenu("action_select")()
        elif option == 2:
            self.addMenu("item_select")()

    def displayDungeonExploration(self):
        print(self.player.name)
        print(self.player.getClassesDisplayString())
    
    def inputListCreatures(self):
        creatures = self.battle_manager.battles[self.player.getData("in_battle")].participants
        choice = intput("Choice: ") - 1
        if choice == len(creatures):
            self.popMenu()
        elif 0 <= choice < len(creatures):
            print(creatures[choice].detailedBattleDescription())
            self.popDataFromCache("waiting_for_turn")()
            input()
            self.popMenu()

    def displayListCreatures(self):
        creatures = self.battle_manager.battles[self.player.getData("in_battle")].participants
        for i, creature in enumerate(creatures):
            print(f"{i + 1}) {creature.name}")
        print(str(len(creatures) + 1) + ") Back")

    def inputListActions(self):
        ...
    
    def displayListActions(self):
        ...

    def inputListItems(self):
        ...
    
    def displayListItems(self):
        ...

    def inputDungeonExploration(self):
        command = input().split()

        if len(command) == 0:
            return

        command_key = command[0]

        if command_key == "saves":
            self.addMenu("")()
        elif command_key == "quit":
            self.popMenu()
            self.clearData()
        elif command_key == "look":
            room = self.map.getRoom(self.player_x, self.player_y)
            print(room.getDescription())
        elif command_key == "interact":
            room = self.map.getRoom(self.player_x, self.player_y)
            if len(command) < 2:
                print("You need to add what to interact with.")
            interaction = command[1]
            for interactable in room.interactables:
                if interactable.name == interaction:
                    print()
        elif command_key == "move":
            room = self.map.getRoom(self.player_x, self.player_y)
            if len(command) < 2:
                print("Add a direction to move in.")
            direction = command[1]
            if direction == "north":
                self.player_y += 1
            elif direction == "south":
                self.player_y -= 1
            elif direction == "east":
                self.player_x += 1
            elif direction == "west":
                self.player_x -= 1
            room = self.map.getRoom(self.player_x, self.player_y)
            print(room.getDescription())

        room = self.map.getRoom(self.player_x, self.player_y)
        room.update()

    @classmethod
    def fromDict(cls, data):
        return cls(**data)

    def toDict(self):
        return {}
