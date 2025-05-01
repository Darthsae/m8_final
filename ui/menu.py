class MenuType:
    def __init__(self):
        self.options = {}

class MenuInstance:
    def __init__(self, menu_type):
        self.__menu_type = menu_type
    
    def getType(self):
        return self.__menu_type