import logging
import threading
from random import Random
from typing import Dict

import Pyro4
import Pyro4.errors

from net.lobby import Lobby

logger = logging.getLogger(__name__)


class Peer:
    def __init__(self, player_name: str):
        self.player_name = player_name

        self.daemon = Pyro4.Daemon()
        self.uri = self.daemon.register(self)
        self.name_server: Pyro4.Proxy = Pyro4.locateNS()

        self.lobby: Pyro4.Daemon | None = None
        self.lobby_instance: Lobby | None = None
        self.lobby_uri = None
        self.lobby_thread: threading.Thread | None = None
        self.lobby_proxy: Pyro4.Proxy | None = None

        self.lobby_name = f'{self.player_name}-lobby'
        self.peers: Dict[str, Pyro4.Proxy] = {}
        self.seed = None

        self.request_loop_thread = threading.Thread(target=self.daemon.requestLoop)
        self.request_loop_thread.start()

        self.multiplayer_instance = None
        self.is_ready = False

    @Pyro4.expose
    @Pyro4.oneway
    def set_is_ready(self):
        self.is_ready = True

    @Pyro4.expose
    @Pyro4.oneway
    def set_seed(self, seed):
        self.seed = seed

    def share_peers(self):
        self.seed = Random().random()
        self.setup_other_peers()
        for player_name, peer in self.peers.items():
            print(f'{player_name} setup...')
            peer.setup_other_peers()
            print(f'{player_name} setup SUCCESS')
            peer.set_seed(self.seed)
            peer.set_is_ready()

    @Pyro4.expose
    def setup_other_peers(self):
        self.peers = {}
        players_dict = self.lobby_proxy.list_players()
        for player_name, uri in players_dict.items():
            if player_name == self.player_name:
                continue
            self.peers[player_name] = Pyro4.Proxy(uri)

    @Pyro4.expose
    @Pyro4.oneway
    def set_tetris_field(self, player_name, field):
        self.multiplayer_instance.peers_fields[player_name] = field

    @Pyro4.expose
    @Pyro4.oneway
    def add_rows(self, num_rows: int):
        self.multiplayer_instance.tetris_field.add_rows(num_rows)
        for uri, peer in self.peers.items():
            peer.set_tetris_field(self.player_name, self.multiplayer_instance.tetris_field.field)

    @Pyro4.expose
    @Pyro4.oneway
    def set_is_dead(self, player_name):
        self.multiplayer_instance.is_dead[player_name] = True
        # TODO: Check if i win
        # self.multiplayer_instance.check_i_win()

    # TODO: Implement this
    # @Pyro4.expose
    # def set_winner(self, uri):
    #     self.winner = uri
    #     self.is_running = False

    def reset(self):
        self.lobby: Pyro4.Daemon | None = None
        self.lobby_instance: Lobby | None = None
        self.lobby_uri = None
        self.lobby_thread: threading.Thread | None = None
        self.lobby_proxy: Pyro4.Proxy | None = None
        self.peers: Dict[str, Pyro4.Proxy] = {}
        self.seed = None

        self.peers: Dict[str, Pyro4.Proxy] = {}
        self.seed = None
        self.multiplayer_instance = None
        self.is_ready = False

    def is_host(self):
        return self.lobby_instance is not None

    def connect_to_lobby(self, name='lobby') -> bool:
        if self.lobby_proxy:
            print('lobby proxy not None')
            return False
        try:
            self.lobby_proxy = Pyro4.Proxy(f'PYRONAME:{name}')
            return self.lobby_proxy.join_lobby(self.player_name, self.uri)
        except Pyro4.errors.CommunicationError:
            self.name_server.remove(name)
            self.reset()
            print('communication error')
            return False

    def disconnect(self):
        if not self.lobby_proxy:
            print('lobby proxy is None')
            return
        self.lobby_proxy.leave_lobby(self.player_name)
        self.reset()

    def new_lobby(self):
        if self.lobby_uri:
            print('lobby uri not None')
            return False
        self.lobby: Pyro4.Daemon = Pyro4.Daemon()
        self.lobby_instance = Lobby(5, name=self.lobby_name)  # TODO: Add in configuration
        self.lobby_uri = self.lobby.register(self.lobby_instance)
        try:
            self.name_server.register(self.lobby_name, self.lobby_uri, metadata=['lobby'], safe=True)
        except Pyro4.errors.NamingError:
            self.reset()
            print('Naming error')
            return False
        self.lobby_thread = threading.Thread(target=self.lobby.requestLoop)
        self.lobby_thread.start()
        self.connect_to_lobby(self.lobby_name)
        print('New Lobby: Success')
        return True

    def shutdown_lobby(self):
        if not self.is_host():
            print('not host')
            return
        if self.lobby_instance:
            self.lobby_instance.deactivate()  # Deactivate the lobby
        if self.lobby:
            self.lobby.shutdown()
            self.lobby_thread.join()
            self.lobby.close()
        if self.name_server:
            self.name_server.remove(self.lobby_name)
        self.reset()
