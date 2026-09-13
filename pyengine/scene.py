from __future__ import annotations
import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import PyEngine


# ――――――――――――――――――――――――― scene base ―――――――――――――――――――――――――


class Scene:
    def __init__(self, engine: PyEngine):
        self.engine = engine
        self.screen = engine.screen
        self.width = engine.width
        self.height = engine.height

    # ――――――――――――――――――――――――― lifecycle ―――――――――――――――――――――――――

    def on_enter(self, **kwargs):
        """
        Вызывается при активации (входе) в сцену. Используется для инициализации объектов, загрузки ресурсов и настройки начального состояния.
        """
        pass

    def on_exit(self):
        """
        Вызывается при выходе из сцены. Используется для очистки ресурсов, сохранения состояния или остановки музыки.
        """
        pass

    # ――――――――――――――――――――――――― per-frame ―――――――――――――――――――――――――

    def events(self, event: pygame.event.Event):
        """
        Обрабатывает события pygame (нажатия клавиш, движения мыши и т.д.) для текущей активной сцены.
        """
        pass

    def update(self):
        """
        Обновляет внутреннюю логику сцены (физика, ИИ, состояния объектов) перед каждым кадром отрисовки.
        """
        pass

    def draw(self):
        """
        Отрисовывает все визуальные элементы текущей сцены на экран.
        """
        pass