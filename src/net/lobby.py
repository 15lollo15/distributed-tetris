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


class Lobby:
    def __init__(self, max_players: int):
        self.players = {}
        self.lock = Lock()
        self.active = True
        self.max_players = max_players

    def _is_full(self):
        return len(self.players.keys()) >= self.max_players

    @check_active
    @Pyro4.expose
    def join_lobby(self, player_name: str, player_uri: str) -> bool:
        with self.lock:
            if player_name not in self.players and not self._is_full():
                self.players[player_name] = player_uri
                return True
            return False

    @check_active
    @Pyro4.expose
    def leave_lobby(self, player_name: str) -> bool:
        with self.lock:
            if player_name in self.players:
                del self.players[player_name]
                return True
            return False

    @check_active
    @Pyro4.expose
    def list_players(self) -> Dict[str, str]:
        with self.lock:
            return self.players

    def deactivate(self):
        self.active = False
