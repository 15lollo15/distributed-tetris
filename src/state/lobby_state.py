from typing import List, Dict

import Pyro4.errors
import pygame as pg
import pygame_gui
from pygame import Surface, Event

import settings
from net.peer import Peer
from state.game_state import GameState


class LobbyState(GameState):

    def __init__(self, peer: Peer):
        self.peer = peer
        self.ui_manager = pygame_gui.UIManager(settings.SCREEN_SIZE, 'data/theme.json')
        self.players_selection_list: pygame_gui.elements.UISelectionList = None
        self.lobby_name_label: pygame_gui.elements.UILabel = None
        self.num_players_label: pygame_gui.elements.UILabel = None
        self.back_button: pygame_gui.elements.UIButton = None
        self.time_elapsed: int = 0
        self.setup_ui()

        self.crashed = False

    def setup_ui(self):
        lobby_name_label_rect = pg.Rect(0, 0, 100, 100)
        self.lobby_name_label = pygame_gui.elements.UILabel(lobby_name_label_rect, 'Match making',
                                                            manager=self.ui_manager,
                                                            anchors={'centerx': 'centerx'})

        players_selection_list_rect = pg.Rect(0, 0, 1500, 600)
        self.players_selection_list = pygame_gui.elements.UISelectionList(players_selection_list_rect,
                                                                          [], manager=self.ui_manager,
                                                                          anchors={'centerx': 'centerx',
                                                                                   'centery': 'centery'}
                                                                          )
        num_players_label_rect = pg.Rect(100, 25, 100, 100)
        num_players_label_rect.right = 1600
        num_players_label_rect.top = 700
        self.num_players_label = pygame_gui.elements.UILabel(num_players_label_rect, '',
                                                             manager=self.ui_manager)

        self.back_button = pygame_gui.elements.UIButton(pg.Rect(100, 25, 200, 50), 'Back', manager=self.ui_manager)

    def handle_events(self, events: List[Event]) -> str | None:
        if self.crashed:
            self.peer.reset()
            self.crashed = False
            return 'BROWSE_LOBBY'

        for event in events:
            if event.type == pg.QUIT:
                if self.peer.is_host():
                    self.peer.shutdown_lobby()
                return 'QUIT'

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.back_button:
                    if self.peer.is_host():
                        self.peer.shutdown_lobby()
                    else:
                        self.peer.disconnect()
                    return 'BROWSE_LOBBY'

            self.ui_manager.process_events(event)

    def update(self, delta_time: int):
        if self.crashed:
            return
        try:
            self.ui_manager.update(delta_time)
            self.time_elapsed += delta_time
            if self.time_elapsed > 5000:
                players_dict: Dict[str, str] = self.peer.lobby_proxy.list_players()
                self.players_selection_list.set_item_list(list(players_dict.keys()))
                self.time_elapsed = 0
            self.lobby_name_label.set_text(self.peer.lobby_proxy.get_name())

            connected_players = self.peer.lobby_proxy.get_players_number()
            max_players = self.peer.lobby_proxy.get_max_players_number()
            players_text = f'({connected_players}/{max_players})'
            self.num_players_label.set_text(players_text)
        except Pyro4.errors.ConnectionClosedError:
            self.crashed = True

    def render(self, screen: Surface):
        self.ui_manager.draw_ui(screen)
