import pygame as pg

from utils import settings
from utils.utils import rotate_matrix
from .shape import Shape
from .tetris_field import BlockType, TetrisField

TETROMINO_SHAPES = {
    BlockType.I_BLOCK: [Shape([
        [False, False, True, False],
        [False, False, True, False],
        [False, False, True, False],
        [False, False, True, False],
    ])],
    BlockType.J_BLOCK: [Shape([
        [False, True, False],
        [False, True, False],
        [True, True, False]
    ])],
    BlockType.L_BLOCK: [Shape([
        [False, True, False],
        [False, True, False],
        [False, True, True]
    ])],
    BlockType.O_BLOCK: [Shape([
        [True, True],
        [True, True],
    ])],
    BlockType.S_BLOCK: [Shape([
        [False, False, False],
        [False, True, True],
        [True, True, False],
    ])],
    BlockType.Z_BLOCK: [Shape([
        [True, True, False],
        [False, True, True],
        [False, False, False],
    ])],
    BlockType.T_BLOCK: [Shape([
        [False, False, False],
        [True, True, True],
        [False, True, False],
    ])]
}


def preload_tetrominos() -> None:
    for bt, shapes in TETROMINO_SHAPES.items():
        for _ in range(3):
            r_matrix = rotate_matrix(shapes[len(shapes) - 1].matrix)
            shapes.append(Shape(r_matrix))


class Tetromino:
    def __init__(self, block_type: BlockType, tetris_field: TetrisField, rotation: int = 0,
                 level: int = 0):
        super().__init__()
        self.block_type = block_type
        self.tetris_field = tetris_field
        self.rotation = rotation
        self.gravity_sleep = 0
        self.level = 0
        self.set_level(self.level)
        self.shape = TETROMINO_SHAPES[self.block_type][self.rotation]

        # Compute spawn point
        x = (settings.TETRIS_FIELD_WIDTH - self.shape.num_cols) // 2
        y = -self.shape.num_rows
        self.pos = pg.Vector2(x, y)

        self.gravity = self.gravity_sleep
        self.rotated = False
        self.gravity_drop = 1
        self.already_pressed = True

        self.das = settings.DAS
        self.is_dead = False

        self.shadow_pos = pg.Vector2()

    def set_level(self, level=0):
        self.level = min(level, len(settings.GRAVITY_SLEEP) - 1)
        self.gravity_sleep = settings.GRAVITY_SLEEP[self.level]

    def resolve_left_collisions(self) -> None:
        while (-self.pos.x) > self.shape.paddings['left'] or self.check_collision_blocks(self.pos):
            self.pos.x += 1

    def resolve_right_collisions(self) -> None:
        right_corner = self.pos.x + self.shape.num_cols
        while ((right_corner - settings.TETRIS_FIELD_WIDTH) > self.shape.paddings['right']
               or self.check_collision_blocks(self.pos)):
            self.pos.x -= 1
            right_corner -= 1

    def resolve_horizontal_collisions(self) -> None:
        self.resolve_left_collisions()
        self.resolve_right_collisions()

    def resolve_bottom_collisions(self) -> None:
        bottom_corner = self.pos.y + self.shape.num_rows
        collisions = self.check_collision_blocks(self.pos)
        if (bottom_corner - settings.TETRIS_FIELD_HEIGHT) > self.shape.paddings['bottom'] or collisions:
            self.pos.y -= 1
            self.is_dead = True

    def go_left(self) -> None:
        self.pos.x -= 1
        self.resolve_left_collisions()

    def go_right(self) -> None:
        self.pos.x += 1
        self.resolve_right_collisions()

    def go_down(self) -> None:
        self.pos.y += 1
        self.resolve_bottom_collisions()

    def rotate(self) -> None:
        old_rotation = self.rotation
        self.rotation = (self.rotation + 1) % 4
        self.shape = TETROMINO_SHAPES[self.block_type][self.rotation]

        if self.check_collision_blocks(self.pos):
            self.rotation = old_rotation
            self.shape = TETROMINO_SHAPES[self.block_type][self.rotation]
            return

        self.resolve_horizontal_collisions()
        self.resolve_bottom_collisions()

    def place_shadow(self) -> None:
        self.shadow_pos = self.pos.copy()
        while True:
            self.shadow_pos.y += 1
            bottom_corner = self.shadow_pos.y + self.shape.num_rows
            collisions = self.check_collision_blocks(self.shadow_pos)
            if (bottom_corner - settings.TETRIS_FIELD_HEIGHT) > self.shape.paddings['bottom'] or collisions:
                self.shadow_pos.y -= 1
                break

    def check_collision_blocks(self, pos: pg.Vector2):
        for i, row in enumerate(self.shape.matrix):
            for j, cell in enumerate(row):
                if not self.shape.matrix[i][j]:
                    continue
                row_f = int(i + pos.y)
                col_f = int(j + pos.x)
                if (col_f < 0 or col_f >= settings.TETRIS_FIELD_WIDTH
                        or row_f < 0 or row_f >= settings.TETRIS_FIELD_HEIGHT):
                    continue
                if self.tetris_field.field[row_f][col_f] != BlockType.NONE:
                    return True
        return False

    def hard_drop(self):
        while not self.is_dead:
            self.go_down()
        self.is_dead = True

    def manage_lateral_input(self, pressed_left: bool, pressed_right: bool):
        if pressed_left:
            if self.das == settings.DAS:
                self.go_left()
            self.das -= 1
        elif pressed_right:
            if self.das == settings.DAS:
                self.go_right()
            self.das -= 1
        else:
            self.das = settings.DAS

    def manage_drop(self, pressed_down: bool):
        if pressed_down:
            self.gravity_drop = settings.SOFT_DROP_WEIGHT
        else:
            self.gravity_drop = 1

    def manage_rotation(self, pressed_up: bool):
        if pressed_up and not self.rotated:
            self.rotate()
            self.rotated = True
        elif not pressed_up:
            self.rotated = False

    def manage_hard_drop(self, pressed_space: bool):
        if pressed_space and not self.already_pressed:
            self.hard_drop()
        elif not pressed_space:
            self.already_pressed = False

    def get_input(self) -> None:
        if self.is_dead:
            return
        pressed = pg.key.get_pressed()
        self.manage_lateral_input(pressed[pg.K_LEFT], pressed[pg.K_RIGHT])
        self.manage_drop(pressed[pg.K_DOWN])
        self.manage_rotation(pressed[pg.K_UP])
        self.manage_hard_drop(pressed[pg.K_SPACE])

    def update(self) -> None:
        self.get_input()

        if self.das < 0:
            self.das = settings.DAS

        self.gravity -= self.gravity_drop
        if self.gravity < 0:
            self.gravity = self.gravity_sleep
            self.go_down()

        self.place_shadow()
