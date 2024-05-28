import pygame as pg

import settings
from net.peer import Peer
from net.tetris_peer import TetrisPeer
from state.state_manager import StateManager


class Game:
    def __init__(self, player_name='player'):
        pg.init()
        self.screen = pg.display.set_mode(settings.SCREEN_SIZE)
        self.clock = pg.time.Clock()
        self.is_running = False
        self.peer = TetrisPeer(player_name=player_name)
        self.state_manager = StateManager(self.peer)

    def run(self):
        self.is_running = True
        while self.is_running:
            delta_time = self.clock.tick(settings.FRAME_RATE)
            self.screen.fill('black')
            events = pg.event.get()

            self.is_running = self.state_manager.handle_events(events)
            self.state_manager.update(delta_time)
            self.state_manager.render(self.screen)

            pg.display.flip()
