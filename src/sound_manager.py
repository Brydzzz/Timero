import pygame
from pathlib import Path


class SoundManager:
    def __init__(self, audio_assets_path: str):
        pygame.mixer.init()
        self.assets_path = Path(audio_assets_path)

    def play_sound(self, filename: str):
        audio_path = self.assets_path / filename
        pygame.mixer.Sound(str(audio_path)).play()

    def stop_all_sounds(self):
        pygame.mixer.stop()

    def quit(self):
        pygame.mixer.quit()
