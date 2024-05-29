import logging
import threading
from dataclasses import dataclass
from functools import wraps
from typing import Dict

import Pyro4
import Pyro4.errors

from net.lobby import Lobby

logger = logging.getLogger(__name__)


def check_active(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.active:
            raise Pyro4.errors.CommunicationError("Peer is no longer active.")
        return method(self, *args, **kwargs)

    return wrapper


@dataclass
class LobbyDescriptor:
    daemon: Pyro4.Daemon = None
    instance: Lobby = None
    uri: Pyro4.URI = None
    thread: threading.Thread = None
    proxy: Pyro4.Proxy = None


class Peer:
    def __init__(self, player_name: str):
        self.player_name = player_name

        self.daemon = Pyro4.Daemon()
        self.uri = self.daemon.register(self)
        self.name_server: Pyro4.Proxy = Pyro4.locateNS()

        self.lobby_descriptor: LobbyDescriptor | None = None

        self.my_lobby_name = f'{self.player_name}-lobby'
        self.peers: Dict[str, Pyro4.Proxy] = {}
        self.name_server.remove(self.my_lobby_name)

        self.request_loop_thread = threading.Thread(target=self.daemon.requestLoop)
        self.request_loop_thread.start()

        self.lock = threading.Lock()

        self.active = True

    @check_active
    def kill(self):
        if self.in_lobby():
            self.disconnect_from_lobby()
        self.daemon.shutdown()
        self.request_loop_thread.join()
        self.active = False

    @check_active
    @Pyro4.expose
    @Pyro4.oneway
    def is_reachable(self):
        # This method is used to check if the peer is still reachable. It does nothing
        pass

    @check_active
    @Pyro4.expose
    def get_peers(self):
        with self.lock:
            if not self.lobby_descriptor:
                raise NotInLobby()
            players = self.lobby_descriptor.proxy.list_players()
            self._init_peers(players)

    @check_active
    def broadcast_peers(self):
        if not self.is_host():
            raise NotAHost()
        self.get_peers()
        for player_name, proxy in self.peers.items():
            proxy.get_peers()
            proxy.disconnect_from_lobby()
        self.disconnect_from_lobby()

    @check_active
    def _init_peers(self, players: Dict[str, str]):
        self.peers = {}
        for player_name, uri in players.items():
            if player_name == self.player_name:
                continue
            self.peers[player_name] = Pyro4.Proxy(uri)

    @check_active
    def is_host(self):
        return self.in_lobby() and self.lobby_descriptor.instance

    @check_active
    def in_lobby(self):
        return self.lobby_descriptor is not None

    @check_active
    def connect_to_lobby(self, name='lobby'):
        if self.in_lobby():
            raise AlreadyInLobby()

        lobby_proxy = Pyro4.Proxy(f'PYRONAME:{name}')
        lobby_proxy.join_lobby(self.player_name, self.uri)
        self.lobby_descriptor = LobbyDescriptor(proxy=lobby_proxy)

    @check_active
    @Pyro4.expose
    def disconnect_from_lobby(self):
        with self.lock:
            if not self.lobby_descriptor:
                raise NotInLobby()

            if self.is_host():
                self.shutdown_lobby()
                return

            self.lobby_descriptor.proxy.leave_lobby(self.player_name)
            self.lobby_descriptor = None

    @check_active
    def _generate_lobby(self) -> LobbyDescriptor:
        lobby_daemon: Pyro4.Daemon = Pyro4.Daemon()
        lobby_instance = Lobby(5, name=self.my_lobby_name)  # TODO: Add in configuration
        lobby_uri = lobby_daemon.register(lobby_instance)
        self.name_server.register(self.my_lobby_name, lobby_uri, metadata=['lobby'], safe=True)
        lobby_thread = threading.Thread(target=lobby_daemon.requestLoop)
        lobby_thread.start()

        return LobbyDescriptor(
            daemon=lobby_daemon,
            instance=lobby_instance,
            uri=lobby_uri,
            thread=lobby_thread,
            proxy=Pyro4.Proxy(f'PYRONAME:{self.my_lobby_name}')
        )

    @check_active
    def new_lobby(self):
        if self.in_lobby():
            raise AlreadyInLobby()
        self.lobby_descriptor = self._generate_lobby()
        self.lobby_descriptor.proxy.join_lobby(self.player_name, self.uri)

    @check_active
    def shutdown_lobby(self):
        if not self.is_host():
            raise NotAHost()
        self.lobby_descriptor.instance.deactivate()
        self.lobby_descriptor.daemon.shutdown()
        self.lobby_descriptor.thread.join()
        self.lobby_descriptor.daemon.close()
        self.name_server.remove(self.my_lobby_name)
        self.lobby_descriptor = None

    def reset(self):
        if self.in_lobby():
            self.disconnect_from_lobby()


class AlreadyInLobby(Exception):
    pass


class NotAHost(Exception):
    pass


class NotInLobby(Exception):
    pass
