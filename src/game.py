from .entity import EntityInstance, EntityType
from .faction import Faction
from .map import Map, RoomType, RoomPool, SpawnPool
from .util import intput
from .menu import MenuType, MenuInstance
from .components import Inventory, FunctionHolder
from .classes import ClassType
from .item import ItemType
from .ability import AbilityType, AbilityInstance
from .battle import BattleManager
from .dummy import dummyFindActionType, dummyTestHurt, dummyTestSelfHeal
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
        self.reloadWithActiveMods()
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
                concatenateFunctions([
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
                ]),
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
            "target_select": MenuType(
                self.displayTargets,
                self.inputTargets
            ),
            "character_sheet": MenuType(
                self.displayCharacterSheet,
                self.inputCharacterSheet
            ),
            "character_level": MenuType(
                self.displayCharacterLevel,
                self.inputCharacterLevel
            ),
            "character_level_view": MenuType(
                self.displayCharacterLevelView,
                self.inputCharacterLevelView
            ),
            "inspect_item": MenuType(
                self.displayInspectItem,
                self.inputInspectItem
            )
        }

    def displayCharacterSheet(self):
        print(self.player.detailedBattleDescription())
        print("Inventory: ")
        index_of_inventory = 0
        for i, component in enumerate(self.player.components):
            if isinstance(component, Inventory):
                index_of_inventory = i
        just = len(str(len(self.player.components[index_of_inventory].items)))
        for i, item in enumerate(self.player.components[index_of_inventory].items):
            print(f"{str(i + 1).rjust(just)}. {item} - {item.description if item != None else None}")
        print("\nAbilities: ")
        just = len(str(len(self.player.actions)))
        for i, ability in enumerate(self.player.actions):
            print(f"{str(i + 1).rjust(just)}. {ability.getType().name} - {ability.getType().description}")
        print()
        print("1) Inspect Item")
        print("2) Level Class")
        print("3) Back\n")

    def inputCharacterSheet(self):
        option = intput("Option: ") - 1
        if option == 0:
            item_index = intput("Item Number: ") - 1
            self.addMenu("inspect_item")()
            self.saveDataToCache("item_index")(item_index)
        elif option == 1:
            self.addMenu("character_level")()
        elif option == 2:
            self.popMenu()

    def displayCharacterLevel(self):
        print("\nClasses: ")
        just = len(str(len(self.class_types)))
        for i, class_data in enumerate(self.class_types.values()):
            print(f"{str(i + 1).rjust(just)}) {class_data.name}")
        print(str(len(self.class_types) + 1).rjust(just) + ") Back\n")

    def inputCharacterLevel(self):
        choice = intput("Choice: ") - 1
        if choice == len(self.class_types):
            self.popMenu()
        elif 0 <= choice < len(self.class_types):
            self.saveDataToCache("class_type")(list(self.class_types.keys())[choice])
            self.addMenu("character_level_view")()

    def displayInspectItem(self):
        for component in self.player.components:
            if isinstance(component, Inventory):
                item = component.getItem(self.retrieveDataFromCache("item_index")())
                print()
                print(f"{item.name} ({item.stack}/{item.max_stack})")
                print("[" + ", ".join(map(str.capitalize, item.tags)) + "]\n")
                print(item.description)
                print()
                print("1) Uses")
                print("2) Back\n")
                return

    def inputInspectItem(self):
        choice = intput("Choice: ") - 1
        if choice == 0:
            for component in self.player.components:
                if isinstance(component, Inventory):
                    item = component.getItem(self.retrieveDataFromCache("item_index")())
                    uses = [AbilityInstance(self.ability_types[data]) for data in item.getType().uses]
                    just = len(str(len(uses)))
                    for i, use in enumerate(uses):
                        print(f"{str(i + 1).rjust(just)}) {use.getType().name} - {use.getType().description}")
                    print(f"{str(len(uses) + 1).rjust(just)}) Back\n")
                    while True:
                        choice = intput("Option: ") - 1
                        if choice == len(uses):
                            break
                        elif 0 <= choice < len(uses):
                            if not uses[choice].canApply([self.player, item]):
                                print("You can not use that item like that right now.\n")
                            else:
                                uses[choice].apply([self.player, item])
                                if item.stack == 0:
                                    component.items[self.popDataFromCache("item_index")()] = None
                                    self.popMenu()
                                break
        elif choice == 1:
            self.popDataFromCache("item_index")()
            self.popMenu()

    def displayCharacterLevelView(self):
        class_doota = self.class_types[self.retrieveDataFromCache("class_type")()]
        print(f"{class_doota.name} ({self.player.levelInClass(class_doota) + 1}/{class_doota.maxLevel()})")
        print(f"{class_doota.description}")
        print()
        print(f"1) Take Level ({self.player.nextXPInClass(class_doota)} XP)")
        print("2) Back\n")

    def inputCharacterLevelView(self):
        option = intput("Option: ") - 1
        if option == 0: 
            class_doota = self.class_types[self.retrieveDataFromCache("class_type")()]
            xp_cost = self.player.nextXPInClass(class_doota)
            if xp_cost == -1:
                print("You are already max level.\n")
            elif self.player.xp < xp_cost:
                print("You lack the neccessary XP to take a level in this class.\n")
            else:
                self.player.xp -= xp_cost
                self.player.gainClassLevel(class_doota, self.ability_types)
                print(f"You have gained one level in {class_doota.name}.\n")
                input()
                self.popMenu()
        elif option == 1:
            self.popMenu()

    def createCharacter(self):
        self.player.name = self.popDataFromCache("character_name")()
        self.player.max_hp = 100
        self.player.hp = 100
        self.player.components.append(Inventory(12))
        self.player.components.append(FunctionHolder(None, self.combatMenu))
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
                with open(file.path + "/mod.json", "r") as f:
                    mod_data = json.load(f)
                    if "default_to_on" in mod_data:
                        self.__mods[file.name] = mod_data["default_to_on"]

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
                                data_f = json.load(f)
                                self.factions[faction_json.name[:-5]] = (Faction.fromDict(faction_json.name[:-5], data_f))
                                if "player" in data_f["hostile"]:
                                    self.factions["player"].hostile.append(faction_json.name[:-5])
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
            room = self.map.getRoom(self.player_x, self.player_y)
            room.update()
            self.battle_manager.updateBattles(self)

    def inputDungeonCombat(self): 
        if self.player.to_die:
            self.popMenu()
            self.popMenu()
            self.clearData()
            return
        
        if not self.player.hasData("in_battle"):
            self.popMenu()
            return

    def combatMenu(self):
        self.saveDataToCache("waiting_for_turn")(True)
        while self.hasDataInCache("waiting_for_turn")():
            if self.menu_stack[-1].getType() == self.menus["dungeon_combat"]:
                room = self.map.getRoom(self.player_x, self.player_y)
                print("\n" + room.getDescription())
                print()
                print("1) Inspect Creature")
                print("2) Take Action")
                print("3) Use Item")
                print("4) Flee\n")
                option = intput("Option: ") - 1
                if option == 0:
                    self.addMenu("creature_inspect")()
                elif option == 1:
                    self.addMenu("action_select")()
                elif option == 2:
                    self.addMenu("item_select")()
                elif option == 3:
                    self.player.flee()
                    self.popDataFromCache("waiting_for_turn")()
            else:
                self.menu_stack[-1].displayMenu()
                self.menu_stack[-1].inputMenu()

    def displayDungeonExploration(self):
        print()
    
    def inputListCreatures(self):
        creatures = self.battle_manager.battles[self.player.getData("in_battle")].participants
        choice = intput("Choice: ") - 1
        if choice == len(creatures):
            self.popMenu()
        elif 0 <= choice < len(creatures):
            print(creatures[choice].detailedBattleDescription())
            input()
            self.popMenu()

    def displayListCreatures(self):
        creatures = self.battle_manager.battles[self.player.getData("in_battle")].participants
        just = len(str(len(creatures)))
        for i, creature in enumerate(creatures):
            print(f"{str(i + 1).rjust(just)}) {creature.name}")
        print(str(len(creatures) + 1).rjust(just) + ") Back\n")

    def inputListActions(self):
        actions = self.player.actions
        choice = intput("Choice: ") - 1
        #print(f"0 <= {choice} < {len(actions)} - {0 <= choice < len(actions)}")
        if choice == len(actions):
            self.popMenu()
        elif 0 <= choice < len(actions):
            action = self.player.actions[choice]
            action_type = dummyFindActionType(self.player, action)
            #print(action_type)
            if action_type == "self_heal":
                if not action.canApply([self.player]):
                    print("You can not use that action right now.\n")
                    return
                action.apply([self.player])
                self.popDataFromCache("waiting_for_turn")()
                input()
                self.popMenu()
            elif action_type in ["other_heal", "other_damage"]:
                self.saveDataToCache("ability_index")(choice)
                self.addMenu("target_select")()
            else:
                if not action.canApply([self.player]):
                    print("You can not use that action right now.\n")
                    return
                action.apply([self.player])
                self.popDataFromCache("waiting_for_turn")()
                input()
                self.popMenu()
    
    def displayListActions(self):
        just = len(str(len(self.player.actions)))
        for i, action in enumerate(self.player.actions):
            print(f"{str(i + 1).rjust(just)}) {action}")
        print(f"{str(len(self.player.actions) + 1).rjust(just)}) Back\n")

    def inputListItems(self):
        index_of_inventory = 0
        for i, component in enumerate(self.player.components):
            if isinstance(component, Inventory):
                index_of_inventory = i
        
        items = self.player.components[index_of_inventory].items
        choice = intput("Choice: ") - 1
        if choice == len(items):
            self.popMenu()
        elif 0 <= choice < len(items):
            stack = items[choice]
            if stack == None or len(stack.getType().uses) <= 0:
                print("That item has no uses.\n")
                return
            index = 0
            uses = [AbilityInstance(self.ability_types[data]) for data in stack.getType().uses]
            for i, use in enumerate(uses):
                print(f"{i + 1}) {use.getType().name} - {use.getType().description}")
            print(f"{len(uses) + 1}) Back\n")
            while True:
                choice = intput("Option: ") - 1
                if choice == len(uses):
                    break
                elif 0 <= choice < len(uses):
                    self.saveDataToCache("item_ability")(stack.getType().uses[index])
                    action = AbilityInstance(self.ability_types[self.retrieveDataFromCache("item_ability")()])
                    if "creature" in action.getType().targets:
                        self.saveDataToCache("item_index")(choice)
                        self.addMenu("target_select")()
                        break
                    else:
                        if not action.canApply([self.player, stack]):
                            print("You can not use that action right now.\n")
                            continue
                        action.apply([self.player, stack])
                        if stack.stack == 0:
                            items[choice] = None
                        print()
                        print(f"{self.player.name} used {stack.name}.")
                        print()
                        self.popDataFromCache("item_ability")
                        self.popDataFromCache("waiting_for_turn")()
                        self.popMenu()
                        break
            
    
    def displayListItems(self):
        index_of_inventory = 0
        for i, component in enumerate(self.player.components):
            if isinstance(component, Inventory):
                index_of_inventory = i

        just = len(str(len(self.player.components[index_of_inventory].items)))
        for i, item in enumerate(self.player.components[index_of_inventory].items):
            if item != None:
                print(f"{str(i + 1).rjust(just)}) {item}")
        print(f"{str(len(self.player.components[index_of_inventory].items) + 1).rjust(just)}) Back\n")
    
    def inputTargets(self):
        creatures = self.battle_manager.battles[self.player.getData("in_battle")].participants
        choice = intput("Choice: ") - 1
        if choice == len(creatures):
            self.popMenu()
        elif 0 <= choice < len(creatures):
            if self.hasDataInCache("ability_index")():
                ability = self.player.actions[self.popDataFromCache("ability_index")()]
                if not ability.canApply([self.player, creatures[choice]]):
                    print("You can not use that action on that target right now.\n")
                    return
                calc = creatures[choice].hp
                ability.apply([self.player, creatures[choice]])
                calc -= creatures[choice].hp
                self.popDataFromCache("waiting_for_turn")()
                print()
                print(f"{self.player.name} used {ability.getType().name} on {creatures[choice].name} for {calc} damage.")
                self.popMenu()
                self.popMenu()
            elif self.hasDataInCache("item_index")():
                ability = AbilityInstance(self.ability_types[self.popDataFromCache("item_ability")()])
                index_of_inventory = 0
                for i, component in enumerate(self.player.components):
                    if isinstance(component, Inventory):
                        index_of_inventory = i
                stack = self.player.components[index_of_inventory].items[self.popDataFromCache("item_index")()]
                if not ability.canApply([self.player, stack, creatures[choice]]):
                    print("You can not use that action on that target right now.\n")
                    return
                calc = creatures[choice].hp
                ability.apply([self.player, stack, creatures[choice]])
                calc -= creatures[choice].hp
                self.popDataFromCache("waiting_for_turn")()
                print()
                print(f"{self.player.name} used {ability.getType().name} on {creatures[choice].name} for {calc} damage.")
                self.popMenu()
                self.popMenu()
    
    def displayTargets(self):
        creatures = self.battle_manager.battles[self.player.getData("in_battle")].participants
        just = len(str(len(creatures)))
        for i, creature in enumerate(creatures):
            print(f"{str(i + 1).rjust(just)}) {creature.name} - ")
        print(str(len(creatures) + 1).rjust(just) + ") Back\n")

    def inputDungeonExploration(self):
        if self.player.to_die:
            self.popMenu()
            self.clearData()
            return
        
        room = self.map.getRoom(self.player_x, self.player_y)
        print("\n" + room.getDescription())
        
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
                print("You need to add what to interact with.\n")
            else:
                interaction = command[1]
                for interactable in room.interactables:
                    if interactable.name == interaction:
                        interactions = [AbilityInstance(self.ability_types[data]) for data in interactable.uses]
                        just = len(str(len(interactions)))
                        for i, interaction in enumerate(interactions):
                            print(f"{str(i + 1).rjust(just)}) {interaction.getType().name} - {interaction.getType().description}")
                        print(f"{str(len(interactions) + 1).rjust(just)}) Back\n")
                        while True:
                            choice = intput("Option: ") - 1
                            if choice == len(interactions):
                                break
                            elif 0 <= choice < len(interactions):
                                if not interactions[choice].canApply([self.player, interactable, room]):
                                    print("You can not do that interaction right now.\n")
                                else:
                                    interactions[choice].apply([self.player, interactable, room])
                                    break
        elif command_key == "move":
            room = self.map.getRoom(self.player_x, self.player_y)
            if len(command) < 2:
                print("Add a direction to move in.\n")
            else:
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
                if room == None: 
                    if direction == "north":
                        self.player_y += -1
                    elif direction == "south":
                        self.player_y -= -1
                    elif direction == "east":
                        self.player_x += -1
                    elif direction == "west":
                        self.player_x -= -1
        elif command_key == "character":
            self.addMenu("character_sheet")()

        room = self.map.getRoom(self.player_x, self.player_y)
        room.update()
        self.battle_manager.updateBattles(self)

    @classmethod
    def fromDict(cls, data):
        return cls(**data)

    def toDict(self):
        return {}
