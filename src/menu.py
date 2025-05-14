class MenuType:
    def __init__(self, display_callback, input_callback):
        self.display_callback = display_callback
        self.input_callback = input_callback

class MenuInstance:
    def __init__(self, menu_type):
        self.__menu_type = menu_type
    
    def displayMenu(self):
        """Displays the menu.
        """
        self.__menu_type.display_callback()
    
    def inputMenu(self):
        """Handles the input for the menu.
        """
        self.__menu_type.input_callback()
    
    def getType(self):
        """Returns the Menu Type of the menu.
        """
        return self.__menu_type