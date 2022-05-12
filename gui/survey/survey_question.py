import pygame


class SurveyQuestion:
    def __init__(self):
        pass

    def draw(self, surface):
        pass

    def mouse_down(self, mouse):
        pass

    def mouse_up(self, mouse):
        pass

    def key_up(self, event: pygame.event.Event):
        pass

    def end_group(self):
        pass

    def has_next(self):
        pass

    def move_next(self):
        pass

    def has_prev(self):
        pass

    def move_prev(self):
        pass

    def notify_events(self, events):
        pass

    def enable(self):
        pass

    def disable(self):
        pass

    def str_result(self) -> str:
        pass