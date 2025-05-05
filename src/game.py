from .entity import EntityInstance, EntityType
from .faction import Faction
from .map import Map, RoomType
from .util import intput
from .menu import MenuType, MenuInstance
from .components import Inventory
from .classes import ClassType
from .item import ItemType
from .ability import AbilityType
import os, json

#region Menu Callbacks
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
#endregion


class Game:
    def __init__(self):
        self.player = EntityInstance(EntityInstance.NULL_ENTITY_TYPE)
        self.__mods = {}
        self.factions = {"player": Faction("Player", [])}
        self.entity_types = {}
        self.room_types = {}
        self.item_types = {}
        self.class_types = {}
        self.ability_types = {}
        self.map = Map()
        self.menu_stack = []
        self.menu_cache = {}
        
        self.menus = {}
        self.rebuildMenus()

        self.addMenu("main_menu")()

        self.getMods()

    def rebuildMenus(self):
        self.menus = {
            "main_menu": MenuType(
                concatenateFunctions([
                    mainMenuDisplay, 
                    generateOptionMenuDisplay([
                        "New Game",
                        "Saves",
                        "Mods",
                        "Exit"
                    ])
                ]), 
                generateOptionMenuInput([
                    self.newGame,
                    self.addMenu("saves"),
                    self.addMenu("mods"),
                    quit
                ])),
            "name_character": MenuType(
                noFunction,
                concatenateFunctions([
                    passInputToCallback("Name of Character: ", str, self.saveDataToCache("character_name")),
                    self.popMenu,
                    self.addMenu("choose_class")
                ])),
            "choose_class": MenuType(
                concatenateFunctions([
                    generateDisplayString("\nClasses"),
                    generateDisplayDict(self.getClassTypes)
                ]),
                concatenateFunctions([
                    passInputToCallback("Class of Character: ", int, remapAndCallback(
                        remapValueToAnother({i + 1: class_type for i, class_type in enumerate(list(self.class_types))}, -1), 
                        self.saveDataToCache("character_class")
                    )),
                    self.createCharacter,
                    self.popMenu,
                    self.addMenu("dungeon_exploration")
                ])),
            "mods": MenuType(
                concatenateFunctions([
                    generateDisplayString("\nMods"),
                    generateDisplayDict(self.mods),
                    generateDisplayString(""),
                    generateOptionMenuDisplay([
                        "Enable/Disable",
                        "Back"
                    ])
                ]),
                generateOptionMenuInput([
                    passInputToCallback("Mod: ", int, passAddedValueToCallback(-1, self.swapEnable)),
                    concatenateFunctions([
                        self.reloadWithActiveMods,
                        self.popMenu
                    ])
                ])),
            "dungeon_exploration": MenuType(
                self.displayDungeonExploration,
                self.inputDungeonExploration
            )
        }

    def createCharacter(self):
        self.player.name = self.popDataFromCache("character_name")()
        self.player.max_hp = 100
        self.player.hp = 100
        self.player.components.append(Inventory(12))
        self.player.gainClassLevel(self.class_types[self.popDataFromCache("character_class")()], self.ability_types)

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
            if file.is_dir and file.name in ["classes", "entities", "items", "rooms", "abilities"]:
                if file.name == "classes":
                    print("Classes is present.")
                    for class_json in os.scandir(path + "/classes"):
                        if class_json.is_file() and class_json.name[-5:] == ".json":
                            with open(class_json.path, "r") as f:
                                self.class_types[class_json.name[:-5]] = ClassType.fromDict(class_json.name[:-5], json.load(f))
                elif file.name == "entities":
                    print("Entities is present.")
                    for entity_json in os.scandir(path + "/entities"):
                        if entity_json.is_file() and entity_json.name[-5:] == ".json":
                            with open(entity_json.path, "r") as f:
                                self.entity_types[entity_json.name[:-5]] = EntityType.fromDict(entity_json.name[:-5], json.load(f))
                elif file.name == "items":
                    print("Items is present.")
                    for item_json in os.scandir(path + "/items"):
                        if item_json.is_file() and item_json.name[-5:] == ".json":
                            with open(item_json.path, "r") as f:
                                self.item_types[item_json.name[:-5]] = ItemType.fromDict(item_json.name[:-5], json.load(f))
                elif file.name == "rooms":
                    print("Rooms is present.")
                    for room_json in os.scandir(path + "/rooms"):
                        if room_json.is_file() and room_json.name[-5:] == ".json":
                            with open(room_json.path, "r") as f:
                                self.room_types[room_json.name[:-5]] = RoomType.fromDict(room_json.name[:-5], json.load(f))
                elif file.name == "abilities":
                    print("Abilities is present.")
                    for ability_json in os.scandir(path + "/abilities"):
                        if ability_json.is_file() and ability_json.name[-5:] == ".json":
                            with open(ability_json.path, "r") as f:
                                self.ability_types[ability_json.name[:-5]] = AbilityType.fromDict(ability_json.name[:-5], json.load(f))

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
    
    def clearData(self):
        self.player = EntityInstance(EntityInstance.NULL_ENTITY_TYPE)
        self.map = Map()

    def popMenu(self):
        self.menu_stack.pop()

    def displayDungeonExploration(self):
        print(self.player.name)
        print(self.player.getClassesDisplayString())

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
    
    @classmethod
    def fromDict(cls, data):
        return cls(**data)
    
    def toDict(self):
        return {}
