# PyEngine

Библиотека для создания 2D-игр на Python, построенная поверх pygame. PyEngine не заменяет pygame — он дополняет его, беря на себя рутинные задачи: управление окном, обработку ввода, коллизии, камеры, очереди отрисовки, анимации и работу со сценами.

Вместо того чтобы каждый раз писать цикл обработки событий, считать дельту времени, вручную проверять пересечения прямоугольников и сдвигать координаты для камеры, ты получаешь готовые методы. Если чего-то не хватает — всегда можно обратиться напрямую к pygame.

## Установка

Скопируй папку `pyengine` в свой проект и импортируй нужные модули:

```python
from pyengine.engine import PyEngine
from pyengine.assets import Assets
from pyengine.scene import Scene
from pyengine.tilemap import Tile, TileSet, TileMap
```

---

## Assets

Класс с предустановленными цветами и шрифтами, чтобы не гуглить RGB-значения и не помнить названия системных шрифтов.

```python
from pyengine.assets import Assets

# Использование констант
engine.create_figure('player', 'rect', Assets.BLUE, (100, 100, 32, 32))
engine.create_font('title', Assets.FONT_ARIAL, 48)

# Утилиты для работы с цветами
dark_red = Assets.darken(Assets.RED, 0.7)
light_blue = Assets.lighten(Assets.BLUE, 1.3)
random = Assets.random_color()
```

### Константы
**Цвета:** `WHITE`, `BLACK`, `RED`, `GREEN`, `BLUE`, `YELLOW`, `CYAN`, `MAGENTA`, `GRAY`, `DARK_GRAY`, `ORANGE`, `PURPLE`
**Шрифты:** `FONT_ARIAL`, `FONT_COMIC`, `FONT_TIMES`, `FONT_COURIER`

### Методы
**get_color(name)**
Возвращает кортеж цвета по строковому имени. Если цвет не найден, возвращает чёрный.
- `name` (str): название цвета, например `'red'`, `'dark_gray'`.

**random_color()**
Генерирует случайный цвет в формате (R, G, B).

**darken(color, factor=0.7)**
Затемняет цвет, умножая каждую RGB-компоненту на коэффициент.
- `color` (tuple): исходный цвет.
- `factor` (float): коэффициент затемнения (0.7 = темнее на 30%).

**lighten(color, factor=1.3)**
Осветляет цвет, умножая каждую RGB-компоненту на коэффициент, но не даёт превысить 255.
- `color` (tuple): исходный цвет.
- `factor` (float): коэффициент осветления (1.3 = ярче на 30%).

---

## Sound

Миксин для работы со звуками и музыкой. Автоматически подключается к `PyEngine`, поэтому все методы доступны через `engine`.

```python
# Загрузка и воспроизведение звуков
engine.load_sound('jump', 'sounds/jump.wav')
engine.play_sound('jump')

# Фоновая музыка
engine.load_music('music/theme.ogg')
engine.play_music(loop=True)
engine.set_music_volume(0.5)
```

### Звуковые эффекты
**load_sound(name, path)**
Загружает звуковой эффект из файла и сохраняет под указанным именем.
- `name` (str): идентификатор звука.
- `path` (str): путь к файлу.

**play_sound(name, loop=False)**
Воспроизводит загруженный звуковой эффект.
- `name` (str): имя звука.
- `loop` (bool): если True, зацикливает воспроизведение.

**stop_sound(name)**
Останавливает воспроизведение звукового эффекта.
- `name` (str): имя звука.

**set_sound_volume(name, volume)**
Устанавливает громкость конкретного звукового эффекта.
- `name` (str): имя звука.
- `volume` (float): громкость от 0.0 до 1.0.

### Музыка
**load_music(path)**
Загружает фоновую музыку из файла. Можно загрузить только один трек одновременно.
- `path` (str): путь к файлу.

**play_music(loop=False)**
Запускает воспроизведение загруженной музыки.
- `loop` (bool): если True, зацикливает музыку.

**stop_music()**
Полностью останавливает музыку.

**pause_music()**
Приостанавливает воспроизведение музыки. Продолжить можно через `resume_music`.

**resume_music()**
Продолжает воспроизведение музыки с момента паузы.

**set_music_volume(volume)**
Устанавливает громкость фоновой музыки.
- `volume` (float): громкость от 0.0 до 1.0.

**fade_in_music(seconds=2.0, loop=False)**
Запускает музыку с плавным нарастанием громкости от нуля.
- `seconds` (float): длительность нарастания в секундах.
- `loop` (bool): зацикливать ли музыку.

**fade_out_music(seconds=2.0)**
Плавно затухает музыку до тишины за указанное время.
- `seconds` (float): длительность затухания в секундах.

**set_all_volume(volume)**
Устанавливает одну громкость сразу для всех звуков и музыки.
- `volume` (float): громкость от 0.0 до 1.0.

---

## Scene

Базовый класс для создания сцен. Сцена — это отдельный экран игры: меню, уровень, пауза, game over. Каждая сцена имеет свой жизненный цикл.

```python
from pyengine.scene import Scene

class MyScene(Scene):
    def on_enter(self, **kwargs): ...
    def on_exit(self): ...
    def events(self, event): ...
    def update(self): ...
    def draw(self): ...
```

### Методы жизненного цикла
**on_enter(**kwargs)**
Вызывается при активации сцены. Здесь создаются фигуры, загружаются карты, устанавливаются начальные позиции.
- `**kwargs`: любые аргументы, переданные при переключении через `engine.set_scene('name', key=value)`.

**on_exit()**
Вызывается при выходе из сцены. Используется для очистки ресурсов, остановки музыки, сохранения прогресса.

### Методы каждого кадра
**events(event)**
Принимает каждое событие pygame. Обрабатывай здесь ввод: нажатия клавиш, клики мыши, движение курсора.
- `event` (pygame.event.Event): объект события pygame.

**update()**
Вызывается каждый кадр перед отрисовкой. Здесь логика: движение, физика, проверки коллизий, обновление состояний.

**draw()**
Вызывается каждый кадр. Здесь отрисовка: фигуры, текст, карты, UI.

---

## Figure

Универсальный графический объект. Одна фигура может быть прямоугольником, кругом, эллипсом, линией, полигоном или спрайтом.

```python
# Создание фигур
engine.create_figure('player', 'rect', Assets.BLUE, (100, 100, 32, 32))
engine.create_figure('enemy', 'circle', Assets.RED, (300, 200, 20))
engine.create_figure('coin', 'sprite', Assets.YELLOW, (500, 400, 'coin_img'))

# Управление
engine.figures['player'].set_pos(200, 150)
engine.figures['player'].move(10, -5)
engine.figures['player'].clamp_to_screen()
engine.figures['player'].play('idle_anim') # Запуск анимации
```

### Позиция и движение
**set_pos(x, y)**
Устанавливает новые координаты фигуры. Автоматически синхронизирует внутренние переменные и параметры отрисовки.
- `x` (float): новая позиция по X.
- `y` (float): новая позиция по Y.

**move(dx, dy)**
Смещает фигуру относительно текущей позиции.
- `dx` (float): смещение по X.
- `dy` (float): смещение по Y.

**clamp_to_screen()**
Ограничивает позицию фигуры границами экрана. Если фигура выходит за край, возвращает её обратно.

### Отрисовка
**draw(offset=(0.0, 0.0))**
Отрисовывает фигуру на экране. Обычно вызывается автоматически движком, но можно вызвать вручную.
- `offset` (tuple[float, float]): смещение камеры (ox, oy). По умолчанию (0, 0).

**set_image(image_name)**
Меняет изображение спрайта. Работает только для фигур с `shape='sprite'`.
- `image_name` (str): имя изображения, ранее загруженного через `engine.load_image`.

### Геометрия
**radius** (свойство)
Возвращает радиус фигуры. Работает только для круга. Для остальных форм возвращает 0.0.

**get_center()**
Возвращает координаты (x, y) центра фигуры. Для круга — центр, для прямоугольника — середина, для линии — середина отрезка.

**get_bounds()**
Возвращает ограничивающий прямоугольник в формате (x, y, ширина, высота). Работает для любой формы, включая полигон.

### Коллизии
**push_out(other)**
Выталкивает текущую фигуру наружу из другой фигуры, если они пересеклись. Работает для любых комбинаций форм.
- `other` (Figure): фигура, из которой нужно вытолкнуть.

### Анимации
**play(anim_name)**
Запускает указанную анимацию, сбрасывая текущий кадр и таймер. Движок автоматически обновляет кадры в главном цикле.
- `anim_name` (str): Имя анимации, зарегистрированной через `engine.add_animation`.

---

## Engine

Главный класс движка. Создаёт окно, управляет сценами, фигурами, вводом, коллизиями и отрисовкой.

```python
from pyengine.engine import PyEngine

engine = PyEngine(
    title='My Game',
    background=Assets.BLACK,
    width=800,
    height=600
)
engine.initialize(start_scene='menu')
engine.run()
```

### Конструктор
**__init__(title='Py-Engine', background=(50, 50, 50), width=800, height=600)**
Создаёт экземпляр движка. Окно пока не открывается — это делает `initialize`.
- `title` (str): заголовок окна.
- `background` (tuple): цвет фона в RGB.
- `width` (int): ширина окна в пикселях.
- `height` (int): высота окна в пикселях.

### Жизненный цикл
**initialize(start_scene=None)**
Инициализирует pygame, создаёт окно, настраивает таймер. После этого можно вызывать `run`.
- `start_scene` (str | None): имя сцены, на которую переключиться сразу после запуска.

**run()**
Запускает главный игровой цикл. Сам обрабатывает события, считает dt, очищает экран, вызывает update/draw сцен, обновляет камеру, отрисовывает очередь и ограничивает FPS до 60. Блокирующий метод — работает пока окно не закроют.

### Сцены
**add_scene(name, scene)**
Регистрирует сцену под именем. Без регистрации `set_scene` не сработает.
- `name` (str): уникальное имя сцены.
- `scene` (Scene): экземпляр класса, наследующего от Scene.

**add_scenes(scenes)**
Регистрирует сразу несколько сцен из словаря.
- `scenes` (dict[str, Scene]): словарь {имя: экземпляр_сцены}.

**set_scene(name, destroy=True, **kwargs)**
Планирует переключение на другую сцену. Переключение произойдёт безопасно в конце текущего кадра.
- `name` (str): имя целевой сцены.
- `destroy` (bool): если True, удаляет все фигуры старой сцены.
- `**kwargs`: аргументы, которые попадут в `on_enter` новой сцены.

### Фигуры
**create_figure(name, shape, color, params, width=0, auto_draw=False, use_camera=True)**
Создаёт фигуру и добавляет в движок.
- `name` (str): уникальное имя.
- `shape` (Literal): тип формы — `'rect'`, `'circle'`, `'ellipse'`, `'line'`, `'polygon'`, `'sprite'`.
- `color` (tuple): цвет RGB.
- `params` (tuple): параметры формы:
  - rect: `(x, y, ширина, высота)`
  - circle: `(x, y, радиус)`
  - ellipse: `(x, y, ширина, высота)`
  - line: `(x1, y1, x2, y2)`
  - polygon: `(список_точек,)`
  - sprite: `(x, y, имя_картинки)`
- `width` (int): толщина обводки. 0 = заливка.
- `auto_draw` (bool): если True, фигура сама добавляется в очередь отрисовки каждый кадр.
- `use_camera` (bool): если True, фигура двигается вместе с камерой. Для элементов UI (счёт, HP-бар) ставь `False`.

**draw_figure(name)**
Добавляет фигуру в очередь отрисовки на текущий кадр.
- `name` (str): имя фигуры.

**remove_figure(name)**
Удаляет фигуру из движка.
- `name` (str): имя фигуры.

**clear_figures()**
Удаляет все фигуры. Обычно не нужно вызывать вручную — `set_scene(destroy=True)` делает это сам.

### Текст и шрифты
**create_font(name, font='Arial', size=36)**
Создаёт шрифт и кэширует его.
- `name` (str): идентификатор для дальнейших вызовов.
- `font` (str): название системного шрифта.
- `size` (int): размер в пунктах.

**draw_text(font, text, x, y, color=(0, 0, 0), antialias=True, use_camera=False)**
Рисует текст на экране.
- `font` (str): имя шрифта, созданного через `create_font`.
- `text` (str): текст.
- `x, y` (int): координаты левого верхнего угла текста.
- `color` (tuple): цвет текста.
- `antialias` (bool): сглаживание.
- `use_camera` (bool): двигать ли текст с камерой. По умолчанию `False`, так как текст часто является UI.

**draw_text_on_figure(fig_name, font, text, color=(0, 0, 0), use_camera=False)**
Рисует текст по центру фигуры. Сам считает центр и размеры текста.
- `fig_name` (str): имя фигуры.
- `font` (str): имя шрифта.
- `text` (str): текст.
- `color` (tuple): цвет текста.
- `use_camera` (bool): двигать ли текст с камерой.

**draw_overlay(color=(0, 0, 0), alpha=180)**
Рисует полупрозрачный слой поверх всего. Годится для затемнения при паузе или открытия меню. Всегда игнорирует камеру.
- `color` (tuple): цвет слоя.
- `alpha` (int): прозрачность от 0 (невидимо) до 255 (глухо).

### Изображения
**load_image(name, path)**
Загружает картинку из файла.
- `name` (str): идентификатор.
- `path` (str): путь к файлу.

**scale_image(name, scale)**
Масштабирует картинку пропорционально.
- `name` (str): имя картинки.
- `scale` (float): коэффициент (0.5 = в два раза меньше, 2.0 = в два раза больше).

**resize_image(name, width, height)**
Растягивает/сжимает картинку до точных размеров. Пропорции не сохраняет.
- `name` (str): имя картинки.
- `width, height` (int): новые размеры в пикселях.

**flip_image(name, new_name, flip_x=False, flip_y=False)**
Зеркалит картинку и сохраняет копию под новым именем. Оригинал не трогает.
- `name` (str): имя исходной картинки.
- `new_name` (str): имя копии.
- `flip_x` (bool): отразить по горизонтали.
- `flip_y` (bool): отразить по вертикали.

**rotate_image(name, new_name, angle)**
Поворачивает картинку и сохраняет копию.
- `name` (str): имя исходной картинки.
- `new_name` (str): имя копии.
- `angle` (float): угол в градусах, против часовой стрелки.

### Ввод
**get_event(event, etype='keyDown', key=None)**
Проверяет конкретное событие в цикле обработки.
- `event` (pygame.event.Event): объект события.
- `etype` (EventLiteral): тип — `'quit'`, `'keyDown'`, `'keyUp'`, `'mouseButtonDown'`, `'mouseButtonUp'`, `'mouseMotion'`.
- `key` (KeyLiteral | None): конкретная клавиша. Если None, проверяется только тип.

**is_pressed(key)**
Возвращает True, пока клавиша или кнопка мыши удерживается. Это не событие, а состояние.
- `key` (KeyLiteral): имя клавиши (`'w'`, `'space'`, `'left'`) или кнопки мыши (`'leftMouseButton'`).

**is_mouse_over(name, cooldown=0.0)**
Возвращает True, если курсор над фигурой.
- `name` (str): имя фигуры.
- `cooldown` (float): минимальный интервал между True. Полезно чтобы не спамить наведением.

**is_clicked(name, cooldown=0.0, button='leftMouseButton')**
Возвращает True, если по фигуре кликнули мышью. Встроенный кулдаун не даёт сработать дважды.
- `name` (str): имя фигуры.
- `cooldown` (float): интервал в секундах.
- `button` (MouseButton): `'leftMouseButton'`, `'rightMouseButton'` или `'middleMouseButton'`.

### Коллизии
**check_collision(name1, name2, cooldown=0.5)**
Проверяют ли две фигуры друг друга. Встроенный кулдаун не даст вернуть True дважды за один "контакт". Поддерживает точную проверку круг-прямоугольник.
- `name1, name2` (str): имена фигур.
- `cooldown` (float): время в секундах до повторного True.

**can_move_to(name, new_x, new_y, obstacles)**
Симулирует перемещение и проверяет, не врежется ли фигура в препятствия. Если врежется — возвращает старые координаты.
- `name` (str): имя фигуры.
- `new_x, new_y` (float): куда хотим переместить.
- `obstacles` (list[str]): список имён фигур-препятствий.
- Возвращает: `(bool, float, float)` — (можно_ли, итоговый_x, итоговый_y).

**resolve_collisions(movers, walls)**
Проходит по списку movers и выталкивает каждого из каждого wall, если они пересекаются.
- `movers` (list[str]): имена подвижных фигур.
- `walls` (list[str]): имена статичных препятствий.

### Движение
**move(name, speed, dx=0.0, dy=0.0, target=None, map_name=None, obstacles=None, use_dt=True, grid_mode=False)**
Универсальный метод. Двигает фигуру, сам умножает скорость на dt, сам проверяет коллизии с тайлами карты и другими фигурами.
- `name` (str): имя фигуры.
- `speed` (float): скорость. Если `use_dt=True` — пикселей в секунду. Если `False` — пикселей за кадр.
- `dx, dy` (float): направление. Обычно -1, 0 или 1. В `grid_mode` игнорируются, если фигура уже движется к текущей цели.
- `target` (tuple[float, float] | None): координаты цели. Фигура плавно пойдёт к ним. Игнорируется в `grid_mode`.
- `map_name` (str | None): имя TileMap для коллизий с тайлами. Обязательно для `grid_mode`.
- `obstacles` (list[str] | None): имена фигур-препятствий.
- `use_dt` (bool): учитывать ли dt. False для UI-анимаций.
- `grid_mode` (bool): если True, включает пошаговое движение по сетке тайлов. Фигура будет останавливаться в центре каждого тайла и ждать нового ввода.

*Пример использования:*
```python
# Стандартное непрерывное движение (игрок бежит, врезается в стены)
dx, dy = 0, 0
if engine.is_pressed('left'): dx -= 1
if engine.is_pressed('right'): dx += 1
engine.move('player', speed=200, dx=dx, dy=dy, map_name='level')

# Пошаговое движение по тайлам (герой идет клетка за клеткой)
dx, dy = 0, 0
if engine.is_pressed('left'): dx = -1
if engine.is_pressed('right'): dx = 1
if engine.is_pressed('up'): dy = -1
if engine.is_pressed('down'): dy = 1
# Фигура плавно перейдет в центр соседнего тайла и остановится там
engine.move('hero', speed=150, dx=dx, dy=dy, map_name='level', grid_mode=True)
```

**move_towards(current_x, current_y, target_x, target_y, speed=0.1)**
Линейная интерполяция (lerp). Возвращает новую точку, которая ближе к цели на долю speed.
- `current_x, current_y` (float): текущие координаты.
- `target_x, target_y` (float): целевые координаты.
- `speed` (float): коэффициент от 0.0 до 1.0 (1.0 = телепорт, 0.05 = медленное скольжение).
- Возвращает: `(int, int)`.

**move_at_speed(current_x, current_y, target_x, target_y, speed=5.0)**
Сдвигает точку ровно на speed пикселей в сторону цели. Если до цели ближе чем speed — ставит точно на цель.
- `current_x, current_y` (float): текущие координаты.
- `target_x, target_y` (float): целевые координаты.
- `speed` (float): смещение в пикселях за один вызов.
- Возвращает: `(int, int)`.

### TileMap и камера
**add_tilemap(name, tilemap)**
Регистрирует карту в движке. После этого `move` сможет сам проверять коллизии с ней.
- `name` (str): имя карты.
- `tilemap` (TileMap): экземпляр TileMap.

**set_camera_target(figure_name)**
Камера автоматически следует за фигурой, держа её в центре экрана.
- `figure_name` (str): имя фигуры.

**set_camera_bounds(bounds_type, bounds_data)**
Ограничивает движение камеры, чтобы она не показывала пустоту за пределами мира.
- `bounds_type` (str): `'map'` (ограничить картой) или `'window'` (не уходить в отрицательные координаты).
- `bounds_data`: экземпляр `TileMap` (если `bounds_type='map'`).

**clamp_to_map(name, map_name)**
Не даёт фигуре вылезти за границы карты. Аналог `clamp_to_screen`, но для размеров карты.
- `name` (str): имя фигуры.
- `map_name` (str): имя карты.

**check_tile_collision(name, map_name, tile_id)**
Проверяет, стоит ли фигура на тайле с указанным ID.
- `name` (str): имя фигуры.
- `map_name` (str): имя карты.
- `tile_id` (int): ID тайла.

*Пример использования:*
```python
# Камера следит за игроком и не выходит за границы карты
engine.set_camera_target('player')
engine.set_camera_bounds('map', level)

# Игрок двигается с коллизиями
engine.move('player', speed=200, dx=dx, dy=dy, map_name='level')
engine.clamp_to_map('player', 'level')

# Проверка подбора монетки
if engine.check_tile_collision('player', 'level', tile_id=10):
    level.remove_tile(tx, ty, layer_index=1)
    score += 1
```

### Анимации
**add_animation(name, frames, fps=8.0)**
Регистрирует анимацию для использования фигурами.
- `name` (str): Уникальное имя анимации.
- `frames` (list[str]): Список имен изображений (кадров), загруженных через `load_image`.
- `fps` (float): Количество кадров в секунду.

*Пример использования:*
```python
engine.load_image('p1', 'assets/player_1.png')
engine.load_image('p2', 'assets/player_2.png')
engine.add_animation('player_idle', frames=['p1', 'p2'], fps=8)
engine.figures['hero'].play('player_idle') # Движок сам меняет кадры
```

### Утилиты
**check_cooldown(name, seconds)**
Таймер-защитка. Возвращает True, если прошло нужное время с последнего вызова. Иначе False.
- `name` (str): уникальный ID таймера.
- `seconds` (float): длительность в секундах.

*Пример использования:*
```python
# Выстрел не чаще раза в полсекунды
if engine.is_pressed('space') and engine.check_cooldown('shoot', seconds=0.5):
    print("Бах!")
```

**get_text_pos(font, text, align_x, align_y, offset_x=0, offset_y=0)**
Считает координаты для текста с учётом выравнивания и размера текста.
- `font` (str): имя шрифта (нужен для измерения текста).
- `text` (str): текст.
- `align_x` (AlignX): `'left'`, `'middle'` или `'right'`.
- `align_y` (AlignY): `'up'`, `'middle'` или `'down'`.
- `offset_x, offset_y` (int): дополнительный сдвиг.
- Возвращает: `(int, int)`.

**get_shape_pos(shape_w, shape_h, align_x, align_y, offset_x=0, offset_y=0)**
Считает координаты для фигуры с учётом её размеров и выравнивания.
- `shape_w, shape_h` (int): ширина и высота.
- `align_x` (AlignX): `'left'`, `'middle'` или `'right'`.
- `align_y` (AlignY): `'up'`, `'middle'` или `'down'`.
- `offset_x, offset_y` (int): дополнительный сдвиг.
- Возвращает: `(int, int)`.

*Пример использования:*
```python
# Кнопка по центру экрана
btn_pos = engine.get_shape_pos(200, 60, 'middle', 'middle')
engine.create_figure('btn', 'rect', Assets.GREEN, btn_pos)
```

---

## TileMap

Система тайловых карт с поддержкой нескольких слоёв. Тайлы — это статичная основа мира: пол, стены, декорации. Динамические объекты (игрок, враги, монетки) — это `Figure`.

```python
from pyengine.tilemap import Tile, TileSet, TileMap

# 1. Создаём набор тайлов
tileset = TileSet(tile_width=32, tile_height=32)
tileset.add_tile(Tile(1, Assets.GREEN, solid=False))  # Земля (не твёрдая)
tileset.add_tile(Tile(2, Assets.GRAY, solid=True))    # Стена (твёрдая)
tileset.add_tile(Tile(3, Assets.YELLOW))              # Монетка

# 2. Создаём карту и слои
level = TileMap(engine, tileset, width=30, height=20)
ground_layer = level.add_layer()   # Индекс 0
object_layer = level.add_layer()   # Индекс 1

# Указываем слой для коллизий
level.collision_layer_index = ground_layer

# 3. Быстрая загрузка из строк (прототипирование)
level.load_from_lines([
    "######################",
    "#....................#",
    "#..22222.............#",
    "######################",
], legend={'#': 2, '.': 1, '2': 1}, layer_index=ground_layer)

# 4. Конвертация координат
px, py = level.cell_to_pixel(5, 2)      # Вернёт (160, 64)
col, row = level.pixel_to_cell(170, 70) # Вернёт (5, 2)

engine.add_tilemap('level', level)
```

### Tile
Один тип тайла.
**__init__(tile_id, color=None, image_name=None, solid=False, exceptions=None)**
- `tile_id` (int): уникальный ID тайла.
- `color` (tuple | None): цвет тайла (используется, если нет `image_name`).
- `image_name` (str | None): имя изображения из `engine.images` (приоритетнее цвета).
- `solid` (bool): если True, фигуры не смогут проходить сквозь этот тайл.
- `exceptions` (list[str] | None): список названий фигур, которые могут проходить сквозь этот тайл даже если `solid=True`.

### TileSet
Набор тайлов с общим размером.
**__init__(tile_width=32, tile_height=32)**
- `tile_width` (int): ширина одного тайла в пикселях.
- `tile_height` (int): высота одного тайла в пикселях.

**add_tile(tile)**
Добавляет тайл в набор. Если тайл с таким ID уже существует, он будет перезаписан.
- `tile` (Tile): экземпляр Tile.

### TileLayer
Один слой тайлов. Карта может содержать несколько слоёв для разделения пола, объектов, переднего плана.
**__init__(width, height, default_tile=0)**
- `width` (int): ширина слоя в тайлах.
- `height` (int): высота слоя в тайлах.
- `default_tile` (int): ID тайла по умолчанию (используется при создании и удалении).

**set_tile(x, y, tile_id)**
Устанавливает тайл с указанным ID в позицию (x, y). Если координаты выходят за границы слоя, метод ничего не делает.
- `x, y` (int): позиция в тайлах.
- `tile_id` (int): ID тайла.

**get_tile(x, y)**
Возвращает ID тайла в позиции (x, y). Если координаты выходят за границы слоя, возвращает 0.
- `x, y` (int): позиция в тайлах.

**remove_tile(x, y)**
Удаляет тайл из позиции (x, y), делая ячейку пустой (ID=0). Пустые тайлы не отрисовываются, что позволяет видеть слои под ними. Если координаты выходят за границы слоя, метод ничего не делает.
- `x, y` (int): позиция в тайлах.

### TileMap
Двумерная карта тайлов с поддержкой нескольких слоёв.
**__init__(engine, tileset, width, height)**
- `engine` (PyEngine): экземпляр PyEngine.
- `tileset` (TileSet): набор тайлов.
- `width` (int): ширина карты в тайлах.
- `height` (int): высота карты в тайлах.

**add_layer(default_tile=0)**
Добавляет новый слой тайлов в карту. Возвращает индекс созданного слоя (начинается с 0).
- `default_tile` (int): ID тайла по умолчанию для этого слоя.

**set_tile(x, y, tile_id, layer_index=0)**
Устанавливает тайл с указанным ID в позицию (x, y) на заданном слое. Если `layer_index` не указан, используется слой 0.
- `x, y` (int): позиция в тайлах.
- `tile_id` (int): ID тайла.
- `layer_index` (int): индекс слоя.

**get_tile(x, y, layer_index=0)**
Возвращает ID тайла в позиции (x, y) на заданном слое. Если `layer_index` не указан, используется слой 0. Если координаты или индекс слоя некорректны, возвращает 0.
- `x, y` (int): позиция в тайлах.
- `layer_index` (int): индекс слоя.

**remove_tile(x, y, layer_index=0)**
Удаляет тайл из позиции (x, y) на заданном слое, делая ячейку пустой. Пустые тайлы не отрисовываются, позволяя видеть нижние слои. Если `layer_index` не указан, используется слой 0.
- `x, y` (int): позиция в тайлах.
- `layer_index` (int): индекс слоя.

**is_solid(x, y, figure_name=None)**
Проверяет, является ли тайл в позиции (x, y) непроходимым. Проверка выполняется только на слое `collision_layer_index`. Если `figure_name` указан и находится в списке `exceptions` тайла, возвращается False.
- `x, y` (int): позиция в тайлах.
- `figure_name` (str | None): имя фигуры для проверки исключений.

**draw()**
Отрисовывает все слои карты на экран с учётом смещения камеры. Слои рисуются по порядку их добавления (от 0 до последнего). Оптимизировано: рисуются только видимые тайлы.

**load_from_lines(lines, legend, layer_index=0)**
Загружает карту из списка строк (текстовый уровень).
- `lines` (list[str]): Список строк, где каждый символ представляет тайл.
- `legend` (dict[str, int]): Словарь соответствия символа и ID тайла (например, `{'#': 1, '.': 0}`).
- `layer_index` (int): Индекс слоя для записи данных.

**cell_to_pixel(col, row)**
Преобразует координаты ячейки (col, row) в пиксельные координаты (x, y).
- `col, row` (int): координаты ячейки.
- Возвращает: `(int, int)`.

**pixel_to_cell(x, y)**
Преобразует пиксельные координаты (x, y) в координаты ячейки (col, row).
- `x, y` (float): пиксельные координаты.
- Возвращает: `(int, int)`.

---

## Мини-игры

Четыре примера, показывающие разные комбинации функционала.

### Игра 1. Без сцен, без TileMap
Простая игра: убегай от красного круга.

```python
from pyengine.engine import PyEngine
from pyengine.assets import Assets

engine = PyEngine('Убеги!', Assets.BLACK, 640, 480)
engine.initialize()

engine.create_figure('player', 'rect', Assets.BLUE, (300, 220, 24, 24))
engine.create_figure('enemy', 'circle', Assets.RED, (50, 50, 16))
engine.create_font('f', Assets.FONT_ARIAL, 20)
alive = True

def update():
    global alive
    if not alive: return
    dx = dy = 0
    if engine.is_pressed('left'): dx -= 1
    if engine.is_pressed('right'): dx += 1
    if engine.is_pressed('up'): dy -= 1
    if engine.is_pressed('down'): dy += 1
    engine.move('player', speed=250, dx=dx, dy=dy)
    engine.figures['player'].clamp_to_screen()
    px, py = engine.figures['player'].get_center()
    engine.move('enemy', speed=120, target=(px, py))
    if engine.check_collision('player', 'enemy', cooldown=999):
        alive = False

def draw():
    engine.draw_figure('player')
    engine.draw_figure('enemy')
    if not alive:
        engine.draw_overlay(Assets.BLACK, 180)
        engine.draw_text('f', 'Game Over', 250, 220, Assets.RED, use_camera=False)

engine.update = update
engine.draw = draw
engine.run()
```

### Игра 2. Без сцен, с TileMap
Собирай монетки в лабиринте. Камера следит за игроком и ограничена границами карты.

```python
from pyengine.engine import PyEngine
from pyengine.assets import Assets
from pyengine.tilemap import Tile, TileSet, TileMap

engine = PyEngine('Монетки', Assets.BLACK, 480, 320)
engine.initialize()

ts = TileSet(32, 32)
ts.add_tile(Tile(1, Assets.DARK_GRAY, solid=True))
ts.add_tile(Tile(2, Assets.YELLOW))

level = TileMap(engine, ts, 30, 20)
ground = level.add_layer()
objects = level.add_layer()
level.collision_layer_index = ground

level.load_from_lines([
    "##############################",
    "#............................#",
    "#...####...........####......#",
    "#...#................#....2..#",
    "##############################",
], legend={'#': 1, '.': 0, '2': 2}, layer_index=ground)

engine.add_tilemap('level', level)
engine.create_figure('p', 'rect', Assets.CYAN, (64, 64, 24, 24))
engine.set_camera_target('p')
engine.set_camera_bounds('map', level) # Камера не покажет пустоту за краями
engine.create_font('f', Assets.FONT_ARIAL, 18)
score = 0

def update():
    global score
    dx = dy = 0
    if engine.is_pressed('left'): dx -= 1
    if engine.is_pressed('right'): dx += 1
    if engine.is_pressed('up'): dy -= 1
    if engine.is_pressed('down'): dy += 1
    
    engine.move('p', speed=180, dx=dx, dy=dy, map_name='level')
    
    # Простая проверка: если коснулись тайла 2, меняем его на 0 (пустоту)
    if engine.check_tile_collision('p', 'level', 2):
        cx, cy = engine.figures['p'].get_center()
        tx, ty = level.pixel_to_cell(cx, cy)
        level.remove_tile(tx, ty, layer_index=objects)
        score += 1

def draw():
    level.draw()
    engine.draw_figure('p')
    engine.draw_text('f', f'Монетки: {score}', 10, 10, Assets.WHITE, use_camera=False)

engine.update = update
engine.draw = draw
engine.run()
```

### Игра 3. Со сценами, без TileMap
Три сцены: меню, арена, game over.

```python
from pyengine.engine import PyEngine
from pyengine.scene import Scene
from pyengine.assets import Assets

engine = PyEngine('Арена', Assets.BLACK, 480, 320)

class Menu(Scene):
    def on_enter(self, **kw):
        self.engine.create_figure('btn', 'rect', Assets.GREEN,
            self.engine.get_shape_pos(180, 50, 'middle', 'middle'))
        self.engine.create_font('f', Assets.FONT_ARIAL, 24)
    def events(self, event):
        if self.engine.get_event(event, 'mouseButtonDown', 'leftMouseButton'):
            if self.engine.is_clicked('btn', cooldown=0.3):
                self.engine.set_scene('arena')
    def update(self): pass
    def draw(self):
        self.engine.draw_figure('btn')
        self.engine.draw_text_on_figure('btn', 'f', 'Играть', Assets.WHITE, use_camera=False)

class Arena(Scene):
    def on_enter(self, **kw):
        self.engine.create_figure('p', 'circle', Assets.BLUE, (100, 160, 18))
        self.engine.create_figure('e', 'circle', Assets.RED, (380, 160, 18))
        self.engine.create_font('f', Assets.FONT_ARIAL, 16)
    def events(self, event): pass
    def update(self):
        px, py = self.engine.figures['p'].get_center()
        self.engine.move('e', speed=100, target=(px, py))
        dx = dy = 0
        if self.engine.is_pressed('left'): dx -= 1
        if self.engine.is_pressed('right'): dx += 1
        if self.engine.is_pressed('up'): dy -= 1
        if self.engine.is_pressed('down'): dy += 1
        self.engine.move('p', speed=200, dx=dx, dy=dy)
        self.engine.figures['p'].clamp_to_screen()
        if self.engine.check_collision('p', 'e', cooldown=999):
            self.engine.set_scene('dead')
    def draw(self):
        self.engine.draw_figure('p')
        self.engine.draw_figure('e')

class Dead(Scene):
    def on_enter(self, **kw):
        self.engine.create_font('f', Assets.FONT_ARIAL, 36)
    def events(self, event): pass
    def update(self):
        if self.engine.is_pressed('space'):
            self.engine.set_scene('menu')
    def draw(self):
        self.engine.draw_text('f', 'Ты умер. Пробел = меню', 80, 140, Assets.RED, use_camera=False)

engine.add_scenes({'menu': Menu(engine), 'arena': Arena(engine), 'dead': Dead(engine)})
engine.initialize(start_scene='menu')
engine.run()
```

### Игра 4. Со сценами, с TileMap и пошаговым движением
Меню → подземелье → победа. Герой двигается строго по клеткам.

```python
from pyengine.engine import PyEngine
from pyengine.scene import Scene
from pyengine.assets import Assets
from pyengine.tilemap import Tile, TileSet, TileMap

engine = PyEngine('Подземелье', Assets.BLACK, 480, 320)

class Menu(Scene):
    def on_enter(self, **kw):
        self.engine.create_figure('btn', 'rect', Assets.ORANGE,
            self.engine.get_shape_pos(200, 50, 'middle', 'middle'))
        self.engine.create_font('f', Assets.FONT_ARIAL, 22)
    def events(self, event):
        if self.engine.get_event(event, 'mouseButtonDown', 'leftMouseButton'):
            if self.engine.is_clicked('btn', 0.3):
                self.engine.set_scene('dungeon')
    def update(self): pass
    def draw(self):
        self.engine.draw_figure('btn')
        self.engine.draw_text_on_figure('btn', 'f', 'Войти в подземелье', Assets.WHITE, use_camera=False)

class Dungeon(Scene):
    def on_enter(self, **kw):
        ts = TileSet(32, 32)
        ts.add_tile(Tile(1, Assets.GRAY, solid=True))
        ts.add_tile(Tile(2, Assets.GREEN))
        
        self.level = TileMap(self.engine, ts, 15, 10)
        ground = self.level.add_layer()
        self.level.collision_layer_index = ground
        
        self.level.load_from_lines([
            "###############",
            "#.............#",
            "#.#####.......#",
            "#.#...#.......#",
            "#.#.2.#.......#",
            "#.#...#.......#",
            "#.#####.......#",
            "#.............#",
            "#.............#",
            "###############",
        ], legend={'#': 1, '.': 0, '2': 2}, layer_index=ground)
        
        self.engine.add_tilemap('dungeon', self.level)
        self.engine.create_figure('p', 'rect', Assets.CYAN, (48, 48, 24, 24))
        self.engine.set_camera_target('p')
        self.engine.set_camera_bounds('map', self.level)
        self.engine.create_font('f', Assets.FONT_ARIAL, 14)
        
    def events(self, event): pass
    
    def update(self):
        dx = dy = 0
        if self.engine.is_pressed('left'): dx = -1
        if self.engine.is_pressed('right'): dx = 1
        if self.engine.is_pressed('up'): dy = -1
        if self.engine.is_pressed('down'): dy = 1
        
        # grid_mode=True: герой сделает один шаг и остановится в центре тайла
        self.engine.move('p', speed=200, dx=dx, dy=dy, map_name='dungeon', grid_mode=True)
        
        if self.engine.check_tile_collision('p', 'dungeon', 2):
            self.engine.set_scene('win')
            
    def draw(self):
        self.level.draw()
        self.engine.draw_figure('p')
        self.engine.draw_text('f', 'Найди зелёный выход (пошагово!)', 10, 10, Assets.WHITE, use_camera=False)

class Win(Scene):
    def on_enter(self, **kw):
        self.engine.create_figure('btn', 'rect', Assets.PURPLE,
            self.engine.get_shape_pos(180, 50, 'middle', 'middle'))
        self.engine.create_font('f', Assets.FONT_ARIAL, 28)
    def events(self, event):
        if self.engine.get_event(event, 'mouseButtonDown', 'leftMouseButton'):
            if self.engine.is_clicked('btn', 0.3):
                self.engine.set_scene('menu')
    def update(self): pass
    def draw(self):
        self.engine.draw_text('f', 'Ты прошёл!', 170, 100, Assets.GREEN, use_camera=False)
        self.engine.draw_figure('btn')
        self.engine.draw_text_on_figure('btn', 'f', 'Заново', Assets.WHITE, use_camera=False)

engine.add_scenes({
    'menu': Menu(engine),
    'dungeon': Dungeon(engine),
    'win': Win(engine)
})
engine.initialize(start_scene='menu')
engine.run()
```

---

## Философия PyEngine

PyEngine не пытается стать заменой pygame или навязать сложную архитектуру. Его цель — убрать рутину. 

Ты больше не будешь писать одни и те же 20 строк кода для проверки клика по кнопке. Ты не будешь каждый раз изобретать велосипед для камеры, которая следует за игроком. Ты не будешь тратить вечер на отладку коллизий между кругом и прямоугольником.

Библиотека дает готовые строительные блоки. Если нужно что-то специфичное — бери `pygame` и делай как хочешь. Но для 90% задач в 2D-играх у PyEngine уже есть решение в одну строку.

**Для кого это:**
* Для тех, кто хочет прототипировать идеи быстро.
* Для новичков, которые хотят понять логику игр, а не тонуть в boilerplate-коде.
* Для опытных разработчиков, которым просто лень каждый раз писать одно и то же.

Удачи в разработке.