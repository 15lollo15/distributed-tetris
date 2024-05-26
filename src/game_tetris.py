import threading
from random import Random
from typing import List, Tuple

import Pyro4
import pygame as pg
import select

import settings
from tetris_field import TetrisField, BlockType
from tetromino import preload_tetrominos, Tetromino


class Game:
    def __init__(self, multiplayer=False, is_server=False):
        pg.init()
        preload_tetrominos()
        self.multiplayer = multiplayer
        self.is_server = is_server
        self.screen = pg.display.set_mode(settings.SCREEN_SIZE)
        self.clock = pg.time.Clock()
        self.is_running = False
        self.tetris_field_sf = pg.surface.Surface((settings.TETRIS_FIELD_WIDTH * settings.BLOCK_SIZE,
                                                   settings.TETRIS_FIELD_HEIGHT * settings.BLOCK_SIZE))
        pg.draw.rect(self.tetris_field_sf, 'black', (0, 0, settings.TETRIS_FIELD_WIDTH * settings.BLOCK_SIZE,
                                                     settings.TETRIS_FIELD_HEIGHT * settings.BLOCK_SIZE))

        self.seed = None

        self.daemon = None
        self.connected_peer_uris = []
        self.server = None
        self.uri = None
        self.peers = []
        self.is_completed = False
        self.peers_fields = {}
        self.peers_fields_sf = {}
        self.is_dead = {}
        self.winner = None
        if multiplayer:
            self.multiplayer_init()

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

        self.run()

    def init_peers_fields(self):
        for uri in self.connected_peer_uris:
            if uri == self.uri:
                continue
            self.peers_fields_sf[uri] = pg.Surface((settings.TETRIS_FIELD_WIDTH * settings.PREVIEW_BLOCK_SIZE,
                                                    settings.TETRIS_FIELD_HEIGHT * settings.PREVIEW_BLOCK_SIZE))

    def init_peers_uris(self):
        for uri in self.connected_peer_uris:
            p = Pyro4.Proxy(uri)
            self.peers.append(p)
        self.connected_peer_uris.append(self.uri)

    def init_peers_fields_sf(self):
        for uri in self.connected_peer_uris:
            if uri == self.uri:
                continue
            self.peers_fields[uri] = [[BlockType.NONE.value for __ in range(settings.TETRIS_FIELD_WIDTH)] for _ in
                                      range(settings.TETRIS_FIELD_HEIGHT)]

    def setup_peers(self):
        for peer in self.peers:
            peer.set_connected_peer_uris(self.connected_peer_uris)
            peer.set_seed(self.seed)

    def server_init(self):
        ns = Pyro4.locateNS()
        ns.register("server", self.uri)
        while len(self.connected_peer_uris) < 2:
            self.manage_remote_events()
        self.is_completed = True
        self.init_peers_uris()
        self.setup_peers()

    def client_ready(self):
        return len(self.connected_peer_uris) != 1 and self.seed is not None

    def client_init(self):
        self.server = Pyro4.Proxy('PYRONAME:server')
        self.server.connect(self.uri)
        self.connected_peer_uris.append('PYRONAME:server')
        while not self.client_ready():
            self.manage_remote_events()

    def init_is_dead(self):
        for uri in self.connected_peer_uris:
            self.is_dead[uri] = False

    def multiplayer_init(self):
        self.seed = settings.rng.random()
        self.daemon = Pyro4.Daemon()
        self.uri = self.daemon.register(self)
        print("MY_URI: " + str(self.uri))
        if self.is_server:
            self.server_init()
        else:
            self.client_init()
        self.init_peers_fields()
        self.init_peers_fields_sf()
        self.init_is_dead()

    def manage_remote_events_loop(self):
        while self.is_running:
            self.manage_remote_events()

    def manage_remote_events(self):
        s, _, _ = select.select(self.daemon.sockets, [], [], 0.01)
        if s:
            self.daemon.events(s)

    @Pyro4.expose
    def connect(self, uri):
        if not self.is_server or self.is_completed:
            return
        self.connected_peer_uris.append(uri)

    @Pyro4.expose
    def set_connected_peer_uris(self, uris: List):
        uris.remove(self.uri)
        self.connected_peer_uris = uris
        for uri in self.connected_peer_uris:
            p = Pyro4.Proxy(uri)
            self.peers.append(p)

    @Pyro4.expose
    @Pyro4.oneway
    def set_tetris_field(self, uri, field):
        self.peers_fields[uri] = field

    @Pyro4.expose
    @Pyro4.oneway
    def add_rows(self, num_rows: int):
        self.tetris_field.add_rows(num_rows)
        for peer in self.peers:
            peer.set_tetris_field(self.uri, self.tetris_field.field)

    @Pyro4.expose
    @Pyro4.oneway
    def set_seed(self, seed):
        self.seed = seed

    @Pyro4.expose
    @Pyro4.oneway
    def set_is_dead(self, uri):
        self.is_dead[uri] = True
        self.check_i_win()

    @Pyro4.expose
    def set_winner(self, uri):
        self.winner = uri
        self.is_running = False

    def check_i_win(self):
        for uri, is_dead in list(self.is_dead.items()):
            if uri == self.uri:
                continue
            if not is_dead:
                return
        if not self.i_lose:
            self.i_win = True

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

    def random_tetromino(self):
        block_type = BlockType.random_block()
        rotation = self.rng.randint(0, 3)
        return Tetromino(block_type, self.tetris_field, rotation=rotation)

    def manage_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False

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

    def add_tetronimo_to_field(self):
        for i, row in enumerate(self.tetromino.shape.matrix):
            for j, cell in enumerate(row):
                x = int(j + self.tetromino.pos.x)
                y = int(i + self.tetromino.pos.y)
                if self.tetromino.shape.matrix[i][j]:
                    self.tetris_field.field[y][x] = self.tetromino.block_type

    def draw_peers_tetris_fields(self):
        for uri, field in list(self.peers_fields.items()):
            if field is None:
                continue
            field_sf = self.peers_fields_sf[uri]
            self.draw_field(field, field_sf, is_preview=True)

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

    def run(self):
        print('started')
        self.is_running = True
        t = threading.Thread(target=self.manage_remote_events_loop)
        t.start()
        while self.is_running:
            self.clock.tick(settings.FRAME_RATE)
            pg.display.set_caption(str(self.clock.get_fps()))
            if self.i_lose:
                continue
            elif self.i_win:
                for peer in self.peers:
                    peer.set_winner(self.uri)
                self.is_running = False
                break
            self.tetris_field_sf.fill(BlockType.NONE.value)
            self.manage_events()
            self.check_i_win()
            self.tetromino.update()
            if self.tetromino.is_dead:
                if self.tetromino.pos.y < 0:
                    print('you lose')
                    self.i_lose = True
                    for peer in self.peers:
                        peer.set_is_dead(self.uri)
                    continue
                self.add_tetronimo_to_field()
                count = self.tetris_field.remove_full_rows()

                if count > 0 and self.multiplayer:
                    enemy_peer = settings.rng.choice(self.peers)
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

                if self.multiplayer:
                    for peer in self.peers:
                        peer.set_tetris_field(self.uri, self.tetris_field.field)

            self.draw_field(self.tetris_field.field, self.tetris_field_sf)
            self.draw_tetronimo()

            self.screen.blit(self.tetris_field_sf, (0, 0))
            self.screen.blit(self.next_tetromino_sf, (self.tetris_field_sf.get_width() + settings.BLOCK_SIZE,
                                                      settings.BLOCK_SIZE))

            self.draw_peers_tetris_fields()
            for i, sf in enumerate(self.peers_fields_sf.values()):
                row = i // 5
                col = i % 5
                spacing = (self.tetris_field_sf.get_width() + settings.BLOCK_SIZE + self.next_tetromino_sf.get_width()
                           + settings.BLOCK_SIZE)
                space = (settings.SCREEN_WIDTH - spacing) // 5
                padding_x = (space - settings.PREVIEW_BLOCK_SIZE * settings.TETRIS_FIELD_WIDTH) // 2
                space_y = settings.SCREEN_HEIGHT // 2
                padding_y = (space_y - settings.PREVIEW_BLOCK_SIZE * settings.TETRIS_FIELD_HEIGHT) // 2
                self.screen.blit(sf, (col * space + spacing + padding_x, row * space_y + padding_y))

            pg.display.update()

        t.join()
        pg.quit()
