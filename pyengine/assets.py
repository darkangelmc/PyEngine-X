import random


# ――――――――――――――――――――――――― assets ―――――――――――――――――――――――――


class Assets:

    # ――――――――――――――――――――――――― colors ―――――――――――――――――――――――――

    WHITE     = (255, 255, 255)
    BLACK     = (0,   0,   0  )
    RED       = (255, 0,   0  )
    GREEN     = (0,   255, 0  )
    BLUE      = (0,   0,   255)
    YELLOW    = (255, 255, 0  )
    CYAN      = (0,   255, 255)
    MAGENTA   = (255, 0,   255)
    GRAY      = (128, 128, 128)
    DARK_GRAY = (64,  64,  64 )
    ORANGE    = (255, 165, 0  )
    PURPLE    = (128, 0,   128)

    COLORS = {
        'white': WHITE, 'black': BLACK, 'red': RED, 'green': GREEN,
        'blue': BLUE, 'yellow': YELLOW, 'cyan': CYAN, 'magenta': MAGENTA,
        'gray': GRAY, 'dark_gray': DARK_GRAY, 'orange': ORANGE, 'purple': PURPLE,
    }

    # ――――――――――――――――――――――――― fonts ―――――――――――――――――――――――――

    FONT_ARIAL   = 'Arial'
    FONT_COMIC   = 'Comic Sans MS'
    FONT_TIMES   = 'Times New Roman'
    FONT_COURIER = 'Courier New'

    # ――――――――――――――――――――――――― utils ―――――――――――――――――――――――――

    @staticmethod
    def get_color(name: str) -> tuple:
        """
        Возвращает кортеж цвета (RGB) по его строковому имени (например, 'red'). Если цвет не найден, возвращает черный.
        """
        return Assets.COLORS.get(name.lower(), Assets.BLACK)

    @staticmethod
    def random_color() -> tuple:
        """
        Генерирует и возвращает случайный цвет в формате RGB.
        """
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    @staticmethod
    def darken(color: tuple, factor: float = 0.7) -> tuple:
        """
        Затемняет указанный цвет, умножая его RGB-компоненты на заданный коэффициент (по умолчанию 0.7).
        """
        return tuple(int(c * factor) for c in color)

    @staticmethod
    def lighten(color: tuple, factor: float = 1.3) -> tuple:
        """
        Осветляет указанный цвет, умножая его RGB-компоненты на заданный коэффициент (по умолчанию 1.3).
        """
        return tuple(min(255, int(c * factor)) for c in color)