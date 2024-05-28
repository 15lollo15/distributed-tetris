import threading
from typing import Dict, List

from pygame import Event

from state.single_player_state import SinglePlayerState
from tetris_field import BlockType


class MultiPlayerState(SinglePlayerState):

    def __init__(self, peer):
        super().__init__()
        self.lock = threading.Lock()
        from net.tetris_peer import TetrisPeer
        self.peer: TetrisPeer = peer
        self.is_dead: Dict[str, bool] = {}
        self.i_win = False

    def set_is_dead(self, player_name: str):
        with self.lock:
            self.is_dead[player_name] = True

    def init_is_dead(self, players: List[str]):
        self.is_dead = {player: False for player in players}

    def setup(self, seed=None):
        super().setup(seed)
        self.is_dead: Dict[str, bool] = {}
        self.i_win = False

    def handle_events(self, events: List[Event]) -> str | None:
        if self.i_win:
            return 'MENU'
        return super().handle_events(events)

    def on_change(self):
        # Do nothing because is set up by the peer
        pass

    def check_i_win(self):
        for is_dead in self.is_dead.values():
            if not is_dead:
                return
        self.i_win = True

    def update(self, delta_time: int):
        if not self.is_running:
            return
        self.tetris_field_sf.fill(BlockType.NONE.value)
        self.tetromino.update()
        self.check_i_win()
        if self.i_win:
            return
        if self.tetromino.is_dead:
            self.check_if_lose()
            if self.i_lose:
                self.peer.broadcast_i_lose()
                return
            self.add_tetronimo_to_field()
            count = self.tetris_field.remove_full_rows()
            self.level_progress(count)
            self.new_tetromino()
        self.draw_field(self.tetris_field.field, self.tetris_field_sf)
        self.draw_tetronimo()
