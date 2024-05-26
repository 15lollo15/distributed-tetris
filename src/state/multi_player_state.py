from net.peer import Peer
from state.single_player_state import SinglePlayerState


class MultiPlayerState(SinglePlayerState):

    def __init__(self, peer: Peer | None):
        super().__init__()
        self.peer = peer

