import pygame
import sys
import math
import time
from typing import Literal

from .tilemap import TileMap
from .figure import Figure
from .scene import Scene
from .sound import Sound


# ――――――――――――――――――――――――― type aliases ―――――――――――――――――――――――――

KeyLiteral = Literal[
    'leftMouseButton', 'rightMouseButton', 'middleMouseButton',
    'escape', 'space', 'tab', 'enter',
    'leftCtrl', 'rightCtrl', 'leftShift', 'rightShift', 'leftAlt', 'rightAlt',
    'left', 'right', 'up', 'down',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
]
EventLiteral = Literal['quit', 'pressed', 'keyDown', 'keyUp', 'mouseButtonDown', 'mouseButtonUp', 'mouseMotion']
AlignX = Literal['left', 'middle', 'right']
AlignY = Literal['up', 'middle', 'down']
MouseButton = Literal['leftMouseButton', 'rightMouseButton', 'middleMouseButton']

# draw queue item: either a Figure or a (surface, pos) blit
DrawItem = tuple[Figure | tuple[pygame.Surface, tuple[int, int]], bool]


# ――――――――――――――――――――――――― engine ―――――――――――――――――――――――――


class PyEngine(Sound):

    _KEYS_MAP: dict[str, int] = {
        'escape': pygame.K_ESCAPE, 'space': pygame.K_SPACE,
        'tab': pygame.K_TAB, 'enter': pygame.K_RETURN,
        'leftCtrl': pygame.K_LCTRL, 'rightCtrl': pygame.K_RCTRL,
        'leftShift': pygame.K_LSHIFT, 'rightShift': pygame.K_RSHIFT,
        'leftAlt': pygame.K_LALT, 'rightAlt': pygame.K_RALT,
        'left': pygame.K_LEFT, 'right': pygame.K_RIGHT,
        'up': pygame.K_UP, 'down': pygame.K_DOWN,
        '0': pygame.K_0, '1': pygame.K_1, '2': pygame.K_2, '3': pygame.K_3, '4': pygame.K_4,
        '5': pygame.K_5, '6': pygame.K_6, '7': pygame.K_7, '8': pygame.K_8, '9': pygame.K_9,
        'a': pygame.K_a, 'b': pygame.K_b, 'c': pygame.K_c, 'd': pygame.K_d, 'e': pygame.K_e,
        'f': pygame.K_f, 'g': pygame.K_g, 'h': pygame.K_h, 'i': pygame.K_i, 'j': pygame.K_j,
        'k': pygame.K_k, 'l': pygame.K_l, 'm': pygame.K_m, 'n': pygame.K_n, 'o': pygame.K_o,
        'p': pygame.K_p, 'q': pygame.K_q, 'r': pygame.K_r, 's': pygame.K_s, 't': pygame.K_t,
        'u': pygame.K_u, 'v': pygame.K_v, 'w': pygame.K_w, 'x': pygame.K_x, 'y': pygame.K_y,
        'z': pygame.K_z,
    }
    _MOUSE_MAP: dict[str, int] = {
        'leftMouseButton': 0,
        'middleMouseButton': 1,
        'rightMouseButton': 2,
    }
    _MOUSE_BTN_MAP: dict[str, int] = {
        'leftMouseButton': 1,
        'middleMouseButton': 2,
        'rightMouseButton': 3,
    }
    _EVENT_MAP: dict[str, int] = {
        'keyDown': pygame.KEYDOWN,
        'keyUp': pygame.KEYUP,
        'mouseButtonDown': pygame.MOUSEBUTTONDOWN,
        'mouseButtonUp': pygame.MOUSEBUTTONUP,
        'mouseMotion': pygame.MOUSEMOTION,
    }

    GRID_SNAP_EPSILON: float = 1.0

    # ――――――――――――――――――――――――― init ―――――――――――――――――――――――――

    def __init__(
        self,
        title: str = 'Py-Engine',
        background: tuple = (50, 50, 50),
        width: int = 800,
        height: int = 600,
    ):
        super().__init__()

        self.title = title
        self.width = width
        self.height = height
        self.background = background

        self.fonts: dict[str, pygame.font.Font] = {}
        self.figures: dict[str, Figure] = {}
        self.images: dict[str, pygame.Surface] = {}

        self._draw_queue: list[DrawItem] = []
        self._cooldowns: dict[str, float] = {}

        self._scenes: dict[str, Scene] = {}
        self._current_scene: Scene | None = None
        self._next_scene: tuple[str, dict, bool] | None = None

        self.screen: pygame.Surface | None = None
        self.clock: pygame.time.Clock | None = None
        self.seconds: float = 0.0
        self.dt: float = 0.0
        self.is_running: bool = False
        self._start_ticks: int = 0

        self.animations: dict[str, dict] = {}

        self._tilemaps: dict[str, 'TileMap'] = {}
        self._grid_targets: dict[str, tuple[float, float]] = {}
        self._camera_target: str | None = None
        self._camera_offset: tuple[float, float] = (0.0, 0.0)
        self._camera_bounds: tuple[str, any] | None = None  # ('map', TileMap) или ('window', None)

    @property
    def camera_offset(self) -> tuple[float, float]:
        """Публичный доступ к смещению камеры"""
        return self._camera_offset

    def initialize(self, start_scene: str | None = None):
        """
        Инициализирует подсистемы pygame, создает окно рендеринга, настраивает таймер и переводит движок в состояние готовности к работе.
        - start_scene (str | None): Имя предварительно зарегистрированной сцены, на которую нужно переключиться сразу после запуска.
        """
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self.clock = pygame.time.Clock()
        self.is_running = True
        if start_scene and start_scene in self._scenes:
            self._next_scene = (start_scene, {}, True)

    # ――――――――――――――――――――――――― loop ―――――――――――――――――――――――――

    def run(self):
        """
        Запускает главный игровой цикл. Берет на себя обработку событий, вызов update/draw сцен, расчет дельты времени (dt), очистку экрана, отрисовку очереди и ограничение FPS. 
        Блокирующий метод, работает до закрытия окна.
        """
        self._start_ticks = pygame.time.get_ticks()
        self._switch_scene()

        while self.is_running:
            self._process_events()
            self.seconds = (pygame.time.get_ticks() - self._start_ticks) / 1000
            self.dt = self.clock.tick(60) / 1000
            self._update_animations()
            self.screen.fill(self.background)

            if self._current_scene:
                self._current_scene.update()
                self._current_scene.draw()
            else:
                self.update()

            self._update_camera()
            self._flush_draw_queue()
            self._switch_scene()
            pygame.display.flip()

        self._quit()

    def _process_events(self):
        for event in pygame.event.get():
            if self._current_scene:
                self._current_scene.events(event)
            else:
                self.events(event)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _flush_draw_queue(self):
        ox, oy = self._camera_offset
        for item, use_camera in self._draw_queue:
            actual_ox, actual_oy = (ox, oy) if use_camera else (0.0, 0.0)
            if isinstance(item, Figure):
                item.draw(self.screen, offset=(actual_ox, actual_oy))
            else:
                self.screen.blit(item[0], (item[1][0] + actual_ox, item[1][1] + actual_oy))
        self._draw_queue.clear()

    def _quit(self):
        pygame.quit()
        sys.exit()

    def update(self):
        """Пользовательская логика"""
        pass

    def events(self, event: pygame.event.Event):
        """Пользовательские события"""
        pass

    # ――――――――――――――――――――――――― scenes ―――――――――――――――――――――――――

    def add_scene(self, name: str, scene: Scene):
        """
        Регистрирует экземпляр сцены в менеджере движка под уникальным именем для последующего переключения.
        - name (str): Строковый идентификатор сцены.
        - scene (Scene): Экземпляр класса, наследующего от базового класса Scene.
        """
        if not isinstance(scene, Scene):
            raise TypeError("scene must be a Scene instance")
        self._scenes[name] = scene

    def add_scenes(self, scenes: dict[str, Scene]):
        """
        Позволяет массово зарегистрировать несколько сцен, передав их в виде словаря.
        - scenes (dict[str, Scene]): Словарь, где ключи — имена сцен, а значения — их экземпляры.
        """
        for name, scene in scenes.items():
            self.add_scene(name, scene)

    def set_scene(self, name: str, destroy: bool = True, **kwargs):
        """
        Планирует безопасное переключение на указанную сцену в конце текущего кадра. Вызывает on_exit у текущей сцены и on_enter у новой.
        - name (str): Имя целевой сцены.
        - destroy (bool): Если True, полностью очищает словарь фигур (clear_figures) при выходе из старой сцены.
        - **kwargs: Словарь аргументов, который будет передан в метод on_enter новой сцены.
        """
        if name not in self._scenes:
            raise ValueError(f"scene '{name}' not registered")
        self._next_scene = (name, kwargs, destroy)

    def _switch_scene(self):
        if self._next_scene is None:
            return
        name, kwargs, destroy = self._next_scene
        self._next_scene = None

        if self._current_scene:
            self._current_scene.on_exit()
            if destroy:
                self.clear_figures()

        self._current_scene = self._scenes.get(name)
        if self._current_scene:
            self._current_scene.on_enter(**kwargs)

    # ――――――――――――――――――――――――― figures ―――――――――――――――――――――――――

    def create_figure(
        self,
        name: str,
        shape: Literal['rect', 'circle', 'ellipse', 'line', 'polygon', 'sprite'],
        color: tuple,
        params: tuple,
        width: int = 0,
        auto_draw: bool = False,
        use_camera: bool = True
    ):
        """
        Создает графический примитив или спрайт, инициализирует его геометрию и регистрирует в движке.
        - name (str): Уникальное имя фигуры для дальнейшего взаимодействия (движение, коллизии).
        - shape (Literal): Тип формы ('rect', 'circle', 'ellipse', 'line', 'polygon', 'sprite').
        - color (tuple): Цвет в формате RGB.
        - params (tuple): Геометрические параметры. Зависят от shape: (x,y,w,h) для rect, (x,y,r) для circle, (x,y,img_name) для sprite и т.д.
        - width (int): Толщина обводки. 0 означает сплошную заливку.
        - auto_draw (bool): Если True, фигура автоматически добавляется в очередь отрисовки на каждый кадр.
        - use_camera (bool): Двигаться с камерой.
        
        Figures param
        -------------
        :rect:    (x, y, w, h)
        :circle:  (x, y, radius)
        :ellipse: (x, y, w, h)
        :line:    (x1, y1, x2, y2)  — width must be > 0
        :polygon: ([points],)
        :sprite:  (x, y, image_name)
        """
        self.figures[name] = Figure(self.screen, shape, color, params, width, images=self.images, use_camera=use_camera)
        if auto_draw:
            self.draw_figure(name)

    def draw_figure(self, name: str):
        """
        Добавляет указанную фигуру в очередь отрисовки (_draw_queue) для текущего кадра.
        - name (str): Имя фигуры, которую нужно отрисовать.
        """
        if name in self.figures:
            fig = self.figures[name]
            self._draw_queue.append((fig, fig.use_camera))

    def remove_figure(self, name: str):
        """
        Удаляет фигуру из памяти движка, освобождая ссылку на неё.
        - name (str): Имя удаляемой фигуры.
        """
        self.figures.pop(name, None)

    def clear_figures(self):
        """
        Полностью очищает внутренний словарь всех зарегистрированных фигур. Обычно вызывается автоматически при смене сцен.
        """
        self.figures.clear()

    # ――――――――――――――――――――――――― text / fonts ―――――――――――――――――――――――――

    def create_font(self, name: str, font: str = 'Arial', size: int = 36):
        """
        Инициализирует системный шрифт заданного размера и кэширует его в движке для многократного использования.
        - name (str): Имя-идентификатор для доступа к шрифту.
        - font (str): Название системного шрифта (например, 'Arial', 'Courier New').
        - size (int): Размер шрифта в пунктах.
        """
        self.fonts[name] = pygame.font.SysFont(font, size)

    def draw_text(
        self,
        font: str,
        text: str,
        x: int,
        y: int,
        color: tuple = (0, 0, 0),
        antialias: bool = True,
        use_camera: bool = False
    ):
        """
        Рендерит текстовую строку в поверхность и добавляет её в очередь отрисовки.
        - font (str): Имя предварительно созданного шрифта.
        - text (str): Отображаемый текст.
        - x, y (int): Координаты верхнего левого угла текста на экране.
        - color (tuple): Цвет текста в RGB.
        - antialias (bool): Включить ли сглаживание шрифта (рекомендуется True).
        - use_camera (bool): Двигаться с камерой.
        """
        surface = self.fonts[font].render(text, antialias, color)
        self._draw_queue.append(((surface, (x, y)), use_camera))

    def draw_text_on_figure(self, fig_name: str, font: str, text: str, color: tuple = (0, 0, 0), use_camera: bool = False):
        """
        Автоматически вычисляет геометрический центр фигуры и отрисовывает текст строго по нему.
        - fig_name (str): Имя фигуры-подложки.
        - font (str): Имя шрифта.
        - text (str): Текст.
        - color (tuple): Цвет текста.
        - use_camera (bool): Двигаться с камерой.
        """
        if fig_name not in self.figures:
            return
        cx, cy = self.figures[fig_name].get_center()
        tw, th = self.fonts[font].size(text)
        self.draw_text(font, text, int(cx - tw / 2), int(cy - th / 2), color, use_camera=use_camera)

    def draw_overlay(self, color: tuple = (0, 0, 0), alpha: int = 180):
        """
        Рисует полупрозрачный прямоугольник поверх всего экрана. Идеально для создания эффекта паузы или затемнения фона при открытии меню.
        - color (tuple): Цвет затемнения (обычно черный).
        - alpha (int): Уровень непрозрачности от 0 (прозрачный) до 255 (глухой).
        """
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(alpha)
        overlay.fill(color)
        self._draw_queue.append(((overlay, (0, 0)), False))

    # ――――――――――――――――――――――――― images ―――――――――――――――――――――――――

    def load_image(self, name: str, path: str):
        """
        Загружает изображение с диска, конвертирует его для быстрого рендеринга и сохраняет в кэш движка.
        - name (str): Идентификатор изображения.
        - path (str): Путь к файлу на диске.
        """
        self.images[name] = pygame.image.load(path).convert_alpha()

    def scale_image(self, name: str, scale: float):
        """
        Пропорционально масштабирует изображение относительно его текущего размера.
        - name (str): Имя изображения.
        - scale (float): Коэффициент масштабирования (например, 0.5 для уменьшения вдвое, 2.0 для увеличения).
        """
        if name in self.images:
            img = self.images[name]
            self.images[name] = pygame.transform.smoothscale(
                img, (int(img.get_width() * scale), int(img.get_height() * scale))
            )

    def resize_image(self, name: str, width: int, height: int):
        """
        Изменяет размер изображения до точных пиксельных значений, игнорируя исходные пропорции.
        - name (str): Имя изображения.
        - width, height (int): Новые целевые размеры в пикселях.
        """
        if name in self.images:
            self.images[name] = pygame.transform.smoothscale(self.images[name], (width, height))

    def flip_image(self, name: str, new_name: str, flip_x: bool = False, flip_y: bool = False):
        """
        Зеркально отражает изображение по заданным осям и сохраняет результат как новую копию, не затрагивая оригинал.
        - name (str): Имя исходного изображения.
        - new_name (str): Имя для сохраненной копии.
        - flip_x, flip_y (bool): Флаги отражения по горизонтали и вертикали.
        """
        if name in self.images:
            self.images[new_name] = pygame.transform.flip(self.images[name], flip_x, flip_y)

    def rotate_image(self, name: str, new_name: str, angle: float):
        """
        Поворачивает изображение на заданный угол и сохраняет результат как новую копию.
        - name (str): Имя исходного изображения.
        - new_name (str): Имя для сохраненной копии.
        - angle (float): Угол поворота в градусах (против часовой стрелки).
        """
        if name in self.images:
            self.images[new_name] = pygame.transform.rotate(self.images[name], angle)

    # ――――――――――――――――――――――――― animations ―――――――――――――――――――――――――

    def add_animation(self, name: str, frames: list[str], fps: float = 8.0, loop: bool = True):
        """
        Регистрирует анимацию для использования фигурами.
        - name (str): Уникальное имя анимации.
        - frames (list[str]): Список имен изображений (кадров), загруженных через load_image.
        - fps (float): Количество кадров в секунду.
        - loop (bool): Зацикливать ли анимацию. Если False, остановится на последнем кадре.
        """
        self.animations[name] = {'frames': frames, 'fps': fps, 'loop': loop}

    def _update_animations(self):
        """Автоматически обновляет кадры анимаций для всех фигур."""
        for fig in self.figures.values():
            fig._update_animation(self.animations, self.dt)

    # ――――――――――――――――――――――――― input ―――――――――――――――――――――――――

    def get_event(
        self,
        event: pygame.event.Event,
        etype: EventLiteral = 'keyDown',
        key: KeyLiteral | None = None,
    ) -> bool:
        """
        Проверяет, соответствует ли переданное событие pygame заданному типу и конкретной клавише/кнопке.
        - event (Event): Объект события из цикла обработки pygame.
        - etype (EventLiteral): Тип ожидаемого события ('keyDown', 'mouseButtonDown' и т.д.).
        - key (KeyLiteral | None): Конкретная клавиша или кнопка мыши. Если None, проверяется только тип события.
        """
        if etype == 'quit':
            return event.type == pygame.QUIT

        expected = self._EVENT_MAP.get(etype)
        if expected is None or event.type != expected:
            return False

        if key is None:
            return True

        if etype in ('mouseButtonDown', 'mouseButtonUp'):
            return event.button == self._MOUSE_BTN_MAP.get(key)

        return event.key == self._KEYS_MAP.get(key)

    def is_pressed(self, key: KeyLiteral) -> bool:
        """
        Возвращает статус удержания клавиши клавиатуры или кнопки мыши в данный конкретный момент (не событие, а состояние).
        - key (KeyLiteral): Имя клавиши или кнопки мыши.
        """
        if key in self._MOUSE_MAP:
            return bool(pygame.mouse.get_pressed()[self._MOUSE_MAP[key]])
        k = self._KEYS_MAP.get(key)
        return k is not None and bool(pygame.key.get_pressed()[k])

    def is_mouse_over(self, name: str, cooldown: float = 0.0) -> bool:
        """
        Проверяет, находится ли курсор мыши в пределах ограничивающего прямоугольника (bounding box) указанной фигуры.
        - name (str): Имя фигуры.
        - cooldown (float): Опциональный кулдаун (в секундах). Если > 0, метод будет возвращать True не чаще указанного интервала (защита от дребезга при наведении).
        """
        if not self._is_mouse_over(name):
            return False
        if cooldown > 0 and not self.check_cooldown(f'_hover_{name}', cooldown):
            return False
        return True

    def _is_mouse_over(self, name: str) -> bool:
        if name not in self.figures:
            return False
        fx, fy, fw, fh = self.figures[name].get_bounds()
        if fw == 0 or fh == 0:
            return False
        mx, my = pygame.mouse.get_pos()
        return fx <= mx <= fx + fw and fy <= my <= fy + fh

    def is_clicked(
        self,
        name: str,
        cooldown: float = 0.0,
        button: MouseButton = 'leftMouseButton',
    ) -> bool:
        """
        Проверяет факт нажатия кнопки мыши, когда курсор находится над фигурой. Встроенный кулдаун предотвращает множественные срабатывания.
        - name (str): Имя фигуры.
        - cooldown (float): Интервал кулдауна в секундах.
        - button (MouseButton): Кнопка мыши ('leftMouseButton', 'rightMouseButton', 'middleMouseButton').
        """
        if not self._is_mouse_over(name):
            return False
        if not pygame.mouse.get_pressed()[self._MOUSE_MAP.get(button, 0)]:
            return False
        if cooldown > 0 and not self.check_cooldown(f'_click_{name}_{button}', cooldown):
            return False
        return True

    # ――――――――――――――――――――――――― collision ―――――――――――――――――――――――――

    def _figures_collide(self, f1: Figure, f2: Figure) -> bool:
        # Круг vs Круг
        if f1.shape == 'circle' and f2.shape == 'circle':
            return math.hypot(f1.x - f2.x, f1.y - f2.y) < (f1.radius + f2.radius)
        
        # Круг vs Прямоугольник (или наоборот)
        if f1.shape == 'circle' and f2.shape in ('rect', 'ellipse', 'sprite'):
            cx, cy = f1.x, f1.y
            rx, ry, rw, rh = f2.get_bounds()
            closest_x = max(rx, min(cx, rx + rw))
            closest_y = max(ry, min(cy, ry + rh))
            return math.hypot(cx - closest_x, cy - closest_y) < f1.radius
        
        if f2.shape == 'circle' and f1.shape in ('rect', 'ellipse', 'sprite'):
            cx, cy = f2.x, f2.y
            rx, ry, rw, rh = f1.get_bounds()
            closest_x = max(rx, min(cx, rx + rw))
            closest_y = max(ry, min(cy, ry + rh))
            return math.hypot(cx - closest_x, cy - closest_y) < f2.radius
        
        # Прямоугольник vs Прямоугольник (AABB)
        x1, y1, w1, h1 = f1.get_bounds()
        x2, y2, w2, h2 = f2.get_bounds()
        return not (x1 > x2 + w2 or x1 + w1 < x2 or y1 > y2 + h2 or y1 + h1 < y2)

    def check_collision(self, name1: str, name2: str, cooldown: float = 0.5) -> bool:
        """
        Проверяет факт геометрического пересечения двух фигур. Использует временные метки для реализации кулдауна, чтобы предотвратить многократное срабатывание в течение одного "контакта".
        - name1, name2 (str): Имена проверяемых фигур.
        - cooldown (float): Время в секундах, на которое блокируется повторное возвращение True после успешного столкновения.
        """
        if name1 not in self.figures or name2 not in self.figures:
            return False
        f1, f2 = self.figures[name1], self.figures[name2]
        if not self._figures_collide(f1, f2):
            return False
        now = time.time()
        if now - max(f1.last_contact_time, f2.last_contact_time) < cooldown:
            return False
        f1.last_contact_time = f2.last_contact_time = now
        return True

    def can_move_to(
        self, name: str, new_x: float, new_y: float, obstacles: list[str]
    ) -> tuple[bool, float, float]:
        """
        Симулирует перемещение фигуры в новые координаты и проверяет, не возникнет ли коллизия с указанными препятствиями. Если коллизия есть, отменяет перемещение.
        - name (str): Имя фигуры.
        - new_x, new_y (float): Проектируемые координаты.
        - obstacles (list): Список имен фигур-препятствий.
        """
        if name not in self.figures:
            return False, new_x, new_y
        fig = self.figures[name]
        old_x, old_y = fig.x, fig.y
        fig.set_pos(new_x, new_y)
        for obs_name in obstacles:
            if obs_name == name or obs_name not in self.figures:
                continue
            if self._figures_collide(fig, self.figures[obs_name]):
                fig.set_pos(old_x, old_y)
                return False, old_x, old_y
        return True, new_x, new_y

    def resolve_collisions(self, movers: list[str], walls: list[str]):
        """
        Метод массового выталкивания (push-out). Итерирует список движущихся объектов и выталкивает их наружу, если они пересекаются с любым объектом из списка стен.
        - movers (list): Имена фигур, которые нужно вытолкнуть (динамические объекты).
        - walls (list): Имена фигур, выступающих в роли препятствий (статичные объекты).
        """
        for n1 in movers:
            if n1 not in self.figures:
                continue
            f1 = self.figures[n1]
            for n2 in walls:
                if n2 == n1 or n2 not in self.figures:
                    continue
                f2 = self.figures[n2]
                if self._figures_collide(f1, f2):
                    f1.push_out(f2)

    # ――――――――――――――――――――――――― cooldowns ―――――――――――――――――――――――――

    def check_cooldown(self, name: str, seconds: float) -> bool:
        """
        Внутренний механизм таймеров. Проверяет, прошло ли заданное время с момента последнего вызова. Если да — перезапускает отсчет и возвращает True. Иначе возвращает False.
        - name (str): Уникальный строковый идентификатор таймера.
        - seconds (float): Длительность кулдауна в секундах.
        """
        now = time.time()
        if now - self._cooldowns.get(name, 0) >= seconds:
            self._cooldowns[name] = now
            return True
        return False

    # ――――――――――――――――――――――――― movement helpers ―――――――――――――――――――――――――

    def move_towards(
        self,
        current_x: float, current_y: float,
        target_x: float, target_y: float,
        speed: float = 0.1,
    ) -> tuple[int, int]:
        """
        Выполняет линейную интерполяцию (lerp) координат для плавного, затухающего приближения к цели.
        - current_x, current_y (float): Текущие координаты.
        - target_x, target_y (float): Целевые координаты.
        - speed (float): Коэффициент интерполяции от 0.0 до 1.0 (где 1.0 — мгновенное перемещение).
        """
        return (
            int(current_x + (target_x - current_x) * speed),
            int(current_y + (target_y - current_y) * speed),
        )

    def move_at_speed(
        self,
        current_x: float, current_y: float,
        target_x: float, target_y: float,
        speed: float = 5.0,
    ) -> tuple[int, int]:
        """
        Вычисляет новую точку на пути к цели, смещаясь ровно на заданное расстояние в пикселях за один вызов (равномерное движение).
        - current_x, current_y (float): Текущие координаты.
        - target_x, target_y (float): Целевые координаты.
        - speed (float): Точное смещение в пикселях за один вызов метода.
        """
        dx = target_x - current_x
        dy = target_y - current_y
        dist = math.hypot(dx, dy)
        if dist < speed:
            return int(target_x), int(target_y)
        ratio = speed / dist
        return int(current_x + dx * ratio), int(current_y + dy * ratio)

    # ――――――――――――――――――――――――― layout helpers ―――――――――――――――――――――――――

    def get_text_pos(
        self,
        font: str,
        text: str,
        align_x: AlignX,
        align_y: AlignY,
        offset_x: int = 0,
        offset_y: int = 0,
    ) -> tuple[int, int]:
        """
        Вычисляет точные координаты (x, y) для отрисовки текста с учетом его размеров, выравнивания относительно экрана и опционального смещения.
        - font (str): Имя шрифта (необходим для расчета ширины и высоты текста).
        - text (str): Сам текст.
        - align_x, align_y (Literal): Горизонтальное ('left', 'middle', 'right') и вертикальное ('up', 'middle', 'down') выравнивание.
        - offset_x, offset_y (int): Дополнительное смещение в пикселях от рассчитанной точки.
        """
        tw, th = self.fonts[font].size(text)
        x = {'left': 0, 'middle': (self.width - tw) // 2, 'right': self.width - tw}.get(align_x, 0)
        y = {'up': 0, 'middle': (self.height - th) // 2, 'down': self.height - th}.get(align_y, 0)
        return (x + offset_x, y + offset_y)

    def get_shape_pos(
        self,
        shape_w: int,
        shape_h: int,
        align_x: AlignX,
        align_y: AlignY,
        offset_x: int = 0,
        offset_y: int = 0,
    ) -> tuple[int, int]:
        """
        Вычисляет координаты (x, y) для размещения геометрической фигуры с учетом её размеров и выравнивания относительно экрана.
        - shape_w, shape_h (int): Ширина и высота фигуры.
        - align_x, align_y (Literal): Горизонтальное и вертикальное выравнивание.
        - offset_x, offset_y (int): Дополнительное смещение в пикселях.
        """
        x = {'left': 0, 'middle': (self.width - shape_w) // 2, 'right': self.width - shape_w}.get(align_x, 0)
        y = {'up': 0, 'middle': (self.height - shape_h) // 2, 'down': self.height - shape_h}.get(align_y, 0)
        return (x + offset_x, y + offset_y)

    # ――――――――――――――――――――――――― tilemap & camera ―――――――――――――――――――――――――
    def _update_camera(self):
        """Автоматически вычисляет смещение камеры с ограничением по границам"""
        if self._camera_target and self._camera_target in self.figures:
            fig = self.figures[self._camera_target]
            cx, cy = fig.get_center()
            offset_x = self.width / 2 - cx
            offset_y = self.height / 2 - cy
            
            if self._camera_bounds:
                bounds_type, bounds_data = self._camera_bounds
                if bounds_type == 'map' and bounds_data is not None:
                    tmap = bounds_data
                    map_width = tmap.width * tmap.tileset.tile_width
                    map_height = tmap.height * tmap.tileset.tile_height
                    if map_width < self.width: offset_x = (self.width - map_width) / 2
                    else: offset_x = max(min(offset_x, 0), self.width - map_width)
                    if map_height < self.height: offset_y = (self.height - map_height) / 2
                    else: offset_y = max(min(offset_y, 0), self.height - map_height)
                elif bounds_type == 'window':
                    offset_x = min(offset_x, 0)
                    offset_y = min(offset_y, 0)
            self._camera_offset = (offset_x, offset_y)
        else:
            self._camera_offset = (0.0, 0.0)

    def set_camera_bounds(self, bounds_type: Literal['map', 'window'], bounds_data=None):
        """
        Устанавливает границы для камеры.
        - 'map': камера ограничена границами карты (передайте TileMap)
        - 'window': камера не уходит в отрицательные координаты
        """
        self._camera_bounds = (bounds_type, bounds_data)

    def add_tilemap(self, name: str, tilemap: 'TileMap'):
        """
        Регистрирует карту тайлов в движке под указанным именем, чтобы методы движения (move) могли автоматически учитывать её для коллизий.
        - name (str): Имя для обращения к карте.
        - tilemap (TileMap): Экземпляр карты.
        """
        self._tilemaps[name] = tilemap

    def set_camera_target(self, figure_name: str):
        """
        Привязывает виртуальную камеру к фигуре. Движок будет автоматически вычислять смещение (offset) так, чтобы указанная фигура всегда находилась в центре экрана.
        - figure_name (str): Имя фигуры-цели.
        """
        self._camera_target = figure_name

    # ――――――――――――――――――――――――― smart movement & collisions ―――――――――――――――――――――――――
    def move(
        self,
        name: str,
        speed: float,
        dx: float = 0.0,
        dy: float = 0.0,
        target: tuple[float, float] | None = None,
        map_name: str | None = None,
        obstacles: list[str] | None = None,
        use_dt: bool = True,
        grid_mode: bool = False
    ):
        """
        Универсальный метод перемещения фигуры. Автоматически умножает скорость на dt, вычисляет вектор движения и разрешает коллизии (выталкивание) с тайлами карты или другими фигурами.
        - name (str): Имя перемещаемой фигуры.
        - speed (float): Скорость (пикселей в секунду, если use_dt=True; или пикселей за кадр, если use_dt=False).
        - dx, dy (float): Вектор направления (например, -1.0, 0.0, 1.0).
        - target (tuple | None): Координаты (x, y) цели. Если указаны, игнорирует dx/dy и плавно стремится к цели.
        - map_name (str | None): Имя TileMap для проверки коллизий с твердыми тайлами.
        - obstacles (list | None): Список имен фигур, с которыми нужно сталкиваться (выталкиваться).
        - use_dt (bool): Учитывать ли дельту времени. False используется для UI-анимаций, где важна стабильность, а не физическая скорость.
        - grid_mode: если True, включает пошаговое движение от центра тайла к центру тайла.
        """
        if name not in self.figures: return
        fig = self.figures[name]

        # --- РЕЖИМ ПОТАГОВОГО ДВИЖЕНИЯ ПО СЕТКЕ ---
        if grid_mode and map_name and map_name in self._tilemaps:
            tmap = self._tilemaps[map_name]
            tw, th = tmap.tileset.tile_width, tmap.tileset.tile_height

            # Текущий тайл фигуры (считаем по её центру)
            cx, cy = fig.get_center()
            current_tx = int(cx // tw)
            current_ty = int(cy // th)

            # Центр текущего тайла
            center_x = current_tx * tw + tw / 2
            center_y = current_ty * th + th / 2

            # Проверяем, находится ли фигура в центре тайла
            in_center = (
                abs(fig.x - center_x) < self.GRID_SNAP_EPSILON and
                abs(fig.y - center_y) < self.GRID_SNAP_EPSILON
            )

            # Если в центре и есть ввод — ищем новую цель
            if in_center and (dx != 0 or dy != 0):
                step_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
                step_y = 1 if dy > 0 else (-1 if dy < 0 else 0)

                target_tx = current_tx + step_x
                target_ty = current_ty + step_y

                # Проверяем, можно ли туда пойти
                if not tmap.is_solid(target_tx, target_ty, figure_name=name):
                    target_x = target_tx * tw + tw / 2
                    target_y = target_ty * th + th / 2
                    self._grid_targets[name] = (target_x, target_y)

            # Если есть активная цель — двигаемся к ней
            if name in self._grid_targets:
                tx, ty = self._grid_targets[name]
                effective_speed = speed * self.dt if use_dt else speed

                new_x, new_y = self.move_at_speed(fig.x, fig.y, tx, ty, effective_speed)
                fig.set_pos(new_x, new_y)

                # Если дошли до цели — фиксируем позицию и удаляем цель
                if (
                    abs(fig.x - tx) < self.GRID_SNAP_EPSILON and
                    abs(fig.y - ty) < self.GRID_SNAP_EPSILON
                ):
                    fig.set_pos(tx, ty)
                    del self._grid_targets[name]

            return  # Завершаем метод

        # --- СТАНДАРТНОЕ НЕПРЕРЫВНОЕ ДВИЖЕНИЕ ---
        if target is not None:
            tx, ty = target
            effective_speed = speed * self.dt if use_dt else speed
            new_x, new_y = self.move_at_speed(fig.x, fig.y, tx, ty, effective_speed)
            actual_dx = new_x - fig.x
            actual_dy = new_y - fig.y
        else:
            mult = self.dt if use_dt else 1.0
            actual_dx = dx * speed * mult
            actual_dy = dy * speed * mult

        # Используем set_pos вместо прямой модификации
        fig.set_pos(fig.x + actual_dx, fig.y)
        self._resolve_collisions_for_move(fig, name, actual_dx, 'x', map_name, obstacles)

        fig.set_pos(fig.x, fig.y + actual_dy)
        self._resolve_collisions_for_move(fig, name, actual_dy, 'y', map_name, obstacles)

    def _resolve_collisions_for_move(
        self,
        fig: Figure,
        fig_name: str,
        d: float,
        axis: str,
        map_name: str | None,
        obstacles: list[str] | None
    ):
        fx, fy, fw, fh = fig.get_bounds()

        # --- Коллизии с TileMap ---
        if map_name and map_name in self._tilemaps:
            tilemap = self._tilemaps[map_name]
            tw, th = tilemap.tileset.tile_width, tilemap.tileset.tile_height
            start_x, end_x = int(fx // tw), int((fx + fw) // tw)
            start_y, end_y = int(fy // th), int((fy + fh) // th)

            for ty in range(start_y, end_y + 1):
                for tx in range(start_x, end_x + 1):
                    if tilemap.is_solid(tx, ty, figure_name=fig_name):
                        tile_rect = pygame.Rect(tx * tw, ty * th, tw, th)
                        fig_rect = pygame.Rect(fig.x, fig.y, fw, fh)

                        if fig_rect.colliderect(tile_rect):
                            if axis == 'x':
                                new_x = tile_rect.left - fw if d > 0 else tile_rect.right
                                fig.set_pos(new_x, fig.y)
                            else:
                                new_y = tile_rect.top - fh if d > 0 else tile_rect.bottom
                                fig.set_pos(fig.x, new_y)
                            fx, fy, fw, fh = fig.get_bounds()

        # --- Коллизии с другими фигурами ---
        if obstacles:
            for obs_name in obstacles:
                if obs_name == fig_name or obs_name not in self.figures:
                    continue
                obs_fig = self.figures[obs_name]
                if self._figures_collide(fig, obs_fig):
                    fig.push_out(obs_fig)
                    fx, fy, fw, fh = fig.get_bounds()

    def clamp_to_map(self, name: str, map_name: str):
        """
        Ограничивает координаты фигуры физическими границами указанной TileMap, не позволяя ей выйти за пределы карты.
        - name (str): Имя фигуры.
        - map_name (str): Имя карты.
        """
        if name not in self.figures or map_name not in self._tilemaps: return
        fig = self.figures[name]
        tmap = self._tilemaps[map_name]
        
        max_x = tmap.width * tmap.tileset.tile_width - fig.get_bounds()[2]
        max_y = tmap.height * tmap.tileset.tile_height - fig.get_bounds()[3]
        
        fig.x = max(0, min(fig.x, max_x))
        fig.y = max(0, min(fig.y, max_y))
        fig.params[0], fig.params[1] = fig.x, fig.y

    def check_tile_collision(self, name: str, map_name: str, tile_id: int, layer_index: int | None = None) -> bool:
        """
        Проверяет пересечение фигуры с тайлом указанного ID.
        Если layer_index не указан, проверяет слой collision_layer_index.
        """
        if name not in self.figures or map_name not in self._tilemaps: return False
        fig = self.figures[name]
        tmap = self._tilemaps[map_name]
        
        target_layer = layer_index if layer_index is not None else tmap.collision_layer_index
        
        fx, fy, fw, fh = fig.get_bounds()
        tw, th = tmap.tileset.tile_width, tmap.tileset.tile_height
        
        for ty in range(int(fy // th), int((fy + fh) // th) + 1):
            for tx in range(int(fx // tw), int((fx + fw) // tw) + 1):
                if tmap.get_tile(tx, ty, target_layer) == tile_id:
                    return True
        return False