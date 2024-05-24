from enum import Enum

import settings

class BlockType(Enum):
    NONE = (149, 97, 226)
    L_BLOCK = (227, 52, 47)
    J_BLOCK = (246, 153, 63)
    I_BLOCK = (255, 237, 74)
    O_BLOCK = (56, 193, 114)
    S_BLOCK = (77, 192, 181)
    T_BLOCK = (52, 144, 220)
    Z_BLOCK = (246, 109, 155)
    WALL_BLOCK = (101, 116, 205)

    @staticmethod
    def random_block():
        return settings.rng.choice([
            BlockType.L_BLOCK,
            BlockType.J_BLOCK,
            BlockType.I_BLOCK,
            BlockType.O_BLOCK,
            BlockType.S_BLOCK,
            BlockType.T_BLOCK,
            BlockType.Z_BLOCK,
        ])


class TetrisField:
    def __init__(self):
        super().__init__()
        self.field = [[BlockType.NONE for _ in range(settings.TETRIS_FIELD_WIDTH)]
                      for _ in range(settings.TETRIS_FIELD_HEIGHT)]

    def clean_row(self, row_index: int):
        while row_index > 0:
            self.field[row_index] = self.field[row_index - 1]
            row_index -= 1
        self.field[0] = [BlockType.NONE for _ in range(settings.TETRIS_FIELD_WIDTH)]

    def is_full_row(self, row_index: int):
        for i, cell in enumerate(self.field[row_index]):
            if cell == BlockType.NONE:
                return False
        return True

    def is_empty_row(self, row_index: int):
        for i, cell in enumerate(self.field[row_index]):
            if cell != BlockType.NONE:
                return False
        return True

    def remove_full_rows(self) -> int:
        count = 0
        i = len(self.field) - 1
        while i >= 0:
            if self.is_full_row(i):
                self.clean_row(i)
                i += 1
                count += 1
            i -= 1
        return count

    def add_rows(self, num_rows: int) -> bool:
        lose = not self.is_empty_row(0)
        hole_index = settings.rng.randint(0, settings.TETRIS_FIELD_WIDTH - 1)
        for i in range(settings.TETRIS_FIELD_HEIGHT - num_rows):
            self.field[i] = self.field[i + num_rows]

        for i in range(settings.TETRIS_FIELD_HEIGHT - num_rows, settings.TETRIS_FIELD_HEIGHT):
            self.field[i] = [
                BlockType.WALL_BLOCK if i != hole_index else BlockType.NONE for i in range(settings.TETRIS_FIELD_WIDTH)
            ]
        return lose


