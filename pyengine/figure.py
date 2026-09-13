from __future__ import annotations
import math
import pygame
from typing import Literal, TYPE_CHECKING

ShapeType = Literal['rect', 'circle', 'ellipse', 'line', 'polygon', 'sprite']

# ――――――――――――――――――――――――― figure ―――――――――――――――――――――――――
class Figure:
    def __init__(
        self,
        screen: pygame.Surface,
        shape: ShapeType,
        color: tuple,
        params: tuple,
        width: int = 0,
        images: dict[str, pygame.Surface] | None = None,
        use_camera: bool = True,
    ):
        self.screen = screen
        self.shape = shape
        self.color = color
        self.params: list = list(params)
        self.width = width
        self.images = images
        self.last_contact_time: float = 0
        self.use_camera: bool = use_camera
        
        # Анимации
        self.current_anim: str | None = None
        self.anim_frame: int = 0
        self.anim_timer: float = 0.0
        self.anim_finished: bool = False
        
        # x/y are always kept in sync with params[0]/[1] via set_pos
        self.x: float = float(params[0])
        self.y: float = float(params[1])
        self.image_name: str | None = params[2] if shape == 'sprite' and len(params) >= 3 else None

    # ――――――――――――――――――――――――― animations ―――――――――――――――――――――――――
    def play(self, anim_name: str):
        """
        Запускает указанную анимацию, сбрасывая текущий кадр и таймер.
        - anim_name (str): Имя анимации, зарегистрированной в engine.add_animation.
        """
        self.current_anim = anim_name
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.anim_finished = False

    def _update_animation(self, animations: dict, dt: float):
        """
        Внутренний метод: обновляет кадр анимации на основе прошедшего времени.
        Вызывается автоматически движком в главном цикле.
        """
        if self.current_anim and self.current_anim in animations:
            if self.anim_finished:
                return
                
            anim = animations[self.current_anim]
            self.anim_timer += dt
            frame_duration = 1.0 / anim['fps']
            
            if self.anim_timer >= frame_duration:
                self.anim_timer -= frame_duration
                
                if self.anim_frame < len(anim['frames']) - 1:
                    self.anim_frame += 1
                    self.set_image(anim['frames'][self.anim_frame])
                else:
                    if anim.get('loop', True):
                        self.anim_frame = 0
                        self.set_image(anim['frames'][0])
                    else:
                        self.anim_finished = True

    # ――――――――――――――――――――――――― position ―――――――――――――――――――――――――
    def set_pos(self, x: float, y: float):
        """
        Устанавливает новые координаты фигуры, автоматически синхронизируя внутренние переменные и параметры отрисовки.
        """
        self.x = x
        self.y = y
        self.params[0] = x
        self.params[1] = y
        if self.shape == 'sprite':
            self.params[2] = self.image_name

    def move(self, dx: float, dy: float):
        """
        Смещает фигуру на заданное расстояние (dx, dy) по осям X и Y относительно её текущей позиции.
        """
        self.set_pos(self.x + dx, self.y + dy)

    def clamp_to_screen(self):
        """
        Ограничивает позицию фигуры границами экрана, не позволяя ей визуально выйти за его пределы.
        """
        fx, fy, fw, fh = self.get_bounds()
        sw, sh = self.screen.get_width(), self.screen.get_height()
        nx, ny = self.x, self.y
        if fx + fw > sw:
            nx = self.x + (sw - (fx + fw))
        elif fx < 0:
            nx = self.x - fx
        if fy + fh > sh:
            ny = self.y + (sh - (fy + fh))
        elif fy < 0:
            ny = self.y - fy
        self.set_pos(nx, ny)

    # ――――――――――――――――――――――――― draw ―――――――――――――――――――――――――
    def draw(self, screen: pygame.Surface, offset: tuple[float, float] = (0.0, 0.0)):
        """
        Отрисовывает фигуру на экране. Принимает опциональный параметр offset для учёта смещения камеры.
        """
        ox, oy = offset
        p = self.params
        draw_x = p[0] + ox
        draw_y = p[1] + oy

        if self.shape == 'rect':
            pygame.draw.rect(screen, self.color, (draw_x, draw_y, p[2], p[3]), self.width)
        elif self.shape == 'circle':
            pygame.draw.circle(screen, self.color, (int(draw_x), int(draw_y)), int(p[2]), self.width)
        elif self.shape == 'ellipse':
            pygame.draw.ellipse(screen, self.color, (draw_x, draw_y, p[2], p[3]), self.width)
        elif self.shape == 'line':
            pygame.draw.line(screen, self.color, (draw_x, draw_y), (p[2] + ox, p[3] + oy), max(1, self.width))
        elif self.shape == 'polygon':
            shifted_pts = [(pt[0] + ox, pt[1] + oy) for pt in p[0]]
            pygame.draw.polygon(screen, self.color, shifted_pts, self.width)
        elif self.shape == 'sprite':
            if self.images and self.image_name and self.image_name in self.images:
                screen.blit(self.images[self.image_name], (int(draw_x), int(draw_y)))

    def set_image(self, image_name: str):
        """
        Меняет изображение спрайта на другое из загруженного набора (работает только для фигур с shape='sprite').
        """
        if self.shape == 'sprite' and self.images and image_name in self.images:
            self.image_name = image_name
            self.params[2] = image_name

    # ――――――――――――――――――――――――― geometry ―――――――――――――――――――――――――
    @property
    def radius(self) -> float:
        """Возвращает радиус фигуры. Работает только для круга. Для остальных форм возвращает 0.0."""
        return float(self.params[2]) if self.shape == 'circle' else 0.0

    def get_center(self) -> tuple[float, float]:
        """
        Возвращает координаты (x, y) геометрического центра фигуры.
        """
        p = self.params
        if self.shape == 'circle':
            return (p[0], p[1])
        if self.shape in ('rect', 'ellipse'):
            return (p[0] + p[2] / 2, p[1] + p[3] / 2)
        if self.shape == 'sprite' and self.images and self.image_name in self.images:
            img = self.images[self.image_name]
            return (p[0] + img.get_width() / 2, p[1] + img.get_height() / 2)
        if self.shape == 'line':
            return ((p[0] + p[2]) / 2, (p[1] + p[3]) / 2)
        return (0.0, 0.0)

    def get_bounds(self) -> tuple[float, float, float, float]:
        """
        Возвращает ограничивающий прямоугольник фигуры в формате (x, y, ширина, высота) для расчетов коллизий.
        """
        p = self.params
        if self.shape in ('rect', 'ellipse'):
            return (p[0], p[1], p[2], p[3])
        if self.shape == 'circle':
            r = p[2]
            return (p[0] - r, p[1] - r, r * 2, r * 2)
        if self.shape == 'sprite' and self.images and self.image_name in self.images:
            img = self.images[self.image_name]
            return (p[0], p[1], float(img.get_width()), float(img.get_height()))
        if self.shape == 'line':
            x1, y1, x2, y2 = p[0], p[1], p[2], p[3]
            w = abs(x2 - x1) or 1.0
            h = abs(y2 - y1) or 1.0
            return (min(x1, x2), min(y1, y2), w, h)
        if self.shape == 'polygon':
            pts = p[0]
            xs = [pt[0] for pt in pts]
            ys = [pt[1] for pt in pts]
            return (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
        return (0.0, 0.0, 0.0, 0.0)

    # ――――――――――――――――――――――――― collision response ―――――――――――――――――――――――――
    def push_out(self, other: Figure):
        """
        Выталкивает текущую фигуру из другой фигуры, если они пересеклись. Используется для физического разрешения коллизий.
        """
        if self.shape == 'circle' and other.shape == 'circle':
            dx = self.x - other.x
            dy = self.y - other.y
            dist = math.hypot(dx, dy)
            min_dist = self.radius + other.radius
            if dist == 0:
                self.set_pos(self.x + min_dist, self.y)
                return
            if dist < min_dist:
                overlap = min_dist - dist
                nx, ny = dx / dist, dy / dist
                self.set_pos(self.x + nx * overlap, self.y + ny * overlap)
            return
            
        x1, y1, w1, h1 = self.get_bounds()
        x2, y2, w2, h2 = other.get_bounds()
        if w1 == 0 or w2 == 0:
            return
            
        ol = (x1 + w1) - x2
        or_ = (x2 + w2) - x1
        ot = (y1 + h1) - y2
        ob = (y2 + h2) - y1
        if ol <= 0 or or_ <= 0 or ot <= 0 or ob <= 0:
            return
            
        m = min(ol, or_, ot, ob)
        if m == ol:
            self.set_pos(self.x - ol, self.y)
        elif m == or_:
            self.set_pos(self.x + or_, self.y)
        elif m == ot:
            self.set_pos(self.x, self.y - ot)
        else:
            self.set_pos(self.x, self.y + ob)