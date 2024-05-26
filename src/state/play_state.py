from random import Random
from typing import List, Tuple

import pygame as pg
from pygame import Surface, Event

import settings
from net.peer import Peer
from state.game_state import GameState
from tetris_field import TetrisField, BlockType
from tetromino import preload_tetrominos, Tetromino


class PlayState(GameState):
    def __init__(self, peer: Peer | None):
        preload_tetrominos()
        self.multiplayer = peer is not None
        self.peer = peer
        self.tetris_field_sf = pg.surface.Surface((settings.TETRIS_FIELD_WIDTH * settings.BLOCK_SIZE,
                                                   settings.TETRIS_FIELD_HEIGHT * settings.BLOCK_SIZE))
        pg.draw.rect(self.tetris_field_sf, 'black', (0, 0, settings.TETRIS_FIELD_WIDTH * settings.BLOCK_SIZE,
                                                     settings.TETRIS_FIELD_HEIGHT * settings.BLOCK_SIZE))

        self.seed = None
        self.rng = Random(self.seed)

        self.tetris_field = TetrisField()
        self.tetromino = self.random_tetromino()
        self.next_tetromino = self.random_tetromino()
        self.rotated = False

        self.next_tetromino_sf = pg.Surface((settings.BLOCK_SIZE * 5, settings.BLOCK_SIZE * 5))
        self.draw_next_tetronimo()

        self.level = 0
        self.to_next_level = settings.NEXT_LEVEL_GAP[self.level]
        self.i_lose = False
        self.i_win = False

    def on_change(self):
        self.rng = Random(self.seed)
        self.tetris_field = TetrisField()
        self.tetromino = self.random_tetromino()
        self.next_tetromino = self.random_tetromino()
        self.rotated = False
        self.draw_next_tetronimo()
        self.level = 0
        self.to_next_level = settings.NEXT_LEVEL_GAP[self.level]
        self.i_lose = False
        self.i_win = False

    def draw_next_tetronimo(self):
        self.next_tetromino_sf.fill(BlockType.NONE.value)
        shape = self.next_tetromino.shape
        color = self.next_tetromino.block_type.value
        tmp_sf = pg.Surface((shape.size * settings.BLOCK_SIZE, shape.size * settings.BLOCK_SIZE), pg.SRCALPHA)
        for i, row in enumerate(shape.matrix):
            for j, cell in enumerate(row):
                x = j * settings.BLOCK_SIZE
                y = i * settings.BLOCK_SIZE
                if cell:
                    pg.draw.rect(tmp_sf, color, (x, y, settings.BLOCK_SIZE, settings.BLOCK_SIZE), border_radius=5)
                    pg.draw.rect(tmp_sf, 'black', (x, y, settings.BLOCK_SIZE, settings.BLOCK_SIZE), 2,
                                 border_radius=5)

        x = (self.next_tetromino_sf.get_width() - tmp_sf.get_width()) / 2
        y = (self.next_tetromino_sf.get_height() - tmp_sf.get_height()) / 2
        self.next_tetromino_sf.blit(tmp_sf, (x, y))

    def draw_tetronimo(self):
        for i, row in enumerate(self.tetromino.shape.matrix):
            for j, cell in enumerate(row):
                x = (j + self.tetromino.pos.x) * settings.BLOCK_SIZE
                y = (i + self.tetromino.pos.y) * settings.BLOCK_SIZE
                y_shadow = (i + self.tetromino.shadow_pos.y) * settings.BLOCK_SIZE
                if cell:
                    color = self.tetromino.block_type.value
                    pg.draw.rect(self.tetris_field_sf, color,
                                 (x, y_shadow, settings.BLOCK_SIZE, settings.BLOCK_SIZE), 2, border_radius=5)
                    pg.draw.rect(self.tetris_field_sf, color, (x, y, settings.BLOCK_SIZE, settings.BLOCK_SIZE),
                                 border_radius=5)
                    pg.draw.rect(self.tetris_field_sf, 'black', (x, y, settings.BLOCK_SIZE, settings.BLOCK_SIZE),
                                 2,
                                 border_radius=5)

    def random_tetromino(self) -> Tetromino:
        block_type = BlockType.random_block()
        rotation = self.rng.randint(0, 3)
        return Tetromino(block_type, self.tetris_field, rotation=rotation)

    def handle_events(self, events: List[Event]) -> str | None:
        if self.i_lose:
            return 'MENU'
        for event in events:
            if event.type == pg.QUIT:
                return 'QUIT'

    def add_tetronimo_to_field(self):
        for i, row in enumerate(self.tetromino.shape.matrix):
            for j, cell in enumerate(row):
                x = int(j + self.tetromino.pos.x)
                y = int(i + self.tetromino.pos.y)
                if self.tetromino.shape.matrix[i][j]:
                    self.tetris_field.field[y][x] = self.tetromino.block_type

    @staticmethod
    def draw_field(field: [List[List[Tuple[int, int, int]]]], field_sf: pg.Surface, is_preview=False):
        block_size = settings.BLOCK_SIZE if not is_preview else settings.PREVIEW_BLOCK_SIZE
        for i, row in enumerate(field):
            for j, cell in enumerate(row):
                color = cell.value if not is_preview else cell
                x = j * block_size
                y = i * block_size
                radius = 0
                if color != BlockType.NONE.value:
                    radius = 5 if not is_preview else 1
                pg.draw.rect(field_sf, color, (x, y, settings.BLOCK_SIZE, settings.BLOCK_SIZE),
                             border_radius=radius)
                if color != BlockType.NONE.value:
                    width = 2 if not is_preview else 1
                    border_radius = 5 if not is_preview else 2
                    pg.draw.rect(field_sf, 'black',
                                 (x, y, settings.BLOCK_SIZE, settings.BLOCK_SIZE), width,
                                 border_radius=border_radius)

    def update(self, delta_time: int):
        if self.i_lose:
            return
        self.tetris_field_sf.fill(BlockType.NONE.value)
        self.tetromino.update()
        if self.tetromino.is_dead:
            if self.tetromino.pos.y < 0:
                print('you lose')
                self.i_lose = True
                return
            self.add_tetronimo_to_field()
            count = self.tetris_field.remove_full_rows()

            exceed = self.to_next_level - count
            self.to_next_level -= count

            if self.to_next_level <= 0:
                self.level = min(self.level + 1, len(settings.NEXT_LEVEL_GAP) - 1)
                self.to_next_level = settings.NEXT_LEVEL_GAP[self.level]
                self.to_next_level -= exceed

            self.tetromino = self.next_tetromino
            self.tetromino.set_level(self.level)
            self.next_tetromino = self.random_tetromino()
            self.draw_next_tetronimo()
        self.draw_field(self.tetris_field.field, self.tetris_field_sf)
        self.draw_tetronimo()

    def render(self, screen: Surface):
        screen.blit(self.tetris_field_sf, (0, 0))
        screen.blit(self.next_tetromino_sf, (self.tetris_field_sf.get_width() + settings.BLOCK_SIZE,
                                             settings.BLOCK_SIZE))
