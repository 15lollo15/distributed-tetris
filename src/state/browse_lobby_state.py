from typing import List

from pygame import Surface, Event
import pygame_gui
import pygame as pg

import settings
from net.peer import Peer
from state.game_state import GameState


class BrowseLobbyState(GameState):

    def __init__(self, peer: Peer):
        self.peer = peer
        self.ui_manager = pygame_gui.UIManager(settings.SCREEN_SIZE, 'data/theme.json')
        self.lobby_selection_list: pygame_gui.elements.UISelectionList = None
        self.new_lobby_button: pygame_gui.elements.UIButton = None
        self.setup_ui()

    def setup_ui(self):
        self.lobby_selection_list = pygame_gui.elements.UISelectionList(pg.Rect((0, 0), (300, 600)), [], manager=self.ui_manager)
        self.new_lobby_button = pygame_gui.elements.UIButton(pg.Rect((0, 600), (100, 200)), 'New lobby', self.ui_manager)

    def handle_events(self, events: List[Event]) -> str | None:
        for event in events:
            if event.type == pg.QUIT:
                return 'QUIT'

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.new_lobby_button:
                    self.peer.new_lobby()
                    return 'LOBBY'

            self.ui_manager.process_events(event)

    def update(self, delta_time: int):
        self.ui_manager.update(delta_time)

    def render(self, screen: Surface):
        self.ui_manager.draw_ui(screen)
