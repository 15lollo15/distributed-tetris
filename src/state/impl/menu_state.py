from typing import List

import pygame as pg
import pygame_gui
from pygame import Surface
from pygame.event import Event

from utils import settings
from state.game_state import GameState


# TODO: Player name input
class MenuState(GameState):

    def __init__(self):
        super().__init__()
        self.ui_manager = pygame_gui.UIManager(settings.SCREEN_SIZE, 'data/theme.json')
        self.single_player_button = None
        self.multi_player_button = None
        self.quit_button = None

        pygame_gui.elements.UILabel(pg.Rect((0, 0), (200, 100)), 'Tetris', self.ui_manager, object_id='#game_title')
        self.single_player_button = pygame_gui.elements.UIButton(pg.Rect((0, 100), (200, 100)), 'Single player',
                                                                 self.ui_manager)
        self.multi_player_button = pygame_gui.elements.UIButton(pg.Rect((0, 200), (200, 100)), 'Multi player',
                                                                self.ui_manager)
        self.quit_button = pygame_gui.elements.UIButton(pg.Rect((0, 300), (200, 100)), 'Quit', self.ui_manager)

    def handle_events(self, events: List[Event]) -> str | None:
        for event in events:
            if event.type == pg.QUIT:
                return 'QUIT'
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.multi_player_button:
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
