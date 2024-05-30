from typing import Dict, List

import pygame as pg
from pygame import Event, Surface

from state.impl.single_player_state import SinglePlayerState
from tetris.tetris_field import BlockType
from utils import settings


class MultiPlayerState(SinglePlayerState):

    def __init__(self, peer):
        super().__init__()
        from net.tetris_peer import TetrisPeer
        self.peer: TetrisPeer = peer
        self.is_dead: Dict[str, bool] = {}
        self.i_win = False
        self.peers_fields_sf: Dict[str, pg.Surface] = {}
        self.init_peers_fields_sf()

    def set_is_dead(self, player_name: str):
        self.is_dead[player_name] = True

    def init_is_dead(self, players: List[str]):
        self.is_dead = {player: False for player in players}

    def setup(self, seed=None):
        super().setup(seed)
        self.is_dead: Dict[str, bool] = {}
        self.i_win = False
        self.peers_fields_sf = {}
        self.init_peers_fields_sf()

    def handle_events(self, events: List[Event]) -> str | None:
        for event in events:
            if event.type == pg.QUIT:
                self.peer.broadcast_i_lose()

        if self.i_win or self.i_lose:
            self.peer.reset()
            return 'MENU'
        return super().handle_events(events)

    def on_change(self):
        # Do nothing because is set up by the peer
        pass

    def check_i_win(self):
        for is_dead in self.is_dead.values():
            if not is_dead:
                return
        self.i_win = True

    def hit_a_peer(self, count: int):
        self.peer.add_row_to_random_peer(count)

    def init_peers_fields_sf(self):
        for player_name, _ in self.peer.peers.items():
            self.peers_fields_sf[player_name] = pg.Surface((settings.TETRIS_FIELD_WIDTH * settings.PREVIEW_BLOCK_SIZE,
                                                            settings.TETRIS_FIELD_HEIGHT * settings.PREVIEW_BLOCK_SIZE))
            self.peers_fields_sf[player_name].fill(BlockType.NONE.value)

    def draw_peer_tetris_field(self, player_name: str, tetris_field: List[List[BlockType]]):
        field_sf = self.peers_fields_sf[player_name]
        self.draw_field(tetris_field, field_sf, is_preview=True)

    def update(self, delta_time: int):
        if not self.is_running:
            return
        self.tetris_field_sf.fill(BlockType.NONE.value)
        self.tetromino.update()
        self.check_i_win()
        if self.i_win:
            return
        if self.tetromino.is_dead:
            self.check_if_lose()
            if self.i_lose:
                self.peer.broadcast_i_lose()
                return
            self.add_tetronimo_to_field()
            count = self.tetris_field.remove_full_rows()
            self.hit_a_peer(count)
            self.level_progress(count)
            self.new_tetromino()
            self.peer.broadcast_set_tetris_field()
        self.draw_field(self.tetris_field.field, self.tetris_field_sf)
        self.draw_tetronimo()

    def render_peers_fields(self, screen: Surface):
        for i, sf in enumerate(self.peers_fields_sf.values()):
            row = i // 5
            col = i % 5
            spacing = (self.tetris_field_sf.get_width() + settings.BLOCK_SIZE + self.next_tetromino_sf.get_width()
                       + settings.BLOCK_SIZE)
            space = (settings.SCREEN_WIDTH - spacing) // 5
            padding_x = (space - settings.PREVIEW_BLOCK_SIZE * settings.TETRIS_FIELD_WIDTH) // 2
            space_y = settings.SCREEN_HEIGHT // 2
            padding_y = (space_y - settings.PREVIEW_BLOCK_SIZE * settings.TETRIS_FIELD_HEIGHT) // 2
            screen.blit(sf, (col * space + spacing + padding_x, row * space_y + padding_y))

    def render(self, screen: Surface):
        super().render(screen)
        self.render_peers_fields(screen)
