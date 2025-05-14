# Playable RPG.
# 5/14/2025
# CSC-121 m8Final
# Daley Ottersbach
from src.game import Game

# This is over 2000 lines of code.
# I would get an anuerism trying to make pseudocode for all of that.

def main():
    """The main function.
    """
    game = Game()

    running = True

    while running:
        game.update()

if __name__ == "__main__":
    main()