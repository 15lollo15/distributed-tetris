from typing import List, Dict

import pygame as pg
import pygame_gui
from pygame import Surface, Event

from net.exceptions import PlayerAlreadyIn, LobbyFull
from utils import settings
from net.peer import Peer, LobbyNameAlreadyTaken
from state.game_state import GameState


# TODO: Info messages
class BrowseLobbyState(GameState):

    def __init__(self, peer: Peer):
        self.peer = peer
        self.ui_manager = pygame_gui.UIManager(settings.SCREEN_SIZE, 'data/theme.json')
        self.lobby_selection_list: pygame_gui.elements.UISelectionList = None
        self.new_lobby_button: pygame_gui.elements.UIButton = None
        self.matchmaking_label: pygame_gui.elements.UILabel = None
        self.back_button: pygame_gui.elements.UIButton = None
        self.time_elapsed: int = 0
        self.setup_ui()

    def setup_ui(self):
        matchmaking_label_rect = pg.Rect(0, 0, 100, 100)
        self.matchmaking_label = pygame_gui.elements.UILabel(matchmaking_label_rect, 'Match making',
                                                             manager=self.ui_manager,
                                                             anchors={'centerx': 'centerx'}
                                                             )
        lobby_selection_list_rect = pg.Rect(0, 0, 1500, 600)
        self.lobby_selection_list = pygame_gui.elements.UISelectionList(lobby_selection_list_rect, [],
                                                                        manager=self.ui_manager,
                                                                        anchors={'centerx': 'centerx',
                                                                                 'centery': 'centery'}
                                                                        )
        new_lobby_button_rect = pg.Rect(0, 0, 200, 50)
        new_lobby_button_rect.right = 1600
        new_lobby_button_rect.top = 25
        self.new_lobby_button = pygame_gui.elements.UIButton(new_lobby_button_rect, 'New lobby',
                                                             manager=self.ui_manager)

        self.back_button = pygame_gui.elements.UIButton(pg.Rect(100, 25, 200, 50), 'Back', manager=self.ui_manager)

    def handle_events(self, events: List[Event]) -> str | None:
        for event in events:
            if event.type == pg.QUIT:
                return 'QUIT'

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.back_button:
                    return 'MENU'
                if event.ui_element == self.new_lobby_button:
                    try:
                        self.peer.new_lobby(settings.MAX_PLAYERS)
                    except LobbyNameAlreadyTaken:
                        print('Lobby name already taken')
                        return
                    return 'LOBBY'

            if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
                if event.ui_element == self.lobby_selection_list:
                    lobby_name = event.text
                    try:
                        self.peer.connect_to_lobby(lobby_name)
                    except PlayerAlreadyIn:
                        print('Player already in lobby')
                        return
                    except LobbyFull:
                        print('Lobby full')
                        return
                    return 'LOBBY'

            self.ui_manager.process_events(event)

    def refresh(self):
        lobbies_dict: Dict[str, str] = self.peer.name_server.list(metadata_all=['lobby'])
        self.lobby_selection_list.set_item_list(list(lobbies_dict.keys()))

    def update(self, delta_time: int):
        self.ui_manager.update(delta_time)
        self.time_elapsed += delta_time
        if self.time_elapsed > settings.REFRESH_INTERVAL:
            self.refresh()
            self.time_elapsed = 0

    def render(self, screen: Surface):
        self.ui_manager.draw_ui(screen)

    def on_change(self):
        super().on_change()
        self.refresh()


