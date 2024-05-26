from typing import List, Dict

import pygame as pg
import pygame_gui
from pygame import Surface, Event

import settings
from net.peer import Peer
from state.game_state import GameState


class BrowseLobbyState(GameState):

    def __init__(self, peer: Peer):
        self.peer = peer
        self.ui_manager = pygame_gui.UIManager(settings.SCREEN_SIZE, 'data/theme.json')
        self.lobby_selection_list: pygame_gui.elements.UISelectionList = None
        self.new_lobby_button: pygame_gui.elements.UIButton = None
        self.time_elapsed: int = 0
        self.setup_ui()

    def setup_ui(self):
        self.lobby_selection_list = pygame_gui.elements.UISelectionList(pg.Rect((0, 0), (300, 600)), [],
                                                                        manager=self.ui_manager,
                                                                        allow_double_clicks=True)
        self.new_lobby_button = pygame_gui.elements.UIButton(pg.Rect((0, 600), (100, 200)), 'New lobby',
                                                             self.ui_manager)

    def handle_events(self, events: List[Event]) -> str | None:
        for event in events:
            if event.type == pg.QUIT:
                return 'QUIT'

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.new_lobby_button:
                    if self.peer.new_lobby():
                        return 'LOBBY'

            if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                if event.ui_element == self.lobby_selection_list:
                    lobby_name = event.text
                    if self.peer.connect_to_lobby(lobby_name):
                        return 'LOBBY'

            self.ui_manager.process_events(event)

    def update(self, delta_time: int):
        self.ui_manager.update(delta_time)
        self.time_elapsed += delta_time
        if self.time_elapsed > 5000:
            lobbies_dict: Dict[str, str] = self.peer.name_server.list(metadata_all=['lobby'])
            self.lobby_selection_list.set_item_list(list(lobbies_dict.keys()))
            self.time_elapsed = 0

    def render(self, screen: Surface):
        self.ui_manager.draw_ui(screen)
