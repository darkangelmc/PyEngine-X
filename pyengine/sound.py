import pygame


# ――――――――――――――――――――――――― sound mixin ―――――――――――――――――――――――――


class Sound:
    def __init__(self):
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.playing_sounds: dict[str, pygame.mixer.Sound] = {}

    # ――――――――――――――――――――――――― sfx ―――――――――――――――――――――――――

    def load_sound(self, name: str, path: str):
        """
        Загружает звуковой эффект (sfx) из файла и сохраняет его в памяти под указанным именем.
        """
        self.sounds[name] = pygame.mixer.Sound(path)

    def play_sound(self, name: str, loop: bool = False):
        """
        Воспроизводит загруженный звуковой эффект. Если loop=True, зацикливает его воспроизведение.
        """
        if name not in self.sounds:
            print(f"sound '{name}' not found")
            return
        sound = self.sounds[name]
        sound.play(loops=-1 if loop else 0)
        self.playing_sounds[name] = sound

    def stop_sound(self, name: str):
        """
        Останавливает воспроизведение указанного звукового эффекта.
        """
        if name in self.playing_sounds:
            self.playing_sounds[name].stop()
            del self.playing_sounds[name]

    def set_sound_volume(self, name: str, volume: float):
        """
        Устанавливает громкость для конкретного звукового эффекта (значение от 0.0 до 1.0).
        """
        if name in self.sounds:
            self.sounds[name].set_volume(volume)

    # ――――――――――――――――――――――――― music ―――――――――――――――――――――――――

    def load_music(self, path: str):
        """
        Загружает фоновую музыкальную композицию из файла (поддерживается только один трек одновременно).
        """
        pygame.mixer.music.load(path)

    def play_music(self, loop: bool = False):
        """
        Начинает воспроизведение загруженной фоновой музыки. Если loop=True, зацикливает её.
        """
        pygame.mixer.music.play(loops=-1 if loop else 0)

    def stop_music(self):
        """
        Полностью останавливает воспроизведение фоновой музыки.
        """
        pygame.mixer.music.stop()

    def pause_music(self):
        """
        Приостанавливает воспроизведение музыки (можно продолжить позже через resume_music).
        """
        pygame.mixer.music.pause()

    def resume_music(self):
        """
        Продолжает воспроизведение музыки с момента паузы.
        """
        pygame.mixer.music.unpause()

    def set_music_volume(self, volume: float):
        """
        Устанавливает громкость фоновой музыки (значение от 0.0 до 1.0).
        """
        pygame.mixer.music.set_volume(volume)

    def fade_in_music(self, seconds: float = 2.0, loop: bool = False):
        """
        Запускает воспроизведение музыки с плавным нарастанием громкости за указанное время (в секундах).
        """
        pygame.mixer.music.play(loops=-1 if loop else 0, fade_ms=int(seconds * 1000))

    def fade_out_music(self, seconds: float = 2.0):
        """
        Плавно затухает и останавливает музыку за указанное время (в секундах).
        """
        pygame.mixer.music.fadeout(int(seconds * 1000))

    def set_all_volume(self, volume: float):
        """
        Устанавливает заданную громкость одновременно для всех загруженных звуков и фоновой музыки.
        """
        for s in self.sounds.values():
            s.set_volume(volume)
        pygame.mixer.music.set_volume(volume)