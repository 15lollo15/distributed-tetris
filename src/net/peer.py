import logging
import threading

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

    def reset(self):
        self.lobby: Pyro4.Daemon | None = None
        self.lobby_instance: Lobby | None = None
        self.lobby_uri = None
        self.lobby_thread: threading.Thread | None = None
        self.lobby_proxy: Pyro4.Proxy | None = None

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
        try:
            self.lobby_uri = self.lobby.register(self.lobby_instance)
        except Pyro4.errors.NamingError:
            self.reset()
            print('Naming error')
            return False
        self.name_server.register(self.lobby_name, self.lobby_uri, metadata=['lobby'], safe=True)
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
