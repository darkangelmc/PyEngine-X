from __future__ import annotations
import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .engine import PyEngine

# ――――――――――――――――――――――――― tile ―――――――――――――――――――――――――
class Tile:
    """Один тип тайла (плитки)"""
    def __init__(
        self, 
        tile_id: int, 
        color: tuple | None = None, 
        image_name: str | None = None,
        solid: bool = False,
        exceptions: list[str] | None = None
    ):
        """
        :tile_id: уникальный ID тайла
        :color: цвет тайла (используется, если нет image_name)
        :image_name: имя изображения из engine.images (приоритетнее цвета)
        :solid: если True, фигуры не смогут проходить сквозь этот тайл
        :exceptions: список названий фигур, которые МОГУТ проходить сквозь этот тайл
        """
        self.id = tile_id
        self.color = color if color else (100, 100, 100)
        self.image_name = image_name
        self.solid = solid
        self.exceptions = exceptions if exceptions else []

# ――――――――――――――――――――――――― tileset ―――――――――――――――――――――――――
class TileSet:
    """Набор тайлов с общим размером"""
    def __init__(self, tile_width: int = 32, tile_height: int = 32):
        """
        :tile_width: ширина одного тайла в пикселях
        :tile_height: высота одного тайла в пикселях
        """
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tiles: dict[int, Tile] = {}

    def add_tile(self, tile: Tile):
        """Добавляет тайл в набор. Если тайл с таким ID уже существует, он будет перезаписан."""
        self.tiles[tile.id] = tile

# ――――――――――――――――――――――――― tilelayer ―――――――――――――――――――――――――
class TileLayer:
    """Один слой тайлов"""
    def __init__(self, width: int, height: int, default_tile: int = 0):
        """
        :width: ширина слоя в тайлах
        :height: высота слоя в тайлах
        :default_tile: ID тайла по умолчанию (используется при создании и удалении)
        """
        self.width = width
        self.height = height
        self.default_tile = default_tile
        self.data: list[list[int]] = [[default_tile for _ in range(width)] for _ in range(height)]

    def set_tile(self, x: int, y: int, tile_id: int):
        """
        Устанавливает тайл с указанным ID в позицию (x, y).
        Если координаты выходят за границы слоя, метод ничего не делает.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y][x] = tile_id

    def get_tile(self, x: int, y: int) -> int:
        """
        Возвращает ID тайла в позиции (x, y).
        Если координаты выходят за границы слоя, возвращает 0.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.data[y][x]
        return 0
    
    def remove_tile(self, x: int, y: int):
        """
        Удаляет тайл из позиции (x, y), делая ячейку пустой (ID=0).
        Пустые тайлы не отрисовываются, что позволяет видеть слои под ними.
        Если координаты выходят за границы слоя, метод ничего не делает.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.data[y][x] = self.default_tile

# ――――――――――――――――――――――――― tilemap ―――――――――――――――――――――――――
class TileMap:
    """Двумерная карта тайлов с поддержкой нескольких слоев"""
    def __init__(self, engine: PyEngine, tileset: TileSet, width: int, height: int):
        """
        :engine: экземпляр PyEngine
        :tileset: набор тайлов (TileSet)
        :width: ширина карты в тайлах
        :height: высота карты в тайлах
        """
        self.engine = engine
        self.tileset = tileset
        self.width = width
        self.height = height
        
        self.layers: list[TileLayer] = []
        self.collision_layer_index: int = 0
        
        # Кеш отрендеренных слоев для ускорения отрисовки
        self._layer_cache: dict[int, pygame.Surface | None] = {}

    def add_layer(self, default_tile: int = 0) -> int:
        """
        Добавляет новый слой тайлов в карту.
        Возвращает индекс созданного слоя (начинается с 0).
        """
        layer = TileLayer(self.width, self.height, default_tile)
        self.layers.append(layer)
        return len(self.layers) - 1

    def set_tile(self, x: int, y: int, tile_id: int, layer_index: int = 0):
        """
        Устанавливает тайл с указанным ID в позицию (x, y) на заданном слое.
        Если layer_index не указан, используется слой 0.
        """
        if 0 <= layer_index < len(self.layers):
            self.layers[layer_index].set_tile(x, y, tile_id)
            self._layer_cache[layer_index] = None  # Сбрасываем кеш

    def get_tile(self, x: int, y: int, layer_index: int = 0) -> int:
        """
        Возвращает ID тайла в позиции (x, y) на заданном слое.
        Если layer_index не указан, используется слой 0.
        Если координаты или индекс слоя некорректны, возвращает 0.
        """
        if 0 <= layer_index < len(self.layers):
            return self.layers[layer_index].get_tile(x, y)
        return 0

    def remove_tile(self, x: int, y: int, layer_index: int = 0):
        """
        Удаляет тайл из позиции (x, y) на заданном слое, делая ячейку пустой.
        Пустые тайлы не отрисовываются, позволяя видеть нижние слои.
        Если layer_index не указан, используется слой 0.
        """
        if 0 <= layer_index < len(self.layers):
            self.layers[layer_index].remove_tile(x, y)
            self._layer_cache[layer_index] = None  # Сбрасываем кеш

    def is_solid(self, x: int, y: int, figure_name: str | None = None) -> bool:
        """
        Проверяет, является ли тайл в позиции (x, y) непроходимым.
        Проверка выполняется только на слое collision_layer_index.
        Если figure_name указан и находится в списке exceptions тайла, возвращается False.
        """
        if self.collision_layer_index >= len(self.layers):
            return False
        tile_id = self.get_tile(x, y, self.collision_layer_index)
        tile = self.tileset.tiles.get(tile_id)
        if tile is None or not tile.solid:
            return False
        if figure_name and figure_name in tile.exceptions:
            return False
        return True

    def _render_layer(self, layer_index: int) -> pygame.Surface:
        """Рендерит весь слой в отдельную Surface (используется для кеширования)."""
        layer = self.layers[layer_index]
        surf = pygame.Surface(
            (self.width * self.tileset.tile_width, self.height * self.tileset.tile_height), 
            pygame.SRCALPHA
        )
        tw, th = self.tileset.tile_width, self.tileset.tile_height
        
        for y in range(self.height):
            for x in range(self.width):
                tile_id = layer.data[y][x]
                if tile_id == 0: continue
                
                tile = self.tileset.tiles.get(tile_id)
                if not tile: continue
                
                px, py = x * tw, y * th
                if tile.image_name and tile.image_name in self.engine.images:
                    surf.blit(self.engine.images[tile.image_name], (px, py))
                else:
                    pygame.draw.rect(surf, tile.color, (px, py, tw, th))
        return surf

    def draw(self):
        """
        Отрисовывает все слои карты на экран с учётом смещения камеры.
        Слои рисуются по порядку их добавления (от 0 до последнего).
        Оптимизировано: использует кеш, если слой не менялся.
        """
        ox, oy = self.engine.camera_offset
        
        for i in range(len(self.layers)):
            if self._layer_cache.get(i) is None:
                self._layer_cache[i] = self._render_layer(i)
            
            self.engine.screen.blit(self._layer_cache[i], (int(ox), int(oy)))

    # ――――――――――――――――――――――――― utils ―――――――――――――――――――――――――
    def cell_to_pixel(self, col: int, row: int) -> tuple[int, int]:
        """
        Преобразует координаты ячейки (col, row) в пиксельные координаты (x, y).
        """
        return (col * self.tileset.tile_width, row * self.tileset.tile_height)

    def pixel_to_cell(self, x: float, y: float) -> tuple[int, int]:
        """
        Преобразует пиксельные координаты (x, y) в координаты ячейки (col, row).
        Использует целочисленное деление, корректно работает с отрицательными координатами.
        """
        return (int(x // self.tileset.tile_width), int(y // self.tileset.tile_height))

    def load_from_lines(self, lines: list[str], legend: dict[str, int], layer_index: int = 0):
        """
        Загружает карту из списка строк (текстовый уровень).
        - lines (list[str]): Список строк, где каждый символ представляет тайл.
        - legend (dict[str, int]): Словарь соответствия символа и ID тайла (например, {'#': 1, '.': 0}).
        - layer_index (int): Индекс слоя для записи данных.
        """
        for row, line in enumerate(lines):
            for col, char in enumerate(line):
                if char in legend:
                    self.set_tile(col, row, legend[char], layer_index)