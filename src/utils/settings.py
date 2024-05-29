from random import Random

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (1700, 800)
FRAME_RATE = 60

TETRIS_FIELD_SIZE = TETRIS_FIELD_WIDTH, TETRIS_FIELD_HEIGHT = (10, 20)
BLOCK_SIZE = 40

PREVIEW_BLOCK_SIZE = 15

GRAVITY_SLEEP = [48, 43, 38, 33, 28, 23, 18, 13, 8, 6]
GRAVITY_SLEEP.extend([5 for _ in range(3)])
GRAVITY_SLEEP.extend([4 for _ in range(3)])
GRAVITY_SLEEP.extend([3 for _ in range(3)])
GRAVITY_SLEEP.extend([2 for _ in range(10)])
GRAVITY_SLEEP.append(1)

MAX_LEVEL = len(GRAVITY_SLEEP) - 1

DAS = 6
SOFT_DROP_WEIGHT = 2

SPAWN_SLEEP = 10

NEXT_LEVEL_GAP = [(i + 1) * 10 for i in range(10)]
NEXT_LEVEL_GAP.extend([100 for _ in range(5)])
NEXT_LEVEL_GAP.extend([(100 + (i + 1) * 10) for i in range(10)])
NEXT_LEVEL_GAP.extend([200 for _ in range(3)])

rng = Random(15)

MAX_PLAYERS = 10
