from random import Random
from typing import Dict, List

import Pyro4
import pygame as pg
from pygame import Surface

import settings
from net.peer import Peer
from state.single_player_state import SinglePlayerState
from tetris_field import BlockType


class MultiPlayerState(SinglePlayerState):

    def __init__(self, peer: Peer | None):
        super().__init__(peer=peer)
        self.peer = peer
        self.seed = self.peer.seed
        self.rng = Random(self.seed)

        self.peers_fields = {}
        self.peers_fields_sf = {}
        self.is_dead: Dict[str, bool] = {}

        self.init_is_dead()
        self.init_peers_fields()
        self.init_peers_fields_sf()

        self.peer.multiplayer_instance = self
        self.is_read_to_play = True
        self.all_ready = False

    def on_change(self):
        super().on_change()
        self.seed = self.peer.seed
        self.rng = Random(self.seed)
        print('seed: ' + str(self.seed))

        self.peers_fields = {}
        self.peers_fields_sf = {}
        self.is_dead = {}

        self.init_is_dead()
        self.init_peers_fields()
        self.init_peers_fields_sf()

        self.peer.multiplayer_instance = self
        self.all_ready = False
        self.is_read_to_play = True

    def init_is_dead(self):
        for player_name, _ in self.peer.peers.items():
            self.is_dead[player_name] = False

    def init_peers_fields(self):
        for player_name, _ in self.peer.peers.items():
            if player_name == self.peer.player_name:
                continue
            self.peers_fields_sf[player_name] = pg.Surface((settings.TETRIS_FIELD_WIDTH * settings.PREVIEW_BLOCK_SIZE,
                                                            settings.TETRIS_FIELD_HEIGHT * settings.PREVIEW_BLOCK_SIZE))

    def init_peers_fields_sf(self):
        for player_name, _ in self.peer.peers.items():
            if player_name == self.peer.player_name:
                continue
            self.peers_fields[player_name] = [[BlockType.NONE.value for __ in range(settings.TETRIS_FIELD_WIDTH)] for _
                                              in
                                              range(settings.TETRIS_FIELD_HEIGHT)]

    def draw_peers_tetris_fields(self):
        for player_name, field in list(self.peers_fields.items()):
            if field is None:
                continue
            field_sf = self.peers_fields_sf[player_name]
            self.draw_field(field, field_sf, is_preview=True)

    def check_i_win(self):
        for player_name, is_dead in list(self.is_dead.items()):
            if player_name == self.peer.player_name:
                continue
            if not is_dead:
                return
        if not self.i_lose:
            self.i_win = True

    def get_alive(self) -> List[Pyro4.Proxy]:
        return [self.peer.peers[player_name] for player_name, is_dead in self.is_dead.items() if not is_dead]

    def update(self, delta_time: int):
        if not self.is_running:
            return

        if not self.all_ready:
            self.all_ready = self.peer.all_ready()
            return

        if self.i_win:
            print('you win')
            for peer in self.peer.peers.values():
                peer.set_winner(self.peer.player_name)
            self.is_running = False
            return

        self.tetris_field_sf.fill(BlockType.NONE.value)
        self.check_i_win()
        self.tetromino.update()
        if self.tetromino.is_dead:
            if self.tetromino.pos.y < 0:
                print('you lose')
                self.i_lose = True
                for peer in self.peer.peers.values():
                    peer.set_is_dead(self.peer.player_name)
                self.is_running = False
                return
            self.add_tetronimo_to_field()
            count = self.tetris_field.remove_full_rows()

            if count > 0:
                enemy_peer = settings.rng.choice(self.get_alive())
                enemy_peer.add_rows(count)
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

            for _, peer in self.peer.peers.items():
                peer.set_tetris_field(self.peer.player_name, self.tetris_field.field)

        self.draw_field(self.tetris_field.field, self.tetris_field_sf)
        self.draw_tetronimo()
        self.draw_peers_tetris_fields()

    def render(self, screen: Surface):
        super().render(screen)
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
