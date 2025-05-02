from src.game import Game

def main():
    game = Game()

    running = True

    while running:
        game.update()

if __name__ == "__main__":
    main()