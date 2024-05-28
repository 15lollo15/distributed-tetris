from functools import wraps
from threading import Lock
from typing import Dict

import Pyro4
import Pyro4.errors


def check_active(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.active:
            raise Pyro4.errors.CommunicationError("Lobby is no longer active.")
        return method(self, *args, **kwargs)

    return wrapper


class PlayerAlreadyIn(Exception):
    pass


class LobbyFull(Exception):
    pass


class PlayerNotInLobby(Exception):
    pass


class Lobby:
    def __init__(self, max_players: int, name='lobby'):
        self.players = {}
        self.lock = Lock()
        self.active = True
        self.max_players = max_players
        self.name = name

    def _is_full(self):
        return len(self.players.keys()) >= self.max_players

    @check_active
    @Pyro4.expose
    def join_lobby(self, player_name: str, player_uri: str):
        with self.lock:
            if player_name in self.players:
                raise PlayerAlreadyIn("Player is already in the lobby.")
            if self._is_full():
                raise LobbyFull("Lobby is full.")
            self.players[player_name] = player_uri

    @check_active
    @Pyro4.expose
    def leave_lobby(self, player_name: str):
        with self.lock:
            if player_name not in self.players:
                raise PlayerNotInLobby("Player is not in the lobby.")
            del self.players[player_name]

    @check_active
    @Pyro4.expose
    def list_players(self) -> Dict[str, str]:
        with self.lock:
            return self.players

    @check_active
    @Pyro4.expose
    def get_name(self) -> str:
        with self.lock:
            return self.name

    @check_active
    @Pyro4.expose
    def get_players_number(self) -> int:
        with self.lock:
            return len(self.players)

    @check_active
    @Pyro4.expose
    def get_max_players_number(self) -> int:
        with self.lock:
            return self.max_players

    def deactivate(self):
        self.active = False
