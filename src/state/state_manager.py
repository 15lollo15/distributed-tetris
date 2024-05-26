from typing import Dict

from net.peer import Peer
from state.browse_lobby_state import BrowseLobbyState
from state.game_state import GameState
from state.lobby_state import LobbyState
from state.menu_state import MenuState
from state.play_state import PlayState


class StateManager:
    def __init__(self, peer: Peer):
        self.states: Dict[str, GameState] = {
            'MENU': MenuState(),
            'BROWSE_LOBBY': BrowseLobbyState(peer),
            'LOBBY': LobbyState(peer),
            'PLAY': PlayState(peer)
        }
        self.current_state: GameState = self.states["LOBBY"]

    def change_state(self, new_state):
        old_state = self.current_state
        self.current_state = self.states[new_state]
        if old_state != self.current_state:
            self.current_state.on_change()

    def handle_events(self, events):
        result = self.current_state.handle_events(events)
        if result:
            if result == "QUIT":
                return False
            self.change_state(result)
        return True

    def update(self, delta_time):
        self.current_state.update(delta_time)

    def render(self, screen):
        self.current_state.render(screen)
