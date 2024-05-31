from pathlib import Path
from typing import List

import pygame as pg
import pygame_gui
from pygame import Surface
from pygame.event import Event

from net.tetris_peer import TetrisPeer
from state.game_state import GameState
from utils import settings


class MenuState(GameState):

    def __init__(self, peer: TetrisPeer):
        super().__init__()
        self.peer = peer
        self.ui_manager = pygame_gui.UIManager(settings.SCREEN_SIZE, Path(r'data\theme.json'))
        self.single_player_button = None
        self.multi_player_button = None
        self.quit_button = None

        self.single_player_button: pygame_gui.elements.UIButton = None
        self.multi_player_button: pygame_gui.elements.UIButton = None
        self.quit_button: pygame_gui.elements.UIButton = None
        self.name_entry: pygame_gui.elements.ui_text_entry_line.UITextEntryLine = None

        self.setup_ui()

    def setup_ui(self):
        pygame_gui.elements.UILabel(pg.Rect((0, 0), (200, 100)), 'Tetris', self.ui_manager, object_id='#game_title')
        self.single_player_button = pygame_gui.elements.UIButton(pg.Rect((0, 100), (200, 100)), 'Single player',
                                                                 self.ui_manager)
        self.multi_player_button = pygame_gui.elements.UIButton(pg.Rect((0, 200), (200, 100)), 'Multi player',
                                                                self.ui_manager)
        self.quit_button = pygame_gui.elements.UIButton(pg.Rect((0, 300), (200, 100)), 'Quit', self.ui_manager)
        self.name_entry = pygame_gui.elements.ui_text_entry_line.UITextEntryLine(pg.Rect((0, 400), (200, 50)),
                                                                                 manager=self.ui_manager,
                                                                                 initial_text=self.peer.player_name,
                                                                                 placeholder_text='Player name')

    def handle_events(self, events: List[Event]) -> str | None:
        for event in events:
            if event.type == pg.QUIT:
                return 'QUIT'
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.multi_player_button:
                    self.peer.set_player_name(self.name_entry.get_text())
                    return 'BROWSE_LOBBY'
                elif event.ui_element == self.single_player_button:
                    return 'SINGLE_PLAYER'
                elif event.ui_element == self.quit_button:
                    return 'QUIT'

            self.ui_manager.process_events(event)

    def update(self, delta_time: int):
        self.ui_manager.update(delta_time)

    def render(self, screen: Surface):
        self.ui_manager.draw_ui(screen)
