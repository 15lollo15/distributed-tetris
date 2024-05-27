import sys

from game import Game

# TODO: Close app

def main(argv: list[str]):
    if 'host' in argv:
        game = Game('host')
        game.state_manager.change_state('MENU')
        game.run()
    else:
        game = Game('client-3')
        game.state_manager.change_state('BROWSE_LOBBY')
        game.run()


if __name__ == '__main__':
    main(sys.argv)
