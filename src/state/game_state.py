from abc import abstractmethod
from typing import List

from pygame import Surface
from pygame.event import Event


class GameState:

    @abstractmethod
    def handle_events(self, events: List[Event]) -> str | None:
        pass

    @abstractmethod
    def update(self, delta_time: int):
        pass

    @abstractmethod
    def render(self, screen: Surface):
        pass

    def on_change(self):
        pass
