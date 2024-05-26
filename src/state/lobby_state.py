from typing import List, Dict

import pygame as pg
from pygame import Surface, Event
import pygame_gui

import settings
from net.peer import Peer
from state.game_state import GameState


class LobbyState(GameState):

    def __init__(self, peer: Peer):
        self.peer = peer
        self.ui_manager = pygame_gui.UIManager(settings.SCREEN_SIZE, 'data/theme.json')
        self.lobby_selection_list: pygame_gui.elements.UISelectionList = None
        self.time_elapsed: int = 0
        self.setup_ui()

    def setup_ui(self):
        self.lobby_selection_list = pygame_gui.elements.UISelectionList(pg.Rect((0, 0), (300, 600)),
                                                                        [], manager=self.ui_manager)

    def handle_events(self, events: List[Event]) -> str | None:
        for event in events:
            if event.type == pg.QUIT:
                return 'QUIT'
            self.ui_manager.process_events(event)

    def update(self, delta_time: int):
        self.ui_manager.update(delta_time)
        self.time_elapsed += delta_time
        if self.time_elapsed > 5000:
            players_dict: Dict[str, str] = self.peer.lobby_proxy.list_players()
            self.lobby_selection_list.set_item_list(list(players_dict.keys()))
            self.time_elapsed = 0

    def render(self, screen: Surface):
        self.ui_manager.draw_ui(screen)