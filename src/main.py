import sys

from game import Game


def main(argv: list[str]):
    if 'host' in argv:
        game = Game('host')
        game.run()
    else:
        game = Game('client-2')
        game.run()


if __name__ == '__main__':
    main(sys.argv)
