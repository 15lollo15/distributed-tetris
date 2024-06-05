import sys

from game import Game


def main(argv: list[str]):
    if len(argv) > 1:
        game = Game(argv[1])
    else:
        game = Game('player')
    game.run()


if __name__ == '__main__':
    main(sys.argv)
