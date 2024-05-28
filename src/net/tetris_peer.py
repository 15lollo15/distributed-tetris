import threading
from random import Random
from typing import List

import Pyro4

from net.peer import Peer, check_active
from state.multi_player_state import MultiPlayerState


class TetrisPeer(Peer):

    def __init__(self, player_name: str, multiplayer_state: MultiPlayerState = None):
        super().__init__(player_name)
        self.multiplayer_state = multiplayer_state
        self.seed = None

        self.is_running = False

    @check_active
    def broadcast_start_game(self):
        if self.is_running:
            raise AlreadyInGame()
        threads: List[threading.Thread] = []
        for player_name, proxy in self.peers.items():
            thread = threading.Thread(target=proxy.start_game)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
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
    def start_game(self):
        with self.lock:
            if self.is_running:
                raise AlreadyInGame()
            self.multiplayer_state.setup(self.seed)
            self.is_running = True

    @check_active
    @Pyro4.expose
    def quit_game(self):
        with self.lock:
            self.is_running = False


class AlreadyInGame(Exception):
    pass
