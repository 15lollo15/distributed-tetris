from random import Random

import Pyro4

from net.peer import Peer, check_active
from state.multi_player_state_new import MultiPlayerState


class TetrisPeer(Peer):

    def __init__(self, player_name: str, multiplayer_state: MultiPlayerState = None):
        super().__init__(player_name)
        self.multiplayer_state = multiplayer_state
        self.seed = None

        self.is_running = False

    @check_active
    @Pyro4.expose
    @Pyro4.oneway
    def set_lose(self, player_name: str):
        with self.lock:
            self.multiplayer_state.set_is_dead(player_name)

    @check_active
    def broadcast_i_lose(self):
        if not self.is_running:
            raise NotInGame()
        for player_name, proxy in self.peers.items():
            proxy.set_lose(self.player_name)

    @check_active
    def broadcast_setup_game(self):
        if self.is_running:
            raise AlreadyInGame()
        for player_name, proxy in self.peers.items():
            proxy.setup_game()
        self.setup_game()

    @check_active
    def broadcast_start_game(self):
        if self.is_running:
            raise AlreadyInGame()
        for player_name, proxy in self.peers.items():
            proxy.start_game()
        self.start_game()

    @check_active
    def broadcast_seed(self):
        if self.is_running:
            raise AlreadyInGame()
        self.seed = Random().randint(0, 1000000)
        for player_name, proxy in self.peers.items():
            proxy.set_seed(self.seed)

    @check_active
    @Pyro4.expose
    def set_seed(self, seed):
        with self.lock:
            if self.is_running:
                raise AlreadyInGame()
            self.seed = seed

    @check_active
    @Pyro4.expose
    def setup_game(self):
        with self.lock:
            if self.is_running:
                raise AlreadyInGame()
            self.multiplayer_state.setup(self.seed)
            self.multiplayer_state.init_is_dead(list(self.peers.keys()))

    @check_active
    @Pyro4.expose
    @Pyro4.oneway
    def start_game(self):
        with self.lock:
            if self.is_running:
                raise AlreadyInGame()
            self.multiplayer_state.start_game()
            self.is_running = True

    @check_active
    @Pyro4.expose
    def quit_game(self):
        with self.lock:
            self.is_running = False

    def reset(self):
        super().reset()
        self.is_running = False
        self.seed = None


class AlreadyInGame(Exception):
    pass


class NotInGame(Exception):
    pass
