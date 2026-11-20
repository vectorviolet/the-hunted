import pygame


class AudioManager:
    def __init__(self) -> None:
        self._menu_song = pygame.mixer.Sound("assets/sounds/menu_theme.ogg")
        self._game_song = pygame.mixer.Sound("assets/sounds/chase_theme.ogg")

    def play_menu(self) -> None:
        self._menu_song.play(-1)

    def stop_menu(self) -> None:
        self._menu_song.stop()

    def play_game(self) -> None:
        self._game_song.play(-1)

    def stop_game(self) -> None:
        self._game_song.stop()

    @staticmethod
    def pause_all() -> None:
        pygame.mixer.pause()
